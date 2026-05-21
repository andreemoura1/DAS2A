import azure.functions as func
import logging
import os

app = func.Blueprint()

@app.timer_trigger(schedule="0 0 6 * * *", arg_name="timer", run_on_startup=False)
def extract_representante(timer: func.TimerRequest) -> None:

    sql_server = os.getenv("SQL_SERVER_SOURCE")
    sql_database = os.getenv("SQL_DATABASE_SOURCE")
    sql_user = os.getenv("SQL_USER_SOURCE")
    sql_pass = os.getenv("SQL_PASSWORD_SOURCE")

 	logging.info(f"servidor: {sql_server},  banco: {sql_database}, usuario:{sql_user}, senha: {sql_pass} ...")   
    """
    Trigger de extração agendada (diária às 06:00 UTC).
    Apenas delega para o orchestrator — sem lógica de negócio aqui.
    """
    logging.info("extract_representante iniciado.")
    logging.info("extract_representante finalizado.")
