import sqlite3
import time
import random
import string
from datetime import date, timedelta

from sqlalchemy import create_engine, text

DB_PATH = "poc_vendamais.db"
TABLE = "cliente"
NUM_RECORDS = 2000
NUM_RUNS = 2


def _gerar_string(n: int) -> str:
    return "".join(random.choices(string.ascii_letters, k=n))


def setup_database() -> None:
    conn = sqlite3.connect(DB_PATH)
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


def bench_sqlite3() -> tuple[list[float], int]:
    times = []
    n_rows = 0
    for _ in range(NUM_RUNS):
        start = time.perf_counter()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {TABLE}")
        rows = cursor.fetchall()
        conn.close()
        times.append(time.perf_counter() - start)
        n_rows = len(rows)
    return times, n_rows


def bench_sqlalchemy() -> tuple[list[float], int]:
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
    times = []
    n_rows = 0
    for _ in range(NUM_RUNS):
        start = time.perf_counter()
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {TABLE}"))
            rows = result.fetchall()
        times.append(time.perf_counter() - start)
        n_rows = len(rows)
    engine.dispose()
    return times, n_rows


def main() -> None:
    print(f"\nConfigurando banco de dados com {NUM_RECORDS} registros na tabela '{TABLE}'...")
    setup_database()
    print("Banco configurado.\n")

    sqlite3_times, n_rows = bench_sqlite3()
    sa_times, _ = bench_sqlalchemy()

    sqlite3_avg = sum(sqlite3_times) / NUM_RUNS
    sa_avg = sum(sa_times) / NUM_RUNS

    faster = "sqlite3 (nativo)" if sqlite3_avg < sa_avg else "SQLAlchemy"
    slower_avg = max(sqlite3_avg, sa_avg)
    faster_avg = min(sqlite3_avg, sa_avg)
    diff_pct = (slower_avg - faster_avg) / slower_avg * 100

    header = f"BENCHMARK — SELECT * FROM {TABLE} | {NUM_RECORDS} registros | {NUM_RUNS} execuções"
    sep = "=" * len(header)

    print(sep)
    print(header)
    print(sep)
    print(f"\n{'Biblioteca':<22} {'Exec 1':>12} {'Exec 2':>12} {'Média':>12}")
    print("-" * 60)
    print(
        f"{'sqlite3 (nativo)':<22}"
        f" {sqlite3_times[0]:>11.6f}s"
        f" {sqlite3_times[1]:>11.6f}s"
        f" {sqlite3_avg:>11.6f}s"
    )
    print(
        f"{'SQLAlchemy 2.x':<22}"
        f" {sa_times[0]:>11.6f}s"
        f" {sa_times[1]:>11.6f}s"
        f" {sa_avg:>11.6f}s"
    )
    print("-" * 60)
    print(f"\nVencedor: {faster}  ({diff_pct:.0f}% mais rápido)\n")

    print("RESULTS_JSON")
    import json
    print(json.dumps({
        "sqlite3_exec1": round(sqlite3_times[0], 6),
        "sqlite3_exec2": round(sqlite3_times[1], 6),
        "sqlite3_avg":   round(sqlite3_avg, 6),
        "sa_exec1":      round(sa_times[0], 6),
        "sa_exec2":      round(sa_times[1], 6),
        "sa_avg":        round(sa_avg, 6),
        "winner":        faster,
        "diff_pct":      round(diff_pct, 1),
        "num_records":   n_rows,
    }))


if __name__ == "__main__":
    main()
