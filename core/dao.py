import sqlite3
from core.database import get_connection, get_db_path


class BaseDAO:
    DB_NAME = None
    TABLE_NAME = None
    JOIN_TABLES = {}

    @classmethod
    def _connect(cls):
        return get_connection(cls.DB_NAME)

    @classmethod
    def create_table(cls, schema: str):
        conn = cls._connect()
        try:
            conn.execute(f"CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} ({schema})")
            conn.commit()
        finally:
            conn.close()

    @classmethod
    def _attach_joins(cls, conn):
        for alias, db_table in cls.JOIN_TABLES.items():
            db_path = get_db_path(db_table)
            conn.execute(f"ATTACH DATABASE '{db_path}' AS {alias}")

    @classmethod
    def save(cls, datos: dict, columns: list) -> int:
        conn = cls._connect()
        try:
            placeholders = ", ".join([f":{col}" for col in columns])
            cols = ", ".join(columns)
            query = f"INSERT INTO {cls.TABLE_NAME} ({cols}) VALUES ({placeholders})"
            cursor = conn.execute(query, datos)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @classmethod
    def get_all(cls, select_cols: str = "*", join: bool = False) -> list:
        conn = cls._connect()
        try:
            if join:
                cls._attach_joins(conn)
            rows = conn.execute(f"SELECT {select_cols} FROM {cls.TABLE_NAME} ORDER BY id DESC").fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @classmethod
    def get_by_id(cls, record_id: int, select_cols: str = "*", join: bool = False) -> dict:
        conn = cls._connect()
        try:
            if join:
                cls._attach_joins(conn)
            row = conn.execute(f"SELECT {select_cols} FROM {cls.TABLE_NAME} WHERE id = ?", (record_id,)).fetchone()
            return dict(row) if row else {}
        finally:
            conn.close()

    @classmethod
    def update(cls, record_id: int, datos: dict, set_cols: list):
        datos['id'] = record_id
        set_clause = ", ".join([f"{col} = :{col}" for col in set_cols])
        conn = cls._connect()
        try:
            conn.execute(f"UPDATE {cls.TABLE_NAME} SET {set_clause} WHERE id = :id", datos)
            conn.commit()
        finally:
            conn.close()

    @classmethod
    def delete(cls, record_id: int):
        conn = cls._connect()
        try:
            conn.execute(f"DELETE FROM {cls.TABLE_NAME} WHERE id = ?", (record_id,))
            conn.commit()
        finally:
            conn.close()

    @classmethod
    def existe_duplicado(cls, datos: dict, where_cols: list, exclude_id: int = None) -> bool:
        conditions = " AND ".join([f"{col} = :{col}" for col in where_cols])
        if exclude_id:
            conditions += f" AND id != :excluir_id"
            datos["excluir_id"] = exclude_id
        
        conn = cls._connect()
        try:
            count = conn.execute(
                f"SELECT COUNT(*) FROM {cls.TABLE_NAME} WHERE {conditions}",
                datos
            ).fetchone()[0]
            return count > 0
        finally:
            conn.close()

    @classmethod
    def search(cls, term: str, search_cols: list) -> list:
        term = f"%{term}%"
        conditions = " OR ".join([f"{col} LIKE :term" for col in search_cols])
        params = {"term": term}
        
        conn = cls._connect()
        try:
            rows = conn.execute(
                f"SELECT * FROM {cls.TABLE_NAME} WHERE {conditions}",
                params
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @classmethod
    def count(cls) -> int:
        conn = cls._connect()
        try:
            row = conn.execute(f"SELECT COUNT(*) FROM {cls.TABLE_NAME}").fetchone()
            return row[0] if row else 0
        finally:
            conn.close()