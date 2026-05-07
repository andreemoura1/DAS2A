from shared.config import get_connection_string
import pyodbc

class TargetRepository:
    def __init__(self):
        self.conn_str = get_connection_string()

    def upsert_records(self, records: list[dict]) -> int:
        with pyodbc.connect(self.conn_str) as conn:
            cursor = conn.cursor()
            # lógica de upsert
            return cursor.rowcount