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
    elif node_1_object.node_type == node_2_object.node_type and 'Scan'  in node_1_object.node_type and node_1_object.relation_name == node_2_object.relation_name:
        return 0.25
    elif node_1_object.node_type == node_2_object.node_type and 'Aggregate' in node_1_object.node_type and node_1_object.group_key == node_2_object.group_key:
        return 0.25
    elif node_1_object.node_type == node_2_object.node_type and "Sort" in node_1_object.node_type and node_1_object.sort_key == node_2_object.sort_key:
        return 0.25
    elif node_1_object.node_type == node_2_object.node_type and ('Hash Join' in node_1_object.node_type) and node_1_object.hash_cond == node_2_object.hash_cond:
        return 0.25
    elif node_1_object.node_type == node_2_object.node_type and ('Merge Join' in node_1_object.node_type) and node_1_object.merge_cond == node_2_object.merge_cond:
        return 0.25
    elif node_1_object.node_type == node_2_object.node_type:
        return 0.5
    elif 'Sort' in node_1_object.node_type and 'Sort' in node_2_object.node_type:
        return 1.0
    elif 'Scan' in node_1_object.node_type and 'Scan' in node_2_object.node_type:
        return 1.0
    elif 'Aggregate' in node_1_object.node_type and 'Aggregate' in node_2_object.node_type:
        return 1.0
    elif ('Join' in node_1_object.node_type or node_1_object.node_type == 'Nested Loop') and ('Join' in node_2_object.node_type or node_2_object.node_type == 'Nested Loop'):
        return 1.0
    return 9223372036854775807

def edge_subt_cost(old_edge_dict, new_edge_dict):
    old_edge_parent_type = old_edge_dict['parent_type']
    old_edge_children_type = old_edge_dict['children_type']
    new_edge_parent_type = new_edge_dict['parent_type']
    new_ege_children_type = new_edge_dict['children_type']
    if old_edge_parent_type == new_edge_parent_type and old_edge_children_type == new_ege_children_type:
        return 0
    return 1.0
    


def get_graph_from_query_plan(query_plan):
    G = nx.DiGraph()
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
            parent_type = G.nodes[parent_index]['custom_object'].node_type
            children_type = current_node.node_type

            G.add_edge(parent_index, current_index, **{'parent_type': str(parent_type), 'children_type': str(children_type)})

        if 'Plans' in current_plan:
            for item in current_plan['Plans']:
                # push child plans into queue
                q.put(item)
                # push parent for each child into queue
                q_node.put(current_index)
        current_index += 1
    
    return G
    
