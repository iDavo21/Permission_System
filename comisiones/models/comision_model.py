import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'comisiones.db')


class ComisionModel:
    @staticmethod
    def _connect():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @staticmethod
    def create_table():
        conn = ComisionModel._connect()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS comisiones (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    personal_id       INTEGER NOT NULL,
                    tipo_comision     TEXT,
                    destino           TEXT,
                    fecha_elaboracion TEXT,
                    fecha_desde       TEXT,
                    fecha_hasta       TEXT,
                    observaciones     TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_personal ON comisiones(personal_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fecha_hasta ON comisiones(fecha_hasta)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fecha_desde ON comisiones(fecha_desde)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tipo ON comisiones(tipo_comision)")
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def save(datos: dict) -> int:
        conn = ComisionModel._connect()
        try:
            cursor = conn.execute("""
                INSERT INTO comisiones (
                    personal_id, tipo_comision, destino,
                    fecha_elaboracion, fecha_desde, fecha_hasta, observaciones
                ) VALUES (
                    :personal_id, :tipo_comision, :destino,
                    :fecha_elaboracion, :fecha_desde, :fecha_hasta, :observaciones
                )
            """, datos)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def _get_personal_info(personal_id):
        from personal.models.personal_model import PersonalModel
        return PersonalModel.get_by_id(personal_id)

    @staticmethod
    def _enrich_row(row_dict):
        personal = ComisionModel._get_personal_info(row_dict.get("personal_id"))
        if personal:
            row_dict.update({
                "nombres": personal.get("nombres", ""),
                "apellidos": personal.get("apellidos", ""),
                "cedula": personal.get("cedula", ""),
                "telefono": personal.get("telefono", ""),
                "grado_jerarquia": personal.get("grado_jerarquia", ""),
                "cargo": personal.get("cargo", ""),
                "dir_domiciliaria": personal.get("dir_domiciliaria", ""),
                "dir_emergencia": personal.get("dir_emergencia", ""),
            })
        return row_dict

    @staticmethod
    def get_all() -> list:
        conn = ComisionModel._connect()
        try:
            rows = conn.execute("""
                SELECT * FROM comisiones ORDER BY id DESC
            """).fetchall()
            result = [ComisionModel._enrich_row(dict(r)) for r in rows]
            return result
        finally:
            conn.close()

    @staticmethod
    def get_by_id(comision_id: int) -> dict:
        conn = ComisionModel._connect()
        try:
            row = conn.execute(
                "SELECT * FROM comisiones WHERE id = ?", (comision_id,)
            ).fetchone()
            if row:
                return ComisionModel._enrich_row(dict(row))
            return {}
        finally:
            conn.close()

    @staticmethod
    def get_by_personal_id(personal_id: int) -> list:
        conn = ComisionModel._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM comisiones WHERE personal_id = ? ORDER BY id DESC",
                (personal_id,),
            ).fetchall()
            result = [ComisionModel._enrich_row(dict(r)) for r in rows]
            return result
        finally:
            conn.close()

    @staticmethod
    def update(comision_id: int, datos: dict):
        datos['id'] = comision_id
        conn = ComisionModel._connect()
        try:
            conn.execute("""
                UPDATE comisiones SET
                    personal_id       = :personal_id,
                    tipo_comision     = :tipo_comision,
                    destino           = :destino,
                    fecha_elaboracion = :fecha_elaboracion,
                    fecha_desde       = :fecha_desde,
                    fecha_hasta       = :fecha_hasta,
                    observaciones     = :observaciones
                WHERE id = :id
            """, datos)
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def delete(comision_id: int):
        conn = ComisionModel._connect()
        try:
            conn.execute("DELETE FROM comisiones WHERE id = ?", (comision_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def delete_by_personal_id(personal_id: int):
        conn = ComisionModel._connect()
        try:
            conn.execute("DELETE FROM comisiones WHERE personal_id = ?", (personal_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def existe_duplicado(datos: dict, excluir_id=None) -> bool:
        conn = ComisionModel._connect()
        try:
            query = """
                SELECT COUNT(*) FROM comisiones 
                WHERE personal_id = :personal_id 
                  AND tipo_comision = :tipo_comision 
                  AND fecha_desde = :fecha_desde 
                  AND fecha_hasta = :fecha_hasta
            """
            parametros = {
                "personal_id": datos.get("personal_id"),
                "tipo_comision": datos.get("tipo_comision"),
                "fecha_desde": datos.get("fecha_desde"),
                "fecha_hasta": datos.get("fecha_hasta")
            }
            if excluir_id:
                query += " AND id != :excluir_id"
                parametros["excluir_id"] = excluir_id
            
            count = conn.execute(query, parametros).fetchone()[0]
            return count > 0
        finally:
            conn.close()
