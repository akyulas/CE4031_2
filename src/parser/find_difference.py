import queue
import networkx as nx
from .node_utils import set_output_name, Node
from networkx.algorithms.similarity import optimize_edit_paths
import re
import sys

def node_match(node_1, node_2):
    return node_1['custom_object'] == node_2['custom_object']

def node_substitude_cost(node_1, node_2):
    node_1_object = node_1['custom_object']
    node_2_object = node_2['custom_object']
    if node_1_object == node_2_object:
        return 0
    elif node_1_object.node_type == node_2_object.node_type:
        return 0.5
    return 9223372036854775807
    


def get_graph_from_query_plan(query_plan):
    G = nx.Graph()
    q = queue.Queue()
    q_node = queue.Queue()
    q.put(query_plan)
    q_node.put(None)
    current_index = 0

    while not q.empty():
        current_plan = q.get()
        parent_index = q_node.get()

        node_type = relation_name = schema = alias = group_key = sort_key = join_type = index_name = hash_cond = table_filter \
            = index_cond = merge_cond = recheck_cond = join_filter = subplan_name = plan_rows = output_name = None
        
        node_type = current_plan['Node Type']
        
        if 'Relation Name' in current_plan:
            relation_name = current_plan['Relation Name']
        if 'Schema' in current_plan:
            schema = current_plan['Schema']
        if 'Alias' in current_plan:
            alias = current_plan['Alias']
        if 'Group Key' in current_plan:
            group_key = current_plan['Group Key']
        if 'Sort Key' in current_plan:
            sort_key = current_plan['Sort Key']
        if 'Join Type' in current_plan:
            join_type = current_plan['Join Type']
        if 'Index Name' in current_plan:
            index_name = current_plan['Index Name']
        if 'Hash Cond' in current_plan:
            hash_cond = current_plan['Hash Cond']
        if 'Filter' in current_plan:
            table_filter = current_plan['Filter']
        if 'Index Cond' in current_plan:
            index_cond = current_plan['Index Cond']
        if 'Merge Cond' in current_plan:
            merge_cond = current_plan['Merge Cond']
        if 'Recheck Cond' in current_plan:
            recheck_cond = current_plan['Recheck Cond']
        if 'Join Filter' in current_plan:
            join_filter = current_plan['Join Filter']
        if 'Subplan Name' in current_plan:
            if "returns" in current_plan['Subplan Name']:
                name = current_plan['Subplan Name']
                subplan_name = name[name.index("$"):-1]
            else:
                subplan_name = current_plan['Subplan Name']
        if "Limit" == node_type:
            plan_rows = current_plan['Plan Rows']
           
        if "Scan" in node_type:
            if "Index" in node_type:
                if relation_name:
                    output_name = set_output_name(relation_name + " with index " + index_name)
            elif "Subquery" in node_type:
                output_name = set_output_name(alias)
            else:
                output_name = set_output_name(relation_name)
        
        current_node = Node(current_plan['Node Type'], relation_name, schema, alias, group_key, sort_key, join_type,
                            index_name, hash_cond, table_filter, index_cond, merge_cond, recheck_cond, join_filter,
                            subplan_name, plan_rows, output_name)
        
        G.add_node(current_index, custom_object=current_node)
        
        if parent_index is not None:
            G.add_edge(parent_index, current_index)

        if 'Plans' in current_plan:
            for item in current_plan['Plans']:
                # push child plans into queue
                q.put(item)
                # push parent for each child into queue
                q_node.put(current_index)
        current_index += 1
    
    return G
    
def find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan):
    result = re.search('select(.*)from', old_query)
    old_query_projections = result.group(1)
    old_query_projections = old_query_projections.replace("(", "")
    old_query_projections = old_query_projections.replace(")", "")
    old_query_projections_set = set([x.strip() for x in old_query_projections.split(',')])
    result = re.search('select(.*)from', new_query)
    new_query_projections = result.group(1)
    new_query_projections = new_query_projections.replace("(", "")
    new_query_projections = new_query_projections.replace(")", "")
    new_query_projections_set = set([x.strip() for x in new_query_projections.split(',')])        
    G1 = get_graph_from_query_plan(old_query_plan)
    G2 = get_graph_from_query_plan(new_query_plan)
    generator = optimize_edit_paths(G1, G2, node_match=node_match, node_subst_cost=node_substitude_cost)
    node_edit_path, edge_edit_path, cost = list(generator)[0]
    if old_query_projections_set == new_query_projections_set:
        return get_the_difference_in_natural_language(G1, G2, node_edit_path, edge_edit_path, cost)
    else:
        query_difference_string = "Query projections has changed from " + str(old_query_projections_set) + " to " + str(new_query_projections_set) + "."
        natural_language_difference_string = get_the_difference_in_natural_language(G1, G2, node_edit_path, edge_edit_path, cost)
        if  natural_language_difference_string == "Nothing has changed!":
            return query_difference_string
        else:
            return query_difference_string + " " + natural_language_difference_string

