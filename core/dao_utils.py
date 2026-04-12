import sqlite3
from typing import Any, Optional
from functools import wraps


def with_connection(db_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from core.database import get_connection
            conn = get_connection(db_name)
            try:
                return func(conn, *args, **kwargs)
            finally:
                conn.close()
        return wrapper
    return decorator


def _dict_from_row(row: Optional[sqlite3.Row]) -> dict:
    return dict(row) if row else {}


def _dicts_from_rows(rows: list) -> list:
    return [dict(r) for r in rows]


def build_where(columns: list, exclude_id: int = None) -> tuple:
    conditions = " AND ".join([f"{col} = :{col}" for col in columns])
    params = {}
    if exclude_id:
        conditions += f" AND id != :excluir_id"
        params["excluir_id"] = exclude_id
    return conditions, params


def build_set_clause(columns: list) -> list:
    return [f"{col} = :{col}" for col in columns]


def build_insert(columns: list) -> tuple:
    cols = ", ".join(columns)
    placeholders = ", ".join([f":{col}" for col in columns])
    return cols, placeholders