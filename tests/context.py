import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.qt_parser.find_difference import find_difference_between_two_query_plans
from src.postgres_interface.postgres_wrapper import PostgresWrapper