def get_the_difference_in_natural_language(G1, G2, node_edit_path, edge_edit_path, cost):
    if cost == 0:
        return "Nothing has changed!"
    node_difference_strings = get_node_differences(G1, G2, node_edit_path)
    node_difference_strings = [node_difference_string for node_difference_string in node_difference_strings if node_difference_string != "N.A."]
    return " ".join(node_difference_strings)


def get_node_differences(G1, G2, node_edit_path):
    node_differences = []
    substitued_nodes = [x for x in node_edit_path if x[0] is not None and x[1] is not None]
    inserted_nodes = [x for x in node_edit_path if x[0] is None and x[1] is not None]
    deleted_nodes = [x for x in node_edit_path if x[0] is not None and x[1] is None]
    print(node_edit_path)
    print(substitued_nodes)
    print(inserted_nodes)
    print(deleted_nodes)
    for node in substitued_nodes:
        node_difference = find_difference_between_two_nodes(G1.nodes[node[0]]['custom_object'], G2.nodes[node[1]]['custom_object'])
        node_differences.append(node_difference)
    if len(inserted_nodes) != 0:
        node_differences.extend(get_the_natural_language_output_for_the_inserted_nodes(G1, G2, substitued_nodes, inserted_nodes))
    return node_differences

def find_difference_between_two_nodes(node_1, node_2):
    return node_1.compare_differences(node_2)

def get_the_natural_language_output_for_the_inserted_nodes(G1, G2, substitued_nodes, inserted_nodes):
    substitued_nodes_dict = {}
    for node_val, node_key in substitued_nodes:
        substitued_nodes_dict[node_key] = node_val
    insert_nodes_in_G2 = [x[1] for x in inserted_nodes]
    G2_nodes = list(G2.nodes())
    G2_nodes.reverse()
    node_differences = []
    node_before = None
    current_inserted_nodes = []
    for node in G2_nodes:
        if node in substitued_nodes_dict:
            if node_before is None:
                node_before = node
            else:
                node_differences.append(get_natural_language_difference_between_two_nodes(G2, node_before, node, current_inserted_nodes))
                node_before = node
        if node not in insert_nodes_in_G2:
            continue
        elif node != min(insert_nodes_in_G2):
            current_inserted_nodes.append(node)
        else:
            current_inserted_nodes.append(node)
            node_differences.append(get_natural_language_difference_between_two_nodes(G2, node_before, None, current_inserted_nodes))
            current_inserted_nodes.clear()
    return node_differences


# def get_natural_language_output_for_the_deleted_nodes(G1, G2, deleted_nodes):
#     pass

def get_natural_language_difference_between_two_nodes(G2, node_before, node_after, inserted_nodes):
    prev_node_type = G2.nodes[node_before]['custom_object'].node_type
    inserted_nodes_type = [G2.nodes[x]['custom_object'].node_type for x in inserted_nodes]
    if node_after is None:
        return get_natural_language_connection_between_objects_in_list(inserted_nodes_type) + " get inserted after " + prev_node_type + ". "
    else:
        next_node_type = G2.nodes[node_after]['custom_object'].node_type
        return get_natural_language_connection_between_objects_in_list(inserted_nodes_type) + " get inserted between " + str(prev_node_type) + " and " + str(next_node_type)

def get_natural_language_connection_between_objects_in_list(objects):
    if len(objects) == 1:
        return objects[0]
    else:
        last_object = objects[-1]
        objects_up_to_last_object = objects[:-1]
        natural_language_connection = ", ".join(objects_up_to_last_object)
        natural_language_connection += " and " + last_object
        return natural_language_connection

    