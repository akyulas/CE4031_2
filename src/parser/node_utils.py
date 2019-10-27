def set_output_name(output_name):
    if "T" == output_name[0] and output_name[1:].isdigit():
        output_name = int(output_name[1:])
    else:
        output_name = output_name
    return output_name

class Node(object):
    def __init__(self, node_type, relation_name, schema, alias, group_key, sort_key, join_type, index_name, 
            hash_cond, table_filter, index_cond, merge_cond, recheck_cond, join_filter, subplan_name,
            plan_rows, output_name):
        self.node_type = node_type
        self.relation_name = relation_name
        self.schema = schema
        self.alias = alias
        self.group_key = group_key
        self.sort_key = sort_key
        self.join_type = join_type
        self.index_name = index_name
        self.hash_cond = hash_cond
        self.table_filter = table_filter
        self.index_cond = index_cond
        self.merge_cond = merge_cond
        self.recheck_cond = recheck_cond
        self.join_filter = join_filter
        self.subplan_name = subplan_name
        self.plan_rows = plan_rows
        self.output_name = output_name
    
    def __eq__(self, other): 
        if not isinstance(other, Node):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.node_type == other.node_type and self.relation_name == other.relation_name and \
        self.schema == other.schema and self.alias == other.alias and self.group_key == other.group_key and \
        self.sort_key == other.sort_key and self.join_type == other.join_type and self.index_name == other.index_name \
        and self.hash_cond == other.hash_cond and self.table_filter == other.table_filter and self.index_cond == other.index_name  \
        and self.merge_cond == other.merge_cond and self.recheck_cond == other.recheck_cond and self.join_filter == other.join_filter \
        and self.subplan_name == other.subplan_name and self.plan_rows == other.plan_rows and self.output_name == other.output_name