def find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan):
    result = re.search('select(.*?)from', old_query, re.IGNORECASE)
    old_query_projections = result.group(1)
    old_query_projections_list = [x.strip() for x in old_query_projections.split(',')]
    for i in range(len(old_query_projections_list)):
        projection = old_query_projections_list[i]
        open_bracket_count = projection.count("(")
        closed_bracket_count = projection.count(")")
        while open_bracket_count > closed_bracket_count:
            projection = projection.replace('(', '', 1)
            open_bracket_count = open_bracket_count - 1
        while closed_bracket_count > open_bracket_count:
            projection = projection.replace(')', '', 1)
            closed_bracket_count = closed_bracket_count - 1
        old_query_projections_list[i] = projection
    print(old_query_projections_list)
    old_query_projections_list.sort()
    result = re.search('select(.*?)from', new_query, re.IGNORECASE)
    new_query_projections = result.group(1)
    new_query_projections_list = [x.strip() for x in new_query_projections.split(',')]
    for i in range(len(new_query_projections_list)):
        projection = new_query_projections_list[i]
        open_bracket_count = projection.count("(")
        closed_bracket_count = projection.count(")")
        while open_bracket_count > closed_bracket_count:
            projection = projection.replace('(', '', 1)
            open_bracket_count = open_bracket_count - 1
        while closed_bracket_count > open_bracket_count:
            projection = projection.replace(')', '', 1)
            closed_bracket_count = closed_bracket_count - 1
        new_query_projections_list[i] = projection
    print(new_query_projections_list)
    new_query_projections_list.sort()      
    G1 = get_graph_from_query_plan(old_query_plan)
    G2 = get_graph_from_query_plan(new_query_plan)
    generator = optimize_edit_paths(G1, G2, node_match=node_match, node_subst_cost=node_substitude_cost, edge_subst_cost=edge_subt_cost)
    node_edit_path, edge_edit_path, cost = list(generator)[0]
    if old_query_projections_list == new_query_projections_list:
        return get_the_difference_in_natural_language(G1, G2, node_edit_path, edge_edit_path, cost)
    else:
        old_query_projections_list.sort()
        new_query_projections_list.sort()
        query_difference_string = "Query projections has changed from " + str(old_query_projections_list) + " to " + str(new_query_projections_list) + "."
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
    join_nodes_for_G2 = [x for x in G2.nodes() if G2.nodes[x]['custom_object'].node_type == "Nested Loop" or "Join" in G2.nodes[x]['custom_object'].node_type]
    join_nodes_for_G1 = [x for x in G1.nodes() if G1.nodes[x]['custom_object'].node_type == "Nested Loop" or "Join" in G1.nodes[x]['custom_object'].node_type]
    for node in substitued_nodes:
        node_difference = find_difference_between_two_nodes(G1.nodes[node[0]]['custom_object'], G2.nodes[node[1]]['custom_object'], node[0], node[1])
        node_differences.append(node_difference)
    if len(inserted_nodes) != 0:
        node_differences.extend(get_natural_language_output_for_the_inserted_nodes(G2, inserted_nodes, substitued_nodes, join_nodes_for_G2))
    if len(deleted_nodes) != 0:
        node_differences.extend(get_natural_language_output_for_the_deleted_nodes(G1, deleted_nodes, substitued_nodes, join_nodes_for_G1))
    return node_differences

def find_difference_between_two_nodes(node_1, node_2, node_1_label, node_2_label):
    return node_1.compare_differences(node_2, node_1_label, node_2_label)

def get_natural_language_output_for_the_inserted_nodes(G2, inserted_nodes, substitued_nodes, join_nodes):
    difference_list = []
    inserted_nodes_list = []
    inserted_nodes_in_G2 = [x[1] for x in inserted_nodes]
    differences = []
    substitued_nodes_in_G2 = [x[1] for x in substitued_nodes]
    for node in list(nx.dfs_postorder_nodes(G2, source=0)):
        if node in substitued_nodes_in_G2:
            continue
        if node in join_nodes:
            differences.append(get_natural_language_ouput_for_join_queries(G2, node))
        else:
            inserted_nodes_list.append(node)
            successors_list = list(G2.successors(inserted_nodes_list[0]))
            if len(successors_list) == 0:
                successor = None
            else:
                successor = successors_list[0]
            if node == 0:
                parent = None
                differences.append(get_natural_language_ouput_between_sucessor_and_parent_for_insertion(G2, successor, parent, inserted_nodes_list))
                inserted_nodes_list.clear()
            else:
                parent = list(G2.predecessors(node))[0]
                if parent in substitued_nodes_in_G2 or parent in join_nodes:
                    differences.append(get_natural_language_ouput_between_sucessor_and_parent_for_insertion(G2, successor, parent, inserted_nodes_list))
                    inserted_nodes_list.clear()
    return differences


def get_natural_language_output_for_the_deleted_nodes(G1, deleted_nodes, substitued_nodes, join_nodes):
    difference_list = []
    deleted_nodes_list = []
    deleted_nodes_in_G1 = [x[0] for x in deleted_nodes]
    differences = []
    substitued_nodes_in_G1 = [x[0] for x in substitued_nodes]
    for node in list(nx.dfs_postorder_nodes(G1, source=0)):
        if node in substitued_nodes_in_G1:
            continue
        else:
            deleted_nodes_list.append(node)
            successors_list = list(G1.successors(deleted_nodes_list[0]))
            if len(successors_list) == 0:
                successor = None
            else:
                successor = successors_list[0]
            if node == 0:
                parent = None
                differences.append(get_natural_language_ouput_between_sucessor_and_parent_for_deletion(G1, successor, parent, deleted_nodes_list))
                deleted_nodes_list.clear()
            else:
                parent = list(G1.predecessors(node))[0]
                if parent in substitued_nodes or parent in join_nodes:
                    differences.append(get_natural_language_ouput_between_sucessor_and_parent_for_deletion(G1, successor, parent, deleted_nodes_list))
                    deleted_nodes_list.clear()
    return differences

