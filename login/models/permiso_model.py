import sqlite3
import os

# Ruta a la base de datos dentro de la carpeta data/
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'permisos.db')

class PermisoModel:
    """Encapsula todas las operaciones CRUD sobre la tabla permisos en SQLite."""

    @staticmethod
    def _connect():
        """Retorna una conexión a la base de datos."""
        return sqlite3.connect(DB_PATH)

    @staticmethod
    def create_table():
        """Crea la tabla si aún no existe."""
        with PermisoModel._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS permisos (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombres           TEXT NOT NULL,
                    apellidos         TEXT NOT NULL,
                    cedula            TEXT NOT NULL,
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
            conn.commit()

    @staticmethod
    def save(datos: dict) -> int:
        """Inserta un nuevo permiso. Retorna el ID generado."""
        with PermisoModel._connect() as conn:
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

    @staticmethod
    def get_all() -> list:
        """Retorna todos los permisos como lista de dicts."""
        with PermisoModel._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM permisos ORDER BY id DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(permiso_id: int) -> dict:
        """Retorna un permiso por su ID."""
        with PermisoModel._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM permisos WHERE id = ?", (permiso_id,)
            ).fetchone()
            return dict(row) if row else {}

    @staticmethod
    def update(permiso_id: int, datos: dict):
        """Actualiza los campos de un permiso existente."""
        datos['id'] = permiso_id
        with PermisoModel._connect() as conn:
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

    @staticmethod
    def delete(permiso_id: int):
        """Elimina un permiso por su ID."""
        with PermisoModel._connect() as conn:
            conn.execute("DELETE FROM permisos WHERE id = ?", (permiso_id,))
            conn.commit()
