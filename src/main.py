from postgres_interface.postgres_wrapper import PostgresWrapper
from parser.find_difference import find_difference_between_two_query_plans

postgres_wrapper = PostgresWrapper()
postgres_wrapper_2 = PostgresWrapper()
conn = postgres_wrapper.connect_to_postgres_db("localhost", "TPC-H", "postgres", "password", port=5433)
old_query = "select * from customer;"
new_query = "select (c_nationkey, c_name) from customer;"
# result_1, success_1 = postgres_wrapper.get_query_plan_of_query("select c_nationkey from customer where c_nationkey > 0 group by c_nationkey;")
# result_2, success_2 = postgres_wrapper_2.get_query_plan_of_query("select c_nationkey from customer group by c_nationkey;")
result_1, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
result_2, success_2 = postgres_wrapper_2.get_query_plan_of_query(new_query)
print(result_1)
print(result_2)

if success_1 and success_2:
    print(find_difference_between_two_query_plans(old_query, result_1, new_query, result_2))
