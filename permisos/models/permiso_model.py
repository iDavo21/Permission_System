from core.database import get_connection, get_db_path
from core.validators import validar_permiso

DB_NAME = "permisos.db"
PERSONAL_DB = "personal.db"


def _attach_personal(conn):
    personal_path = get_db_path(PERSONAL_DB)
    conn.execute(f"ATTACH DATABASE '{personal_path}' AS personal_db")


class PermisoModel:
    @staticmethod
    def _connect():
        return get_connection(DB_NAME)

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
        ok, msg, errores = validar_permiso(datos)
        if not ok:
            raise ValueError(msg)
        
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
    def get_all() -> list:
        conn = PermisoModel._connect()
        try:
            _attach_personal(conn)
            rows = conn.execute("""
                SELECT p.*, 
                       per.nombres, per.apellidos, per.cedula, per.telefono,
                       per.grado_jerarquia, per.cargo, 
                       per.dir_domiciliaria, per.dir_emergencia
                FROM permisos p
                LEFT JOIN personal_db.personal per ON p.personal_id = per.id
                ORDER BY p.id DESC
            """).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(permiso_id: int) -> dict:
        conn = PermisoModel._connect()
        try:
            _attach_personal(conn)
            row = conn.execute("""
                SELECT p.*, 
                       per.nombres, per.apellidos, per.cedula, per.telefono,
                       per.grado_jerarquia, per.cargo, 
                       per.dir_domiciliaria, per.dir_emergencia
                FROM permisos p
                LEFT JOIN personal_db.personal per ON p.personal_id = per.id
                WHERE p.id = ?
            """, (permiso_id,)).fetchone()
            return dict(row) if row else {}
        finally:
            conn.close()

    @staticmethod
    def get_by_personal_id(personal_id: int) -> list:
        conn = PermisoModel._connect()
        try:
            _attach_personal(conn)
            rows = conn.execute("""
                SELECT p.*, 
                       per.nombres, per.apellidos, per.cedula, per.telefono,
                       per.grado_jerarquia, per.cargo, 
                       per.dir_domiciliaria, per.dir_emergencia
                FROM permisos p
                LEFT JOIN personal_db.personal per ON p.personal_id = per.id
                WHERE p.personal_id = ?
                ORDER BY p.id DESC
            """, (personal_id,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def update(permiso_id: int, datos: dict):
        ok, msg, errores = validar_permiso(datos)
        if not ok:
            raise ValueError(msg)
        
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

    @staticmethod
    def tiene_permiso_activo(personal_id: int) -> bool:
        """Verifica si una persona tiene un permiso activo (vigente o por expirar)."""
        from core.estado_utils import obtener_estado
        conn = PermisoModel._connect()
        try:
            rows = conn.execute(
                "SELECT fecha_hasta FROM permisos WHERE personal_id = ?",
                (personal_id,)
            ).fetchall()
            for row in rows:
                estado, _ = obtener_estado(row[0])
                if estado in ("Vigente", "Por Expirar"):
                    return True
            return False
        finally:
            conn.close()

    @staticmethod
    def existe_duplicado(datos: dict, excluir_id=None) -> bool:
        conn = PermisoModel._connect()
        try:
            query = """
                SELECT COUNT(*) FROM permisos 
                WHERE personal_id = :personal_id 
                  AND tipo_permiso = :tipo_permiso 
                  AND fecha_desde = :fecha_desde 
                  AND fecha_hasta = :fecha_hasta
            """
            parametros = {
                "personal_id": datos.get("personal_id"),
                "tipo_permiso": datos.get("tipo_permiso"),
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
