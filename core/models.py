import sqlite3
import os


class BaseModel:
    DB_PATH = None
    
    @classmethod
    def _connect(cls):
        conn = sqlite3.connect(cls.DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn
    
    @classmethod
    def _execute_query(cls, query: str, params: tuple = None, fetch: str = "all"):
        conn = cls._connect()
        try:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            
            if fetch == "one":
                row = cursor.fetchone()
                return dict(row) if row else None
            elif fetch == "scalar":
                return cursor.fetchone()[0] if cursor.fetchone() else None
            else:
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
        finally:
            conn.close()
    
    @classmethod
    def _execute_update(cls, query: str, params: dict = None, return_id: bool = False):
        conn = cls._connect()
        try:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            conn.commit()
            return cursor.lastrowid if return_id else True
        finally:
            conn.close()


def get_db_path(db_name: str) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'data', db_name)