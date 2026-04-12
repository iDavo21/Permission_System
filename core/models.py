import sqlite3
import os
from functools import lru_cache
from contextlib import contextmanager


class BaseModelMixin:
    _DB_PATH = None
    
    @classmethod
    def get_db_path(cls, db_name: str) -> str:
        if cls._DB_PATH:
            return cls._DB_PATH
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'data', db_name)

    @classmethod
    def _connect(cls):
        if cls._DB_PATH:
            conn = sqlite3.connect(cls._DB_PATH)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            return conn
        return None

    @classmethod
    def _get_single(cls, query: str, params: tuple = None):
        conn = cls._connect()
        try:
            if params:
                row = conn.execute(query, params).fetchone()
            else:
                row = conn.execute(query).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @classmethod
    def _get_all(cls, query: str, params: tuple = None):
        conn = cls._connect()
        try:
            if params:
                rows = conn.execute(query, params).fetchall()
            else:
                rows = conn.execute(query).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @classmethod
    def _execute(cls, query: str, params: dict = None, return_id: bool = False):
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

    @classmethod
    def _count(cls, query: str, params: tuple = None) -> int:
        conn = cls._connect()
        try:
            if params:
                row = conn.execute(query, params).fetchone()
            else:
                row = conn.execute(query).fetchone()
            return row[0] if row else 0
        finally:
            conn.close()


class BaseModel:
    DB_PATH = None
    _connections_cache = {}

    @classmethod
    def get_db_path(cls, db_name: str) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'data', db_name)

    @classmethod
    def _get_connection(cls):
        if cls.DB_PATH not in cls._connections_cache:
            conn = sqlite3.connect(cls.DB_PATH)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            cls._connections_cache[cls.DB_PATH] = conn
        return cls._connections_cache[cls.DB_PATH]

    @classmethod
    @contextmanager
    def _transaction(cls):
        conn = cls._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    @classmethod
    def execute_query(cls, query: str, params: tuple = None, fetch: str = "all"):
        conn = cls._get_connection()
        try:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            
            if fetch == "one":
                row = cursor.fetchone()
                return dict(row) if row else None
            elif fetch == "scalar":
                result = cursor.fetchone()
                return result[0] if result else None
            else:
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            raise

    @classmethod
    def execute_update(cls, query: str, params: dict = None, return_id: bool = False):
        with cls._transaction() as conn:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            return cursor.lastrowid if return_id else True

    @classmethod
    def close_all_connections(cls):
        for conn in cls._connections_cache.values():
            conn.close()
        cls._connections_cache.clear()


def get_db_path(db_name: str) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'data', db_name)