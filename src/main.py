from postgres_interface.postgres_wrapper import PostgresWrapper
from parser.find_difference import find_difference_between_two_query_plans

postgres_wrapper = PostgresWrapper()
postgres_wrapper_2 = PostgresWrapper()
conn = postgres_wrapper.connect_to_postgres_db("localhost", "TPC-H", "postgres", "password", port=5433)
result_1, success_1 = postgres_wrapper.get_query_plan_of_query("select * from customer;")
result_2, success_2 = postgres_wrapper_2.get_query_plan_of_query("select * from nation;")

if success_1 and success_2:
    find_difference_between_two_query_plans(result_1, result_2)
