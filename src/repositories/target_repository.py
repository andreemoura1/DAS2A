from shared.config import get_connection_string
import pyodbc


class TargetRepository:
    def __init__(self):
        self.conn_str = get_connection_string()

    def upsert_records(self, table: str, key_column: str, records: list[dict]) -> int:
        if not records:
            return 0

        columns = list(records[0].keys())
        col_list = ", ".join(columns)
        param_list = ", ".join(["?" for _ in columns])
        update_set = ", ".join(
            [f"target.{col} = source.{col}" for col in columns if col != key_column]
        )
        insert_cols = ", ".join([f"source.{col}" for col in columns])

        merge_sql = (
            f"MERGE INTO {table} AS target "
            f"USING (VALUES ({param_list})) AS source ({col_list}) "
            f"ON target.{key_column} = source.{key_column} "
            f"WHEN MATCHED THEN UPDATE SET {update_set} "
            f"WHEN NOT MATCHED THEN INSERT ({col_list}) VALUES ({insert_cols});"
        )

        total_affected = 0
        with pyodbc.connect(self.conn_str) as conn:
            cursor = conn.cursor()
            for record in records:
                values = [record[col] for col in columns]
                cursor.execute(merge_sql, values)
                total_affected += cursor.rowcount
            conn.commit()

        return total_affected