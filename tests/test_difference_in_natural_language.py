from .context import find_difference_between_two_query_plans, PostgresWrapper

postgres_wrapper = PostgresWrapper()
conn = postgres_wrapper.connect_to_postgres_db("localhost", "TPC-H", "postgres", "password", port=5433)

def test_node_changes_for_table_changes_are_reflected_correctly():
    old_query = "select * from lineitem;"
    new_query = "select * from customer"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string == "Relation name lineitem has changed into relation name customer."

def test_node_changes_for_filter_changes_are_reflected_correctly():
    old_query = "select * from customer;"
    new_query = "select * from customer where c_nationkey = 15;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string == "Table filter has changed from None into (c_nationkey = 15)."
    #############################################################################################
    old_query = "select * from customer where c_nationkey > 0;"
    new_query = "select * from customer where c_nationkey = 15;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string == "Table filter has changed from (c_nationkey > 0) into (c_nationkey = 15)."

def test_node_changes_for_table_changes_and_filter_changes_are_reflected_correctly():
    old_query = "select * from lineitem;"
    new_query = "select * from customer where c_nationkey > 0;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string == "Relation name lineitem has changed into relation name customer and table filter has changed from None into (c_nationkey > 0)."

def test_projection_changes_are_reflected_correctly_are_reflected_correctly():
    old_query = "select * from customer;"
    new_query = "select (c_nationkey, c_name) from customer;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string == "Query projections has changed from {'*'} to {'c_name', 'c_nationkey'}."
    #############################################################################################
    old_query = "select * from customer;"
    new_query = "select (c_nationkey, c_name) from customer where c_nationkey = 15;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string == "Query projections has changed from {'*'} to {'c_name', 'c_nationkey'}. Table filter has changed from None into (c_nationkey = 15)."
