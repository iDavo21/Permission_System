import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DB_DIR, exist_ok=True)


def get_db_path(db_name: str) -> str:
    return os.path.join(DB_DIR, db_name)


def _create_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


class db_connection:
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._conn = None

    def __enter__(self):
        self._conn = _create_connection(self._db_path)
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            self._conn.close()
        return False


def get_connection(db_name: str) -> sqlite3.Connection:
    return _create_connection(get_db_path(db_name))


def connect(db_name: str):
    return db_connection(get_db_path(db_name))