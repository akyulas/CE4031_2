from .context import find_difference_between_two_query_plans, PostgresWrapper

host = "localhost"
DB_NAME = "TPC-H"
user = "postgres"
password = "password"
port=5433
postgres_wrapper = PostgresWrapper()
conn = postgres_wrapper.connect_to_postgres_db(host, DB_NAME, user, password, port=port)

def test_node_changes_for_table_changes_are_reflected_correctly():
    old_query = "select * from lineitem;"
    new_query = "select * from customer;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string.replace("\n", "") == "The node with node label 0 of type Seq Scan has the following changes: relation name lineitem has changed into relation name customer, alias has changed from lineitem into customer and output name has changed from lineitem into customer."

def test_node_changes_for_filter_changes_are_reflected_correctly():
    old_query = "select * from customer;"
    new_query = "select * from customer where c_nationkey = 15;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string.replace("\n", "") == "The node with node label 0 of type Seq Scan has the following changes: table filter has changed from None into (c_nationkey = 15)."
    #############################################################################################
    old_query = "select * from customer where c_nationkey > 0;"
    new_query = "select * from customer where c_nationkey = 15;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string.replace("\n", "") == "The node with node label 0 of type Seq Scan has the following changes: table filter has changed from (c_nationkey > 0) into (c_nationkey = 15)."

def test_node_changes_for_table_changes_and_filter_changes_are_reflected_correctly():
    old_query = "select * from lineitem;"
    new_query = "select * from customer where c_nationkey > 0;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string.replace("\n", "") == "The node with node label 0 of type Seq Scan has the following changes: relation name lineitem has changed into relation name customer, alias has changed from lineitem into customer, table filter has changed from None into (c_nationkey > 0) and output name has changed from lineitem into customer."

def test_projection_changes_are_reflected_correctly():
    old_query = "select * from customer;"
    new_query = "select (c_nationkey, c_name) from customer;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string.replace("\n", "") == "Query projections has changed from ['*'] in the old query to ['c_name', 'c_nationkey'] in the new query."
    #############################################################################################
    old_query = "select * from customer;"
    new_query = "select (c_nationkey, c_name) from customer where c_nationkey = 15;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string.replace("\n", "") == "Query projections has changed from ['*'] in the old query to ['c_name', 'c_nationkey'] in the new query.The node with node label 0 of type Seq Scan has the following changes: table filter has changed from None into (c_nationkey = 15)."

def test_insertions_are_reflected_correctly():
    old_query = "select * from lineitem;"
    new_query = "select l_returnflag, l_linestatus,sum(l_quantity) as sum_qty, sum(l_extendedprice) as sum_base_price, sum(l_extendedprice * (1 - l_discount)) as sum_disc_price, sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge, avg(l_quantity) as avg_qty, avg(l_extendedprice) as avg_price, avg(l_discount) as avg_disc, count(*) as count_order from lineitem where l_shipdate <= '1998-09-16' group by l_returnflag, l_linestatus order by l_returnflag, l_linestatus;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string.replace("\n", "") == "Query projections has changed from ['*'] in the old query to ['avg(l_discount) as avg_disc', 'avg(l_extendedprice) as avg_price', 'avg(l_quantity) as avg_qty', 'count(*) as count_order', 'l_linestatus', 'l_returnflag', 'sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge', 'sum(l_extendedprice * (1 - l_discount)) as sum_disc_price', 'sum(l_extendedprice) as sum_base_price', 'sum(l_quantity) as sum_qty'] in the new query.The node with node label 0 of type Seq Scan gets mapped to new node label 4 of type Seq Scan and table filter has changed from None into (l_shipdate <= '1998-09-16'::date).Aggregate (3,New), Sort (2,New), Gather Merge (1,New) and Aggregate (0,New) gets inserted after Seq Scan (4,New)."

def test_deletions_are_reflected_correctly():
    old_query = "select l_returnflag, l_linestatus,sum(l_quantity) as sum_qty, sum(l_extendedprice) as sum_base_price, sum(l_extendedprice * (1 - l_discount)) as sum_disc_price, sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge, avg(l_quantity) as avg_qty, avg(l_extendedprice) as avg_price, avg(l_discount) as avg_disc, count(*) as count_order from lineitem where l_shipdate <= '1998-09-16' group by l_returnflag, l_linestatus order by l_returnflag, l_linestatus;"
    new_query = "select * from lineitem;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string.replace("\n", "") == "Query projections has changed from ['avg(l_discount) as avg_disc', 'avg(l_extendedprice) as avg_price', 'avg(l_quantity) as avg_qty', 'count(*) as count_order', 'l_linestatus', 'l_returnflag', 'sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge', 'sum(l_extendedprice * (1 - l_discount)) as sum_disc_price', 'sum(l_extendedprice) as sum_base_price', 'sum(l_quantity) as sum_qty'] in the old query to ['*'] in the new query.The node with node label 4 of type Seq Scan gets mapped to new node label 0 of type Seq Scan and table filter has changed from (l_shipdate <= '1998-09-16'::date) into None.Aggregate (3,Old), Sort (2,Old), Gather Merge (1,Old) and Aggregate (0,Old) that is after Seq Scan (4,Old) gets deleted."

