import os

def get_connection_string() -> str:
    conn = os.getenv("SQL_CONNECTION_STRING")
    if not conn:
        raise EnvironmentError("SQL_CONNECTION_STRING não configurada.")
    return conn

def get_storage_account_url() -> str:
    url = os.getenv("STORAGE_ACCOUNT_URL")
    if not url:
        raise EnvironmentError("STORAGE_ACCOUNT_URL não configurada.")
    return url