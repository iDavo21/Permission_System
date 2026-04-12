from core.database import get_connection

DB_NAME = "personal.db"


class PersonalModel:
    """Modelo DAO para la gestión de personal."""
    @staticmethod
    def _connect():
        return get_connection(DB_NAME)

    @staticmethod
    def create_table():
        conn = PersonalModel._connect()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS personal (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombres           TEXT NOT NULL,
                    apellidos         TEXT NOT NULL,
                    cedula            TEXT NOT NULL UNIQUE,
                    telefono          TEXT NOT NULL,
                    grado_jerarquia   TEXT,
                    cargo             TEXT,
                    dir_domiciliaria  TEXT,
                    dir_emergencia    TEXT,
                    creado_en         TEXT DEFAULT CURRENT_TIMESTAMP,
                    actualizado_en    TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cedula ON personal(cedula)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_nombres ON personal(nombres)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_apellidos ON personal(apellidos)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_grado ON personal(grado_jerarquia)")
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def save(datos: dict) -> int:
        """Guarda un nuevo registro de personal."""
        conn = PersonalModel._connect()
        try:
            cursor = conn.execute("""
                INSERT INTO personal (
                    nombres, apellidos, cedula, telefono,
                    grado_jerarquia, cargo, dir_domiciliaria, dir_emergencia
                ) VALUES (
                    :nombres, :apellidos, :cedula, :telefono,
                    :grado_jerarquia, :cargo, :dir_domiciliaria, :dir_emergencia
                )
            """, datos)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_all() -> list:
        """Obtiene todos los registros de personal."""
        conn = PersonalModel._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM personal ORDER BY apellidos, nombres"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(personal_id: int) -> dict:
        """Obtiene un registro de personal por ID."""
        conn = PersonalModel._connect()
        try:
            row = conn.execute(
                "SELECT * FROM personal WHERE id = ?", (personal_id,)
            ).fetchone()
            return dict(row) if row else {}
        finally:
            conn.close()

    @staticmethod
    def update(personal_id: int, datos: dict):
        """Actualiza un registro de personal."""
        datos['id'] = personal_id
        conn = PersonalModel._connect()
        try:
            conn.execute("""
                UPDATE personal SET
                    nombres           = :nombres,
                    apellidos         = :apellidos,
                    cedula            = :cedula,
                    telefono          = :telefono,
                    grado_jerarquia   = :grado_jerarquia,
                    cargo             = :cargo,
                    dir_domiciliaria  = :dir_domiciliaria,
                    dir_emergencia    = :dir_emergencia,
                    actualizado_en    = CURRENT_TIMESTAMP
                WHERE id = :id
            """, datos)
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def delete(personal_id: int):
        """Elimina un registro de personal."""
        conn = PersonalModel._connect()
        try:
            conn.execute("DELETE FROM personal WHERE id = ?", (personal_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def existe_cedula(cedula: str, excluir_id: int = None) -> bool:
        """Verifica si una cédula ya existe."""
        conn = PersonalModel._connect()
        try:
            if excluir_id:
                row = conn.execute(
                    "SELECT COUNT(*) FROM personal WHERE cedula = ? AND id != ?",
                    (cedula, excluir_id)
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT COUNT(*) FROM personal WHERE cedula = ?",
                    (cedula,)
                ).fetchone()
            return row[0] > 0
        finally:
            conn.close()

    @staticmethod
    def buscar(termino: str) -> list:
        """Busca personal por término."""
        conn = PersonalModel._connect()
        try:
            t = "%%%s%%" % termino
            rows = conn.execute("""
                SELECT * FROM personal
                WHERE nombres LIKE :t OR apellidos LIKE :t OR cedula LIKE :t OR grado_jerarquia LIKE :t
                ORDER BY apellidos, nombres
            """, {"t": t}).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def contar() -> int:
        """Cuenta el total de registros."""
        conn = PersonalModel._connect()
        try:
            row = conn.execute("SELECT COUNT(*) FROM personal").fetchone()
            return row[0]
        finally:
            conn.close()