def get_natural_language_output_with_node_type_from_node_index(G, index):
    node_type = G.nodes[index]['custom_object'].node_type
    return str(node_type) + " (" + str(index) + ")"


def get_natural_language_ouput_for_join_queries(G, join_node_index):
    successors = list(G.successors(join_node_index))
    successors_with_node_type = [get_natural_language_output_with_node_type_from_node_index(G, successor) for successor in successors]
    return get_natural_language_output_with_node_type_from_node_index(G, join_node_index) + " joins " + get_natural_language_connection_between_objects_in_list(successors_with_node_type) + \
        " and gets inserted."
    

def get_natural_language_ouput_between_sucessor_and_parent_for_insertion(G2, successor, parent, inserted_nodes):
    inserted_nodes_with_nodes_type = [get_natural_language_output_with_node_type_from_node_index(G2, index) for index in inserted_nodes]
    if successor != None and parent != None:
        return str(get_natural_language_connection_between_objects_in_list(inserted_nodes_with_nodes_type)) + " gets inserted in between " + get_natural_language_output_with_node_type_from_node_index(G2, successor) + " and " + get_natural_language_output_with_node_type_from_node_index(G2, parent) +"."
    if successor == None and parent == None:
        return str(get_natural_language_connection_between_objects_in_list(inserted_nodes_with_nodes_type)) + " gets inserted"
    if successor == None:
        return str(get_natural_language_connection_between_objects_in_list(inserted_nodes_with_nodes_type)) + " gets inserted before " + get_natural_language_output_with_node_type_from_node_index(G2, parent) + "."
    return str(get_natural_language_connection_between_objects_in_list(inserted_nodes_with_nodes_type)) + " gets inserted after " + get_natural_language_output_with_node_type_from_node_index(G2, successor) + "."

def get_natural_language_ouput_between_sucessor_and_parent_for_deletion(G1, successor, parent, deleted_nodes):
    deleted_nodes_with_nodes_type = [get_natural_language_output_with_node_type_from_node_index(G1, index) for index in deleted_nodes]
    if successor != None and parent != None:
        return str(get_natural_language_connection_between_objects_in_list(deleted_nodes_with_nodes_type)) + " gets deleted in between " + get_natural_language_output_with_node_type_from_node_index(G1, successor) + " and " + get_natural_language_output_with_node_type_from_node_index(G1, parent) +"."
    if successor == None and parent == None:
        return str(get_natural_language_connection_between_objects_in_list(deleted_nodes_with_nodes_type)) + " gets deleted"
    if successor == None:
        return str(get_natural_language_connection_between_objects_in_list(deleted_nodes_with_nodes_type)) + " gets deleted before " + get_natural_language_output_with_node_type_from_node_index(G1, parent) + "."
    return str(get_natural_language_connection_between_objects_in_list(deleted_nodes_with_nodes_type)) + " gets deleted after " + get_natural_language_output_with_node_type_from_node_index(G1, successor) + "."
    

# def get_natural_language_difference_between_two_nodes_for_deletion(G2, node_before, node_after, deleted_nodes):
#     prev_node_type = G2.nodes[node_before]['custom_object'].node_type
#     deleted_nodes_type = [G2.nodes[x]['custom_object'].node_type for x in deleted_nodes]
#     if node_after is None:
#         return get_natural_language_connection_between_objects_in_list(deleted_nodes_type) + " get deleted after " + prev_node_type + "."
#     else:
#         next_node_type = G2.nodes[node_after]['custom_object'].node_type
#         return get_natural_language_connection_between_objects_in_list(deleted_nodes_type) + " get deleted between " + str(prev_node_type) + " and " + str(next_node_type)

def get_natural_language_connection_between_objects_in_list(objects):
    if len(objects) == 1:
        return objects[0]
    else:
        last_object = objects[-1]
        objects_up_to_last_object = objects[:-1]
        natural_language_connection = ", ".join(objects_up_to_last_object)
        natural_language_connection += " and " + last_object
        return natural_language_connection

    
