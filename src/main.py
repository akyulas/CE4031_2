from postgres_interface.postgres_wrapper import PostgresWrapper
from parser.find_difference import find_difference_between_two_query_plans

postgres_wrapper = PostgresWrapper()
postgres_wrapper_2 = PostgresWrapper()
conn = postgres_wrapper.connect_to_postgres_db("localhost", "TPC-H", "postgres", "password", port=5433)
new_query = "select * from orders;"
old_query = "select o_orderpriority, count(*) as order_count from orders as o where o_orderdate >= '1996-05-01' and o_orderdate < '1996-08-01' and exists (select * from lineitem where l_orderkey = o.o_orderkey and l_commitdate < l_receiptdate) group by o_orderpriority order by o_orderpriority;"
result_1, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
result_2, success_2 = postgres_wrapper_2.get_query_plan_of_query(new_query)

if success_1 and success_2:
    print(find_difference_between_two_query_plans(old_query, result_1, new_query, result_2))
