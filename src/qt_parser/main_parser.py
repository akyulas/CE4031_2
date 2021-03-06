import networkx as nx
import queue
import re
try:
    from utils.singleton import Singleton
except:
    from src.utils.singleton import Singleton
from .find_difference import node_substitude_cost, edge_subt_cost, get_the_difference_in_natural_language, node_match
from .node_utils import set_output_name, Node
from networkx.algorithms.similarity import optimize_edit_paths

class Parser(metaclass=Singleton):
    """
    Define an object used to store graphs and find the differences between the graphs
    """

    old_graph = nx.DiGraph()
    new_graph = nx.DiGraph()

    def update_graphs_with_new_query_plans(self, query_plan_1, query_plan_2):
        """
        This function is used to update the graphs by regenearting them from 
        new query plan
        """
        if query_plan_1 is None:
            self.old_graph.clear()
        else:
            self.update_graph_from_query_plan(self.old_graph, query_plan_1)
        if query_plan_2 is None:
            self.new_graph.clear()
        else:
            self.update_graph_from_query_plan(self.new_graph, query_plan_2)
     
    def get_graphs_for_visualizations(self):
        """
        This function is used to generate graphs that will be used for visualization
        """
        return self.old_graph.reverse(), self.new_graph.reverse()
    
    def get_difference_between_old_and_new_graphs(self, old_query, new_query):
        """
        This function is used to get the difference between old and new graphs
        """
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
        new_query_projections_list.sort()
        generator = optimize_edit_paths(self.old_graph, self.new_graph, node_match=node_match, node_subst_cost=node_substitude_cost, edge_subst_cost=edge_subt_cost)
        node_edit_path, edge_edit_path, cost = list(generator)[0]
        if old_query_projections_list == new_query_projections_list:
            return get_the_difference_in_natural_language(self.old_graph, self.new_graph, node_edit_path, edge_edit_path, cost)
        else:
            old_query_projections_list.sort()
            new_query_projections_list.sort()
            query_difference_string = "Query projections has changed from " + str(old_query_projections_list) + " in the old query to " + str(new_query_projections_list) + " in the new query."
            natural_language_difference_string = get_the_difference_in_natural_language(self.old_graph, self.new_graph, node_edit_path, edge_edit_path, cost)
            if  natural_language_difference_string == "Nothing has changed!":
                return query_difference_string
            else:
                return query_difference_string + "\n" + natural_language_difference_string

    def update_graph_from_query_plan(self, G, query_plan):
        """
        This function is used to update the current graph with information 
        from the query plan
        """
        G.clear()
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