def test_subqueries_are_reflected_correctly():
    old_query = "select * from orders;"
    new_query = "select o_orderpriority, count(*) as order_count from orders as o where o_orderdate >= '1996-05-01' and o_orderdate < '1996-08-01' and exists (select * from lineitem where l_orderkey = o.o_orderkey and l_commitdate < l_receiptdate) group by o_orderpriority order by o_orderpriority;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string.replace("\n", "") == "Query projections has changed from ['*'] in the old query to ['count(*) as order_count', 'o_orderpriority'] in the new query.The node with node label 0 of type Seq Scan gets mapped to new node label 5 of type Seq Scan, alias has changed from orders into o and table filter has changed from None into ((o_orderdate >= '1996-05-01'::date) AND (o_orderdate < '1996-08-01'::date)).Index Scan (6,New) gets inserted before Nested Loop (4,New).Nested Loop (4,New) joins Seq Scan (5,New) and Index Scan (6,New) and gets inserted.Sort (3,New), Aggregate (2,New), Gather Merge (1,New) and Aggregate (0,New) gets inserted after Nested Loop (4,New)."
    ################################################################################################################################################################################
    old_query = "select o_orderpriority, count(*) as order_count from orders as o where o_orderdate >= '1996-05-01' and o_orderdate < '1996-08-01' and exists (select * from lineitem where l_orderkey = o.o_orderkey and l_commitdate < l_receiptdate) group by o_orderpriority order by o_orderpriority;"
    new_query = "select * from orders;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string.replace("\n", "") == "Query projections has changed from ['count(*) as order_count', 'o_orderpriority'] in the old query to ['*'] in the new query.The node with node label 5 of type Seq Scan gets mapped to new node label 0 of type Seq Scan, alias has changed from o into orders and table filter has changed from ((o_orderdate >= '1996-05-01'::date) AND (o_orderdate < '1996-08-01'::date)) into None.Index Scan (6,Old) that is before Nested Loop (4,Old) gets deleted.Nested Loop (4,Old), Sort (3,Old), Aggregate (2,Old), Gather Merge (1,Old) and Aggregate (0,Old) that is after Seq Scan (5,Old) gets deleted."
    ######################################################################################################################################################################################
    old_query = "select l_orderkey, sum(l_extendedprice * (1 - l_discount)) as revenue, o_orderdate, o_shippriority from orders, customer, lineitem where c_mktsegment = 'BUILDING' and c_custkey = o_custkey and l_orderkey = o_orderkey and o_orderdate < '1995-03-22' and l_shipdate > '1995-03-22' group by l_orderkey, o_orderdate, o_shippriority order by revenue desc, o_orderdate limit 10;"
    new_query = "select * from orders;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string.replace("\n", "") == "Query projections has changed from ['l_orderkey', 'o_orderdate', 'o_shippriority', 'sum(l_extendedprice * (1 - l_discount)) as revenue'] in the old query to ['*'] in the new query.The node with node label 9 of type Seq Scan gets mapped to new node label 0 of type Seq Scan and table filter has changed from (o_orderdate < '1995-03-22'::date) into None.Seq Scan (11,Old) and Hash (10,Old) that is before Hash Join (7,Old) gets deleted.Hash Join (7,Old) that is in between Seq Scan (9,Old) and Nested Loop (6,Old) gets deleted.Index Scan (8,Old) that is before Nested Loop (6,Old) gets deleted.Nested Loop (6,Old), Sort (5,Old), Aggregate (4,Old), Gather Merge (3,Old), Aggregate (2,Old), Sort (1,Old) and Limit (0,Old) that is after Hash Join (7,Old) gets deleted."
    ######################################################################################################################################################################################
