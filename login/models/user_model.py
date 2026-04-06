import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'usuarios.db')

SALT_LENGTH = 32
DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASS = "admin123"


def hash_password(password: str, salt: bytes = None) -> tuple:
    if salt is None:
        salt = os.urandom(SALT_LENGTH)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return key, salt


def verify_password(password: str, stored_key: bytes, stored_salt: bytes) -> bool:
    computed_key, _ = hash_password(password, stored_salt)
    return computed_key == stored_key


class UserModel:
    @staticmethod
    def _connect():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @classmethod
    def create_table(cls):
        conn = cls._connect()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    username    TEXT NOT NULL UNIQUE,
                    password_key BLOB NOT NULL,
                    password_salt BLOB NOT NULL,
                    nombre      TEXT NOT NULL,
                    rol         TEXT NOT NULL DEFAULT 'admin',
                    activo      INTEGER NOT NULL DEFAULT 1,
                    creado_en   TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_username ON usuarios(username)")
            conn.commit()
        finally:
            conn.close()
        cls._crear_admin_default()

    @classmethod
    def _crear_admin_default(cls):
        conn = cls._connect()
        try:
            existe = conn.execute(
                "SELECT COUNT(*) FROM usuarios WHERE username = ?", (DEFAULT_ADMIN_USER,)
            ).fetchone()[0]
            if not existe:
                key, salt = hash_password(DEFAULT_ADMIN_PASS)
                conn.execute(
                    "INSERT INTO usuarios (username, password_key, password_salt, nombre, rol) VALUES (?, ?, ?, ?, ?)",
                    (DEFAULT_ADMIN_USER, key, salt, "Administrador", "admin"),
                )
                conn.commit()
        finally:
            conn.close()

    @classmethod
    def authenticate(cls, username: str, password: str) -> dict:
        conn = cls._connect()
        try:
            row = conn.execute(
                "SELECT * FROM usuarios WHERE username = ? AND activo = 1", (username,)
            ).fetchone()
            if not row:
                return {}
            if verify_password(password, row["password_key"], row["password_salt"]):
                return dict(row)
            return {}
        finally:
            conn.close()

    @classmethod
    def crear_usuario(cls, username: str, password: str, nombre: str, rol: str = "admin") -> int:
        key, salt = hash_password(password)
        conn = cls._connect()
        try:
            cursor = conn.execute(
                "INSERT INTO usuarios (username, password_key, password_salt, nombre, rol) VALUES (?, ?, ?, ?, ?)",
                (username, key, salt, nombre, rol),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @classmethod
    def cambiar_password(cls, user_id: int, nueva_password: str):
        key, salt = hash_password(nueva_password)
        conn = cls._connect()
        try:
            conn.execute(
                "UPDATE usuarios SET password_key = ?, password_salt = ? WHERE id = ?",
                (key, salt, user_id),
            )
            conn.commit()
        finally:
            conn.close()

    @classmethod
    def obtener_todos(cls) -> list:
        conn = cls._connect()
        try:
            rows = conn.execute(
                "SELECT id, username, nombre, rol, activo, creado_en FROM usuarios ORDER BY id"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @classmethod
    def desactivar_usuario(cls, user_id: int):
        conn = cls._connect()
        try:
            conn.execute("UPDATE usuarios SET activo = 0 WHERE id = ?", (user_id,))
            conn.commit()
        finally:
            conn.close()
