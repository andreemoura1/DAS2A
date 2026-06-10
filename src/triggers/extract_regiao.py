import azure.functions as func
import logging
from repositories.source_repository import SourceRepository
from repositories.target_repository import TargetRepository

app = func.Blueprint()


@app.timer_trigger(schedule="0 0 6 * * *", arg_name="timer", run_on_startup=False)
def extract_regiao(timer: func.TimerRequest) -> None:
    logging.info("extract_regiao iniciado.")

    source_repo = SourceRepository()
    target_repo = TargetRepository()

    try:
        records = source_repo.fetch_all("SELECT * FROM erp.regiao")
        logging.info(f"{len(records)} registros encontrados em erp.regiao")

        affected = target_repo.upsert_records(
            table="erp.regiao",
            key_column="id_regiao",
            records=records
        )
        logging.info(f"{affected} registros processados no target")

    except Exception as e:
        logging.error(f"Erro ao processar erp.regiao: {str(e)}")
        raise

    logging.info("extract_regiao finalizado.")