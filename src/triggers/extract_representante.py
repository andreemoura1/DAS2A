import azure.functions as func
import logging
from repositories.source_repository import SourceRepository
from repositories.target_repository import TargetRepository

app = func.Blueprint()


@app.timer_trigger(schedule="0 0 6 * * *", arg_name="timer", run_on_startup=False)
def extract_representante(timer: func.TimerRequest) -> None:
    logging.info("extract_representante iniciado.")

    source_repo = SourceRepository()
    target_repo = TargetRepository()

    try:
        records = source_repo.fetch_all("SELECT * FROM erp.representante")
        logging.info(f"{len(records)} registros encontrados em erp.representante")

        affected = target_repo.upsert_records(
            table="erp.representante",
            key_column="id_representante",
            records=records
        )
        logging.info(f"{affected} registros processados no target")

    except Exception as e:
        logging.error(f"Erro ao processar erp.representante: {str(e)}")
        raise

    logging.info("extract_representante finalizado.")