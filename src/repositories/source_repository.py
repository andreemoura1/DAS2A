import pyodbc
import os


class SourceRepository:
    def __init__(self):
        sql_server = os.getenv("SQL_SERVER_SOURCE")
        sql_database = os.getenv("SQL_DATABASE_SOURCE")
        sql_user = os.getenv("SQL_USER_SOURCE")
        sql_pass = os.getenv("SQL_PASSWORD_SOURCE")

        self.conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={sql_server};"
            f"DATABASE={sql_database};"
            f"UID={sql_user};"
            f"PWD={sql_pass};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )

    def fetch_all(self, query: str) -> list[dict]:
        with pyodbc.connect(self.conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]