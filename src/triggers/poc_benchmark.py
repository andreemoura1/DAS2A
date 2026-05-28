import sqlite3
import time
import random
import string
import json
import logging
import os
import tempfile
from datetime import date, timedelta

import azure.functions as func
from sqlalchemy import create_engine, text

app = func.Blueprint()

TABLE = "cliente"
NUM_RECORDS = 2000
NUM_RUNS = 2


def _gerar_string(n: int) -> str:
    return "".join(random.choices(string.ascii_letters, k=n))


def _setup_database(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE} (
            id               INTEGER PRIMARY KEY,
            nome             TEXT,
            email            TEXT,
            cpf              TEXT,
            cidade           TEXT,
            estado           TEXT,
            data_cadastro    TEXT
        )
    """)
    cursor.execute(f"DELETE FROM {TABLE}")

    base_date = date(2020, 1, 1)
    estados = ["SP", "RJ", "MG", "RS", "PR", "BA", "SC", "GO"]
    records = [
        (
            i,
            _gerar_string(20),
            f"cliente{i}@vendamais.com",
            f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}",
            _gerar_string(10),
            random.choice(estados),
            str(base_date + timedelta(days=random.randint(0, 1825))),
        )
        for i in range(1, NUM_RECORDS + 1)
    ]
    cursor.executemany(f"INSERT INTO {TABLE} VALUES (?,?,?,?,?,?,?)", records)
    conn.commit()
    conn.close()


def _bench_sqlite3(db_path: str) -> list[float]:
    times = []
    for _ in range(NUM_RUNS):
        start = time.perf_counter()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {TABLE}")
        cursor.fetchall()
        conn.close()
        times.append(time.perf_counter() - start)
    return times


def _bench_sqlalchemy(db_path: str) -> list[float]:
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    times = []
    for _ in range(NUM_RUNS):
        start = time.perf_counter()
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {TABLE}"))
            result.fetchall()
        times.append(time.perf_counter() - start)
    engine.dispose()
    return times


@app.route(route="poc-benchmark", methods=["GET"])
def poc_benchmark(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("poc_benchmark iniciado.")

    db_path = os.path.join(tempfile.gettempdir(), "poc_vendamais.db")

    try:
        _setup_database(db_path)

        sqlite3_times = _bench_sqlite3(db_path)
        sa_times = _bench_sqlalchemy(db_path)

        sqlite3_avg = sum(sqlite3_times) / NUM_RUNS
        sa_avg = sum(sa_times) / NUM_RUNS

        faster_avg = min(sqlite3_avg, sa_avg)
        slower_avg = max(sqlite3_avg, sa_avg)
        diff_pct = round((slower_avg - faster_avg) / slower_avg * 100, 1)
        winner = "sqlite3 (nativo)" if sqlite3_avg < sa_avg else "SQLAlchemy"

        payload = {
            "tabela": TABLE,
            "registros": NUM_RECORDS,
            "execucoes_por_biblioteca": NUM_RUNS,
            "sqlite3": {
                "exec_1_s": round(sqlite3_times[0], 6),
                "exec_2_s": round(sqlite3_times[1], 6),
                "media_s": round(sqlite3_avg, 6),
            },
            "sqlalchemy": {
                "exec_1_s": round(sa_times[0], 6),
                "exec_2_s": round(sa_times[1], 6),
                "media_s": round(sa_avg, 6),
            },
            "vencedor": winner,
            "diferenca_percentual": f"{diff_pct}%",
        }

        logging.info("poc_benchmark finalizado. Vencedor: %s (%s%% mais rápido)", winner, diff_pct)
        return func.HttpResponse(
            json.dumps(payload, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=200,
        )

    except Exception as exc:
        logging.error("Erro no poc_benchmark: %s", str(exc))
        return func.HttpResponse(
            json.dumps({"erro": str(exc)}),
            mimetype="application/json",
            status_code=500,
        )
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