def test_subplans_are_reflected_correctly():
    old_query = "select p_brand, p_type, p_size, count(distinct ps_suppkey) as supplier_cnt from partsupp, part where p_partkey = ps_partkey and p_brand <> 'Brand#34' and p_type not like 'ECONOMY BRUSHED%' and p_size in (22, 14, 27, 49, 21, 33, 35, 28) and partsupp.ps_suppkey not in ( select s_suppkey from supplier where s_comment like '%Customer%Complaints%') group by p_brand, p_type, p_size order by supplier_cnt desc, p_brand, p_type, p_size;"
    new_query = "select * from orders;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string.replace("\n", "") == "Query projections has changed from ['count(distinct ps_suppkey) as supplier_cnt', 'p_brand', 'p_size', 'p_type'] in the old query to ['*'] in the new query.The node with node label 7 of type Seq Scan gets mapped to new node label 0 of type Seq Scan, relation name supplier has changed into relation name orders, alias has changed from supplier into orders, table filter has changed from ((s_comment)::text ~~ '%Customer%Complaints%'::text) into None, subplan name has changed from SubPlan 1 into None and output name has changed from supplier into orders.Seq Scan (5,Old) that is in between Seq Scan (7,Old) and Hash Join (4,Old) gets deleted.Seq Scan (8,Old) and Hash (6,Old) that is before Hash Join (4,Old) gets deleted.Hash Join (4,Old), Gather (3,Old), Sort (2,Old), Aggregate (1,Old) and Sort (0,Old) that is after Seq Scan (5,Old) gets deleted."

def test_some_sample_queries_from_neuron():
    old_query = "select l_orderkey, sum(l_extendedprice * (1 - l_discount)) as revenue, o_orderdate, o_shippriority from orders, lineitem where l_orderkey = o_orderkey and o_orderdate < date '1995-03-21' and l_shipdate > date '1995-03-21' group by l_orderkey, o_orderdate, o_shippriority order by revenue desc, o_orderdate limit 10;"
    new_query = "select l_orderkey, sum(l_extendedprice * (1 - l_discount)) as revenue, o_orderdate, o_shippriority from customer, orders, lineitem where c_mktsegment = 'HOUSEHOLD' and c_custkey = o_custkey and l_orderkey = o_orderkey and o_orderdate < date '1995-03-21' and l_shipdate > date '1995-03-21' group by l_orderkey, o_orderdate, o_shippriority order by revenue desc, o_orderdate limit 10;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string.replace("\n", "") == "The node with node label 6 of type Hash Join gets mapped to new node label 7 of type Hash Join and hash condition has changed from (lineitem.l_orderkey = orders.o_orderkey) into (orders.o_custkey = customer.c_custkey).The node with node label 7 of type Seq Scan gets mapped to new node label 11 of type Seq Scan, relation name lineitem has changed into relation name customer, alias has changed from lineitem into customer, table filter has changed from (l_shipdate > '1995-03-21'::date) into (c_mktsegment = 'HOUSEHOLD'::bpchar) and output name has changed from lineitem into customer.The node with node label 8 of type Hash gets mapped to new node label 10 of type Hash.Index Scan (8,New) gets inserted before Nested Loop (6,New).Nested Loop (6,New) joins Hash Join (7,New) and Index Scan (8,New) and gets inserted."
    ####################################################################################################
    old_query = "select l_orderkey, sum(l_extendedprice * (1 - l_discount)) as revenue, o_orderdate, o_shippriority from customer, orders, lineitem where c_mktsegment = 'HOUSEHOLD' and c_custkey = o_custkey and l_orderkey = o_orderkey and o_orderdate < date '1995-03-21' and l_shipdate > date '1995-03-21' group by l_orderkey, o_orderdate, o_shippriority order by revenue desc, o_orderdate limit 10;"
    new_query = "select l_orderkey, sum(l_extendedprice * (1 - l_discount)) as revenue, o_orderdate, o_shippriority from orders, lineitem where l_orderkey = o_orderkey and o_orderdate < date '1995-03-21' and l_shipdate > date '1995-03-21' group by l_orderkey, o_orderdate, o_shippriority order by revenue desc, o_orderdate limit 10;"
    old_query_plan, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    new_query_plan, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)
    assert success_1 == True
    assert success_2 == True
    natural_language_string = find_difference_between_two_query_plans(old_query, old_query_plan, new_query, new_query_plan)
    assert natural_language_string.replace("\n", "") == "The node with node label 7 of type Hash Join gets mapped to new node label 6 of type Hash Join and hash condition has changed from (orders.o_custkey = customer.c_custkey) into (lineitem.l_orderkey = orders.o_orderkey).The node with node label 10 of type Hash gets mapped to new node label 8 of type Hash.The node with node label 11 of type Seq Scan gets mapped to new node label 7 of type Seq Scan, relation name customer has changed into relation name lineitem, alias has changed from customer into lineitem, table filter has changed from (c_mktsegment = 'HOUSEHOLD'::bpchar) into (l_shipdate > '1995-03-21'::date) and output name has changed from customer into lineitem.Index Scan (8,Old) that is before Nested Loop (6,Old) gets deleted.Nested Loop (6,Old) that is in between Hash Join (7,Old) and Sort (5,Old) gets deleted."
