import azure.functions as func
import logging
from repositories.source_repository import SourceRepository
from repositories.target_repository import TargetRepository

app = func.Blueprint()


@app.timer_trigger(schedule="0 0 6 * * *", arg_name="timer", run_on_startup=False)
def extract_estoque_movimentacao(timer: func.TimerRequest) -> None:
    logging.info("extract_estoque_movimentacao iniciado.")

    source_repo = SourceRepository()
    target_repo = TargetRepository()

    try:
        records = source_repo.fetch_all("SELECT * FROM erp.estoque_movimentacao")
        logging.info(f"{len(records)} registros encontrados em erp.estoque_movimentacao")

        affected = target_repo.upsert_records(
            table="erp.estoque_movimentacao",
            key_column="id_estoque_movimentacao",
            records=records
        )
        logging.info(f"{affected} registros processados no target")

    except Exception as e:
        logging.error(f"Erro ao processar erp.estoque_movimentacao: {str(e)}")
        raise

    logging.info("extract_estoque_movimentacao finalizado.")