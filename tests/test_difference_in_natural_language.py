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
    assert natural_language_string == "The node with node label 0 of type Seq Scan gets mapped to new node label 0 of type Seq Scan, relation name lineitem has changed into relation name customer, alias has changed from lineitem into customer and output name has changed from lineitem into customer."

def test_node_changes_for_filter_changes_are_reflected_correctly():
    old_query = "select * from customer;"
    new_query = "select * from customer where c_nationkey = 15;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string == "The node with node label 0 of type Seq Scan gets mapped to new node label 0 of type Seq Scan and table filter has changed from None into (c_nationkey = 15)."
    #############################################################################################
    old_query = "select * from customer where c_nationkey > 0;"
    new_query = "select * from customer where c_nationkey = 15;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string == "The node with node label 0 of type Seq Scan gets mapped to new node label 0 of type Seq Scan and table filter has changed from (c_nationkey > 0) into (c_nationkey = 15)."

def test_node_changes_for_table_changes_and_filter_changes_are_reflected_correctly():
    old_query = "select * from lineitem;"
    new_query = "select * from customer where c_nationkey > 0;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string == "The node with node label 0 of type Seq Scan gets mapped to new node label 0 of type Seq Scan, relation name lineitem has changed into relation name customer, alias has changed from lineitem into customer, table filter has changed from None into (c_nationkey > 0) and output name has changed from lineitem into customer."

def test_projection_changes_are_reflected_correctly():
    old_query = "select * from customer;"
    new_query = "select (c_nationkey, c_name) from customer;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string == "Query projections has changed from ['*'] to ['c_name', 'c_nationkey']."
    #############################################################################################
    old_query = "select * from customer;"
    new_query = "select (c_nationkey, c_name) from customer where c_nationkey = 15;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string == "Query projections has changed from ['*'] to ['c_name', 'c_nationkey']. The node with node label 0 of type Seq Scan gets mapped to new node label 0 of type Seq Scan and table filter has changed from None into (c_nationkey = 15)."

def test_insertions_are_reflected_correctly():
    old_query = "select * from lineitem;"
    new_query = "select l_returnflag, l_linestatus,sum(l_quantity) as sum_qty, sum(l_extendedprice) as sum_base_price, sum(l_extendedprice * (1 - l_discount)) as sum_disc_price, sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge, avg(l_quantity) as avg_qty, avg(l_extendedprice) as avg_price, avg(l_discount) as avg_disc, count(*) as count_order from lineitem where l_shipdate <= '1998-09-16' group by l_returnflag, l_linestatus order by l_returnflag, l_linestatus;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string == "Query projections has changed from ['*'] to ['avgl_discount as avg_disc', 'avgl_extendedprice as avg_price', 'avgl_quantity as avg_qty', 'count* as count_order', 'l_linestatus', 'l_returnflag', 'suml_extendedprice * 1 - l_discount * 1 + l_tax as sum_charge', 'suml_extendedprice * 1 - l_discount as sum_disc_price', 'suml_extendedprice as sum_base_price', 'suml_quantity as sum_qty']. The node with node label 0 of type Seq Scan gets mapped to new node label 4 of type Seq Scan and table filter has changed from None into (l_shipdate <= '1998-09-16'::date). Aggregate (3), Sort (2), Gather Merge (1) and Aggregate (0) gets inserted after Seq Scan (4)."

def test_deletions_are_reflected_correctly():
    old_query = "select l_returnflag, l_linestatus,sum(l_quantity) as sum_qty, sum(l_extendedprice) as sum_base_price, sum(l_extendedprice * (1 - l_discount)) as sum_disc_price, sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge, avg(l_quantity) as avg_qty, avg(l_extendedprice) as avg_price, avg(l_discount) as avg_disc, count(*) as count_order from lineitem where l_shipdate <= '1998-09-16' group by l_returnflag, l_linestatus order by l_returnflag, l_linestatus;"
    new_query = "select * from lineitem;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string == "Query projections has changed from ['avgl_discount as avg_disc', 'avgl_extendedprice as avg_price', 'avgl_quantity as avg_qty', 'count* as count_order', 'l_linestatus', 'l_returnflag', 'suml_extendedprice * 1 - l_discount * 1 + l_tax as sum_charge', 'suml_extendedprice * 1 - l_discount as sum_disc_price', 'suml_extendedprice as sum_base_price', 'suml_quantity as sum_qty'] to ['*']. The node with node label 4 of type Seq Scan gets mapped to new node label 0 of type Seq Scan and table filter has changed from (l_shipdate <= '1998-09-16'::date) into None. Aggregate (3), Sort (2), Gather Merge (1) and Aggregate (0) gets deleted after Seq Scan (4)."

def test_subqueries_are_reflected_correctly():
    old_query = "select * from orders;"
    new_query = "select o_orderpriority, count(*) as order_count from orders as o where o_orderdate >= '1996-05-01' and o_orderdate < '1996-08-01' and exists (select * from lineitem where l_orderkey = o.o_orderkey and l_commitdate < l_receiptdate) group by o_orderpriority order by o_orderpriority;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string == "Query projections has changed from ['*'] to [\"count* as order_count from orders as o where o_orderdate >= '1996-05-01' and o_orderdate < '1996-08-01' and exists select *\", 'o_orderpriority']. The node with node label 0 of type Seq Scan gets mapped to new node label 5 of type Seq Scan, alias has changed from orders into o and table filter has changed from None into ((o_orderdate >= '1996-05-01'::date) AND (o_orderdate < '1996-08-01'::date)). Index Scan (6) gets inserted before Nested Loop (4). Nested Loop (4) joins Seq Scan (5) and Index Scan (6)and gets inserted. Sort (3), Aggregate (2), Gather Merge (1) and Aggregate (0) gets inserted after Nested Loop (4)."
    ################################################################################################################################################################################
    old_query = "select o_orderpriority, count(*) as order_count from orders as o where o_orderdate >= '1996-05-01' and o_orderdate < '1996-08-01' and exists (select * from lineitem where l_orderkey = o.o_orderkey and l_commitdate < l_receiptdate) group by o_orderpriority order by o_orderpriority;"
    new_query = "select * from orders;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string == "Query projections has changed from [\"count* as order_count from orders as o where o_orderdate >= '1996-05-01' and o_orderdate < '1996-08-01' and exists select *\", 'o_orderpriority'] to ['*']. The node with node label 5 of type Seq Scan gets mapped to new node label 0 of type Seq Scan, alias has changed from o into orders and table filter has changed from ((o_orderdate >= '1996-05-01'::date) AND (o_orderdate < '1996-08-01'::date)) into None. Index Scan (6) gets deleted before Nested Loop (4). Nested Loop (4), Sort (3), Aggregate (2), Gather Merge (1) and Aggregate (0) gets deleted after Seq Scan (5)."
