from core.database import get_connection, get_db_path
from core.validators import validar_situacion

DB_NAME = "situaciones_irregulares.db"
PERSONAL_DB = "personal.db"


def _attach_personal(conn):
    personal_path = get_db_path(PERSONAL_DB)
    conn.execute(f"ATTACH DATABASE '{personal_path}' AS personal_db")


class SituacionIrregularModel:
    @staticmethod
    def _connect():
        return get_connection(DB_NAME)

    @staticmethod
    def create_table():
        conn = SituacionIrregularModel._connect()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS situaciones_irregulares (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    personal_id       INTEGER NOT NULL,
                    tipo_situacion    TEXT NOT NULL,
                    fecha_inicio      TEXT NOT NULL,
                    fecha_resolucion  TEXT,
                    estado            TEXT DEFAULT 'Activo',
                    observaciones     TEXT,
                    created_at        TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_personal ON situaciones_irregulares(personal_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_estado ON situaciones_irregulares(estado)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tipo ON situaciones_irregulares(tipo_situacion)")
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def save(datos: dict) -> int:
        ok, msg, errores = validar_situacion(datos)
        if not ok:
            raise ValueError(msg)
        
        conn = SituacionIrregularModel._connect()
        try:
            cursor = conn.execute("""
                INSERT INTO situaciones_irregulares (
                    personal_id, tipo_situacion, fecha_inicio,
                    fecha_resolucion, estado, observaciones
                ) VALUES (
                    :personal_id, :tipo_situacion, :fecha_inicio,
                    :fecha_resolucion, :estado, :observaciones
                )
            """, datos)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_all() -> list:
        conn = SituacionIrregularModel._connect()
        try:
            _attach_personal(conn)
            rows = conn.execute("""
                SELECT s.*, 
                       per.nombres, per.apellidos, per.cedula,
                       per.grado_jerarquia, per.cargo
                FROM situaciones_irregulares s
                LEFT JOIN personal_db.personal per ON s.personal_id = per.id
                ORDER BY s.id DESC
            """).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(situacion_id: int) -> dict:
        conn = SituacionIrregularModel._connect()
        try:
            _attach_personal(conn)
            row = conn.execute("""
                SELECT s.*, 
                       per.nombres, per.apellidos, per.cedula,
                       per.grado_jerarquia, per.cargo, per.telefono,
                       per.dir_domiciliaria, per.dir_emergencia
                FROM situaciones_irregulares s
                LEFT JOIN personal_db.personal per ON s.personal_id = per.id
                WHERE s.id = ?
            """, (situacion_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def get_by_personal_id(personal_id: int) -> list:
        conn = SituacionIrregularModel._connect()
        try:
            _attach_personal(conn)
            rows = conn.execute("""
                SELECT s.*, 
                       per.nombres, per.apellidos, per.cedula,
                       per.grado_jerarquia, per.cargo
                FROM situaciones_irregulares s
                LEFT JOIN personal_db.personal per ON s.personal_id = per.id
                WHERE s.personal_id = ?
                ORDER BY s.id DESC
            """, (personal_id,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def update(situacion_id: int, datos: dict):
        ok, msg, errores = validar_situacion(datos)
        if not ok:
            raise ValueError(msg)
        
        conn = SituacionIrregularModel._connect()
        try:
            conn.execute("""
                UPDATE situaciones_irregulares SET
                    personal_id = :personal_id,
                    tipo_situacion = :tipo_situacion,
                    fecha_inicio = :fecha_inicio,
                    fecha_resolucion = :fecha_resolucion,
                    estado = :estado,
                    observaciones = :observaciones
                WHERE id = :id
            """, {**datos, "id": situacion_id})
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def delete(situacion_id: int):
        conn = SituacionIrregularModel._connect()
        try:
            conn.execute("DELETE FROM situaciones_irregulares WHERE id = ?", (situacion_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def delete_by_personal_id(personal_id: int):
        conn = SituacionIrregularModel._connect()
        try:
            conn.execute("DELETE FROM situaciones_irregulares WHERE personal_id = ?", (personal_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def resolver(situacion_id: int, fecha_resolucion: str):
        conn = SituacionIrregularModel._connect()
        try:
            conn.execute("""
                UPDATE situaciones_irregulares 
                SET estado = 'Resuelto', fecha_resolucion = ?
                WHERE id = ?
            """, (fecha_resolucion, situacion_id))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def tiene_situacion_activa(personal_id: int) -> bool:
        """Verifica si una persona tiene una situación irregular activa."""
        conn = SituacionIrregularModel._connect()
        try:
            count = conn.execute(
                "SELECT COUNT(*) FROM situaciones_irregulares WHERE personal_id = ? AND estado = 'Activo'",
                (personal_id,)
            ).fetchone()[0]
            return count > 0
        finally:
            conn.close()

    @staticmethod
    def existe_duplicado(datos: dict, excluir_id=None) -> bool:
        conn = SituacionIrregularModel._connect()
        try:
            query = """
                SELECT COUNT(*) FROM situaciones_irregulares 
                WHERE personal_id = :personal_id 
                  AND tipo_situacion = :tipo_situacion 
                  AND estado = 'Activo'
            """
            if excluir_id:
                query += " AND id != :excluir_id"
                datos["excluir_id"] = excluir_id
            
            count = conn.execute(query, datos).fetchone()[0]
            return count > 0
        finally:
            conn.close()