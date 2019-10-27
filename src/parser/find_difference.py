import queue
import networkx as nx
from .node_utils import set_output_name, Node
from networkx.algorithms.similarity import optimize_edit_paths

def node_match(node_1, node_2):
    return node_1['custom_object'] == node_2['custom_object']


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
        if 'Actual Rows' in current_plan:
            actual_rows = current_plan['Actual Rows']
        if 'Actual Total Time' in current_plan:
            actual_time = current_plan['Actual Total Time']
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
    
def find_difference_between_two_query_plans(old_query_plan, new_query_plan):
    G1 = get_graph_from_query_plan(old_query_plan)
    G2 = get_graph_from_query_plan(new_query_plan)
    generator = optimize_edit_paths(G1, G2, node_match=node_match)
    for i in generator:
        print(i)

    