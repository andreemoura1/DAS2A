import azure.functions as func
import logging
from repositories.source_repository import SourceRepository
from repositories.target_repository import TargetRepository

app = func.Blueprint()


@app.timer_trigger(schedule="0 0 6 * * *", arg_name="timer", run_on_startup=False)
def extract_pedido_item(timer: func.TimerRequest) -> None:
    logging.info("extract_pedido_item iniciado.")

    source_repo = SourceRepository()
    target_repo = TargetRepository()

    try:
        records = source_repo.fetch_all("SELECT * FROM erp.pedido_item")
        logging.info(f"{len(records)} registros encontrados em erp.pedido_item")

        affected = target_repo.upsert_records(
            table="erp.pedido_item",
            key_column="id_pedido_item",
            records=records
        )
        logging.info(f"{affected} registros processados no target")

    except Exception as e:
        logging.error(f"Erro ao processar erp.pedido_item: {str(e)}")
        raise

    logging.info("extract_pedido_item finalizado.")
