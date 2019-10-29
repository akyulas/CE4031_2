from postgres_interface.postgres_wrapper import PostgresWrapper
from parser.find_difference import find_difference_between_two_query_plans

postgres_wrapper = PostgresWrapper()
postgres_wrapper_2 = PostgresWrapper()
conn = postgres_wrapper.connect_to_postgres_db("localhost", "TPC-H", "postgres", "password", port=5433)
old_query = "select * from lineitem;"
new_query = "select l_returnflag, l_linestatus,sum(l_quantity) as sum_qty, sum(l_extendedprice) as sum_base_price, sum(l_extendedprice * (1 - l_discount)) as sum_disc_price, sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge, avg(l_quantity) as avg_qty, avg(l_extendedprice) as avg_price, avg(l_discount) as avg_disc, count(*) as count_order from lineitem where l_shipdate <= '1998-09-16' group by l_returnflag, l_linestatus order by l_returnflag, l_linestatus;"
# result_1, success_1 = postgres_wrapper.get_query_plan_of_query("select c_nationkey from customer where c_nationkey > 0 group by c_nationkey;")
# result_2, success_2 = postgres_wrapper_2.get_query_plan_of_query("select c_nationkey from customer group by c_nationkey;")
result_1, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
result_2, success_2 = postgres_wrapper_2.get_query_plan_of_query(new_query)

if success_1 and success_2:
    print(find_difference_between_two_query_plans(old_query, result_1, new_query, result_2))
