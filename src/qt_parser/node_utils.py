def set_output_name(output_name):
    """
    This function is used to define the output name
    """
    try:
        if "T" == output_name[0] and output_name[1:].isdigit():
            output_name = int(output_name[1:])
        else:
            output_name = output_name
    except:
        output_name = None
    return output_name

class Node(object):
    """
    Define an object used to represent a node
    """
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
        """
        This function is used to check if two node types are equal
        """ 
        if not isinstance(other, Node):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.node_type == other.node_type and self.relation_name == other.relation_name and \
        self.schema == other.schema and self.alias == other.alias and self.group_key == other.group_key and \
        self.sort_key == other.sort_key and self.join_type == other.join_type and self.index_name == other.index_name \
        and self.hash_cond == other.hash_cond and self.table_filter == other.table_filter and self.index_cond == other.index_name  \
        and self.merge_cond == other.merge_cond and self.recheck_cond == other.recheck_cond and self.join_filter == other.join_filter \
        and self.subplan_name == other.subplan_name and self.plan_rows == other.plan_rows and self.output_name == other.output_name
    
    def compare_differences(self, other, original_label, current_label):
        """
        This function is ued to comparent differences between two nodes
        """
        differences = []
        if not(self.node_type == other.node_type or ("Scan" in self.node_type and "Scan" in other.node_type) or \
            ("Aggregate" in self.node_type and "Aggregate" in other.node_type) or ((self.node_type == "Nested Loop" or "Join" in self.node_type)\
                and (other.node_type == "Nested Loop" or "Join" in other.node_type))):
            difference = "The node with node label " + str(original_label) + " of type " + str(self.node_type) + " has evolved into " + str(current_label) + " of type " + str(other.node_type)
            differences.append(difference)
        else:
            if (original_label != current_label or self.node_type != other.node_type):
                difference = "The node with node label " + str(original_label) + " of type " + str(self.node_type) + " gets mapped to new node label " + str(current_label) + " of type " + str(other.node_type)
                differences.append(difference)
            if self.relation_name != other.relation_name:
                difference =  "relation name " + str(self.relation_name) + " has changed into " +  "relation name " + str(other.relation_name)
                differences.append(difference)
            if self.schema != other.schema:
                difference = "schema has changed from " + str(self.schema) + " into " + str(other.schema)
                differences.append(difference)
            if self.alias != other.alias:
                difference = "alias has changed from " + str(self.alias) + " into " + str(other.alias)
                differences.append(difference)
            if self.group_key != other.group_key:
                difference = "group key has changed from " + str(self.group_key) + " into " + str(other.group_key)
                differences.append(difference)
            if self.sort_key != other.sort_key:
                difference = "sort key has changed from " + str(self.sort_key) + " into " + str(other.sort_key)
                differences.append(difference)
            if self.join_type != other.join_type:
                difference = "join type has changed from " + str(self.join_type) + " into " + str(other.join_type)
                differences.append(difference)
            if self.index_name != other.index_name:
                difference = "index name has changed from " + str(self.index_name) + " into " + str(other.index_name)
                differences.append(difference)
            if self.hash_cond != other.hash_cond:
                difference = "hash condition has changed from " + str(self.hash_cond) + " into " + str(other.hash_cond)
                differences.append(difference)
            if self.table_filter != other.table_filter:
                difference =  "table filter has changed from " + str(self.table_filter) + " into " + str(other.table_filter)
                differences.append(difference)
            if self.index_cond != other.index_cond:
                difference =  "index condition has changed from " + str(self.index_cond) + " into " + str(other.index_cond)
                differences.append(difference)
            if self.merge_cond != other.merge_cond:
                difference =  "merge condition has changed from " + str(self.merge_cond) + " into " + str(other.merge_cond)
                differences.append(difference)
            if self.recheck_cond != other.recheck_cond:
                difference =  "recheck condition has changed from " + str(self.recheck_cond) + " into " + str(other.recheck_cond)
                differences.append(difference)
            if self.join_filter != other.join_filter:
                difference =  "join filter has changed from " + str(self.join_filter) + " into " + str(other.join_filter)
                differences.append(difference)
            if self.subplan_name != other.subplan_name:
                difference =  "subplan name has changed from " + str(self.subplan_name) + " into " + str(other.subplan_name)
                differences.append(difference)
            if self.output_name != other.output_name:
                difference =  "output name has changed from " + str(self.output_name) + " into " + str(other.output_name)
                differences.append(difference)
        if len(differences) == 0:
            return "N.A."
        if len(differences) == 1:
            difference = differences[0]
            if (original_label == current_label and self.node_type == other.node_type):
                return "The node with node label " + str(original_label) + " of type " + str(self.node_type) + " has the following changes: " \
                    + difference[0] +  difference [1:] + ".\n"
            else:
                return difference[0].upper() +  difference [1:] + ".\n"
        else:
            last_difference = differences[-1]
            differences_up_to_last = differences[:-1]
            difference_string = ", ".join(differences_up_to_last)
            difference_string += " and " + last_difference + ".\n"
            if (original_label == current_label and self.node_type == other.node_type):
                return "The node with node label " + str(original_label) + " of type " + str(self.node_type) + " has the following changes: " \
                    + difference_string[0] +  difference_string[1:]
            else:
                return difference_string[0].upper() +  difference_string[1:]
