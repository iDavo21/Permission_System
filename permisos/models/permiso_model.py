import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'permisos.db')


class PermisoModel:
    @staticmethod
    def _connect():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @staticmethod
    def create_table():
        conn = PermisoModel._connect()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS permisos (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    personal_id       INTEGER NOT NULL,
                    tipo_permiso      TEXT,
                    fecha_elaboracion TEXT,
                    fecha_desde       TEXT,
                    fecha_hasta       TEXT,
                    observaciones     TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_personal ON permisos(personal_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fecha_hasta ON permisos(fecha_hasta)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fecha_desde ON permisos(fecha_desde)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tipo ON permisos(tipo_permiso)")
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def save(datos: dict) -> int:
        conn = PermisoModel._connect()
        try:
            cursor = conn.execute("""
                INSERT INTO permisos (
                    personal_id, tipo_permiso,
                    fecha_elaboracion, fecha_desde, fecha_hasta, observaciones
                ) VALUES (
                    :personal_id, :tipo_permiso,
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
        personal = PermisoModel._get_personal_info(row_dict.get("personal_id"))
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
        conn = PermisoModel._connect()
        try:
            rows = conn.execute("""
                SELECT * FROM permisos ORDER BY id DESC
            """).fetchall()
            result = [PermisoModel._enrich_row(dict(r)) for r in rows]
            return result
        finally:
            conn.close()

    @staticmethod
    def get_by_id(permiso_id: int) -> dict:
        conn = PermisoModel._connect()
        try:
            row = conn.execute(
                "SELECT * FROM permisos WHERE id = ?", (permiso_id,)
            ).fetchone()
            if row:
                return PermisoModel._enrich_row(dict(row))
            return {}
        finally:
            conn.close()

    @staticmethod
    def get_by_personal_id(personal_id: int) -> list:
        conn = PermisoModel._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM permisos WHERE personal_id = ? ORDER BY id DESC",
                (personal_id,),
            ).fetchall()
            result = [PermisoModel._enrich_row(dict(r)) for r in rows]
            return result
        finally:
            conn.close()

    @staticmethod
    def update(permiso_id: int, datos: dict):
        datos['id'] = permiso_id
        conn = PermisoModel._connect()
        try:
            conn.execute("""
                UPDATE permisos SET
                    personal_id       = :personal_id,
                    tipo_permiso      = :tipo_permiso,
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
    def delete(permiso_id: int):
        conn = PermisoModel._connect()
        try:
            conn.execute("DELETE FROM permisos WHERE id = ?", (permiso_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def delete_by_personal_id(personal_id: int):
        conn = PermisoModel._connect()
        try:
            conn.execute("DELETE FROM permisos WHERE personal_id = ?", (personal_id,))
            conn.commit()
        finally:
            conn.close()
