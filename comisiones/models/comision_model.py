from core.database import get_connection, get_db_path
from core.validators import validar_comision

DB_NAME = "comisiones.db"
PERSONAL_DB = "personal.db"


def _attach_personal(conn):
    personal_path = get_db_path(PERSONAL_DB)
    conn.execute(f"ATTACH DATABASE '{personal_path}' AS personal_db")


class ComisionModel:
    @staticmethod
    def _connect():
        return get_connection(DB_NAME)

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
                    fecha_salida      TEXT,
                    finalizada       INTEGER DEFAULT 0,
                    observaciones     TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_personal ON comisiones(personal_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fecha_salida ON comisiones(fecha_salida)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_finalizada ON comisiones(finalizada)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tipo ON comisiones(tipo_comision)")
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def save(datos: dict) -> int:
        ok, msg, errores = validar_comision(datos)
        if not ok:
            raise ValueError(msg)
        
        conn = ComisionModel._connect()
        try:
            cursor = conn.execute("""
                INSERT INTO comisiones (
                    personal_id, tipo_comision, destino,
                    fecha_elaboracion, fecha_salida, finalizada, observaciones
                ) VALUES (
                    :personal_id, :tipo_comision, :destino,
                    :fecha_elaboracion, :fecha_salida, :finalizada, :observaciones
                )
            """, datos)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_all() -> list:
        conn = ComisionModel._connect()
        try:
            _attach_personal(conn)
            rows = conn.execute("""
                SELECT c.*, 
                       per.nombres, per.apellidos, per.cedula, per.telefono,
                       per.grado_jerarquia, per.cargo, 
                       per.dir_domiciliaria, per.dir_emergencia
                FROM comisiones c
                LEFT JOIN personal_db.personal per ON c.personal_id = per.id
                ORDER BY c.id DESC
            """).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(comision_id: int) -> dict:
        conn = ComisionModel._connect()
        try:
            _attach_personal(conn)
            row = conn.execute("""
                SELECT c.*, 
                       per.nombres, per.apellidos, per.cedula, per.telefono,
                       per.grado_jerarquia, per.cargo, 
                       per.dir_domiciliaria, per.dir_emergencia
                FROM comisiones c
                LEFT JOIN personal_db.personal per ON c.personal_id = per.id
                WHERE c.id = ?
            """, (comision_id,)).fetchone()
            return dict(row) if row else {}
        finally:
            conn.close()

    @staticmethod
    def get_by_personal_id(personal_id: int) -> list:
        conn = ComisionModel._connect()
        try:
            _attach_personal(conn)
            rows = conn.execute("""
                SELECT c.*, 
                       per.nombres, per.apellidos, per.cedula, per.telefono,
                       per.grado_jerarquia, per.cargo, 
                       per.dir_domiciliaria, per.dir_emergencia
                FROM comisiones c
                LEFT JOIN personal_db.personal per ON c.personal_id = per.id
                WHERE c.personal_id = ?
                ORDER BY c.id DESC
            """, (personal_id,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def update(comision_id: int, datos: dict):
        ok, msg, errores = validar_comision(datos)
        if not ok:
            raise ValueError(msg)
        
        datos['id'] = comision_id
        conn = ComisionModel._connect()
        try:
            conn.execute("""
                UPDATE comisiones SET
                    personal_id       = :personal_id,
                    tipo_comision     = :tipo_comision,
                    destino           = :destino,
                    fecha_elaboracion = :fecha_elaboracion,
                    fecha_salida      = :fecha_salida,
                    finalizada       = :finalizada,
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
    def finalizar(comision_id: int):
        conn = ComisionModel._connect()
        try:
            conn.execute("UPDATE comisiones SET finalizada = 1 WHERE id = ?", (comision_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def tiene_comision_activa(personal_id: int) -> bool:
        """Verifica si una persona tiene una comisión activa (no finalizada)."""
        conn = ComisionModel._connect()
        try:
            count = conn.execute(
                "SELECT COUNT(*) FROM comisiones WHERE personal_id = ? AND finalizada = 0",
                (personal_id,)
            ).fetchone()[0]
            return count > 0
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
                  AND fecha_salida = :fecha_salida
            """
            parametros = {
                "personal_id": datos.get("personal_id"),
                "tipo_comision": datos.get("tipo_comision"),
                "fecha_salida": datos.get("fecha_salida"),
            }
            if excluir_id:
                query += " AND id != :excluir_id"
                parametros["excluir_id"] = excluir_id
            
            count = conn.execute(query, parametros).fetchone()[0]
            return count > 0
        finally:
            conn.close()
