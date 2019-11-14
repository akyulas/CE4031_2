import psycopg2
import json
try:
    from utils.singleton import Singleton
except:
    from src.utils.singleton import Singleton

class PostgresWrapper(metaclass=Singleton):
    """
    Define an object used to wrap around postgres
    """
    
    def connect_to_postgres_db(self, host, dbname, user, password, port=5432):
        """
        This function is used to connect to postgres db.
        """
        try:
            conn = psycopg2.connect(
                host = host,
                dbname = dbname,
                user = user,
                password = password,
                port = port
            )
            self.conn = conn
            return conn, True
        except Exception as e:
            return str(e), False
    
    def get_query_plan_of_query(self, query):
        """
        This function is used to get query plan of a query from postgres db.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("explain (format json) " + query)
            result = cursor.fetchall()[0][0][0]['Plan']
            cursor.close()
            return result, True
        except Exception as e:
            self.conn.rollback()
            return str(e), False



