from postgres_interface.postgres_wrapper import PostgresWrapper
from parser.find_difference import find_difference_between_two_query_plans

postgres_wrapper = PostgresWrapper()
postgres_wrapper_2 = PostgresWrapper()
conn = postgres_wrapper.connect_to_postgres_db("localhost", "TPC-H", "postgres", "root", port=5432)
new_query = "select c_custkey, c_name, sum(l_extendedprice * (1 - l_discount)) as revenue, c_acctbal, c_address, c_phone, c_comment from customer, orders, lineitem where c_custkey = o_custkey and l_orderkey = o_orderkey and o_orderdate >= '1993-07-01' and o_orderdate < '1993-10-01' and l_returnflag = 'R' group by c_custkey, c_name, c_acctbal, c_phone, c_address, c_comment order by revenue desc limit 20;"
old_query = "select c_custkey, c_name, sum(l_extendedprice * (1 - l_discount)) as revenue, c_acctbal, n_name, c_address, c_phone, c_comment from customer, orders, lineitem, nation where c_custkey = o_custkey and l_orderkey = o_orderkey and o_orderdate >= '1993-07-01' and o_orderdate < '1993-10-01' and l_returnflag = 'R' and c_nationkey = n_nationkey group by c_custkey, c_name, c_acctbal, c_phone, n_name, c_address, c_comment order by revenue desc limit 20;"

result_1, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
result_2, success_2 = postgres_wrapper_2.get_query_plan_of_query(new_query)
if success_1 and success_2:
    print(find_difference_between_two_query_plans(old_query, result_1, new_query, result_2))
