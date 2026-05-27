import azure.functions as func
import logging
import os
import pyodbc

app = func.Blueprint()


@app.timer_trigger(schedule="0 0 6 * * *", arg_name="timer", run_on_startup=False)
def extract_estoque_movimentacao(timer: func.TimerRequest) -> None:

    sql_server = os.getenv("SQL_SERVER_SOURCE")
    sql_database = os.getenv("SQL_DATABASE_SOURCE")
    sql_user = os.getenv("SQL_USER_SOURCE")
    sql_pass = os.getenv("SQL_PASSWORD_SOURCE")

    logging.info("extract_estoque_movimentacao iniciado.")

    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={sql_server};"
        f"DATABASE={sql_database};"
        f"UID={sql_user};"
        f"PWD={sql_pass};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM erp.estoque_movimentacao"
            cursor.execute(query)
            rows = cursor.fetchall()
            logging.info(rows)

    except Exception as e:
        logging.error(f"Erro ao ler erp.estoque_movimentacao: {str(e)}")
        raise

    logging.info("extract_estoque_movimentacao finalizado.")