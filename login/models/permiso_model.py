import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'permisos.db')


class PermisoModel:
    """Encapsula todas las operaciones CRUD sobre la tabla permisos en SQLite."""

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
                    nombres           TEXT NOT NULL,
                    apellidos         TEXT NOT NULL,
                    cedula            TEXT NOT NULL UNIQUE,
                    telefono          TEXT NOT NULL,
                    grado_jerarquia   TEXT,
                    cargo             TEXT,
                    tipo_permiso      TEXT,
                    fecha_elaboracion TEXT,
                    fecha_desde       TEXT,
                    fecha_hasta       TEXT,
                    dir_domiciliaria  TEXT,
                    dir_emergencia    TEXT,
                    observaciones     TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cedula ON permisos(cedula)")
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
                    nombres, apellidos, cedula, telefono,
                    grado_jerarquia, cargo, tipo_permiso,
                    fecha_elaboracion, fecha_desde, fecha_hasta,
                    dir_domiciliaria, dir_emergencia, observaciones
                ) VALUES (
                    :nombres, :apellidos, :cedula, :telefono,
                    :grado_jerarquia, :cargo, :tipo_permiso,
                    :fecha_elaboracion, :fecha_desde, :fecha_hasta,
                    :dir_domiciliaria, :dir_emergencia, :observaciones
                )
            """, datos)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_all() -> list:
        conn = PermisoModel._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM permisos ORDER BY id DESC"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(permiso_id: int) -> dict:
        conn = PermisoModel._connect()
        try:
            row = conn.execute(
                "SELECT * FROM permisos WHERE id = ?", (permiso_id,)
            ).fetchone()
            return dict(row) if row else {}
        finally:
            conn.close()

    @staticmethod
    def update(permiso_id: int, datos: dict):
        datos['id'] = permiso_id
        conn = PermisoModel._connect()
        try:
            conn.execute("""
                UPDATE permisos SET
                    nombres           = :nombres,
                    apellidos         = :apellidos,
                    cedula            = :cedula,
                    telefono          = :telefono,
                    grado_jerarquia   = :grado_jerarquia,
                    cargo             = :cargo,
                    tipo_permiso      = :tipo_permiso,
                    fecha_elaboracion = :fecha_elaboracion,
                    fecha_desde       = :fecha_desde,
                    fecha_hasta       = :fecha_hasta,
                    dir_domiciliaria  = :dir_domiciliaria,
                    dir_emergencia    = :dir_emergencia,
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
    def existe_cedula(cedula: str, excluir_id: int = None) -> bool:
        conn = PermisoModel._connect()
        try:
            if excluir_id:
                row = conn.execute(
                    "SELECT COUNT(*) FROM permisos WHERE cedula = ? AND id != ?",
                    (cedula, excluir_id)
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT COUNT(*) FROM permisos WHERE cedula = ?",
                    (cedula,)
                ).fetchone()
            return row[0] > 0
        finally:
            conn.close()
