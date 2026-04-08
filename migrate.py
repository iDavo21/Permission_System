import sqlite3
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
OLD_PATH = os.path.join(ROOT, 'login', 'data', 'permisos.db')
DATA_DIR = os.path.join(ROOT, 'data')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups', 'pre_migracion')
USUARIOS_DB = os.path.join(DATA_DIR, 'usuarios.db')


def migrar():
    print("=" * 60)
    print("MIGRACION DE DATOS")
    print("=" * 60)

    if not os.path.exists(OLD_PATH):
        print("\nNo se encontro la base de datos antigua en: %s" % OLD_PATH)
        return

    conn_old = sqlite3.connect(OLD_PATH)
    conn_old.row_factory = sqlite3.Row
    tables = conn_old.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print("\nTablas en BD antigua:", [t[0] for t in tables])

    if 'permisos' not in [t[0] for t in tables]:
        print("No hay tabla permisos en la BD antigua.")
        return

    rows = conn_old.execute("SELECT * FROM permisos ORDER BY id").fetchall()
    print("Registros encontrados: %d" % len(rows))

    if len(rows) == 0:
        print("No hay datos para migrar.")
        conn_old.close()
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)
    for db in ['permisos.db', 'personal.db', 'comisiones.db', 'usuarios.db']:
        src = os.path.join(DATA_DIR, db)
        if os.path.exists(src):
            dst = os.path.join(BACKUP_DIR, db)
            if not os.path.exists(dst):
                import shutil
                shutil.copy2(src, dst)
                print("  Respaldo: %s" % db)

    print("\n[1/4] Extrayendo datos personales...")
    personal_map = {}
    personal_data = {}

    for r in rows:
        cedula = r['cedula']
        if cedula not in personal_map:
            pid = len(personal_map) + 1
            personal_map[cedula] = pid
            personal_data[pid] = {
                'nombres': r['nombres'],
                'apellidos': r['apellidos'],
                'cedula': cedula,
                'telefono': r['telefono'],
                'grado_jerarquia': r['grado_jerarquia'],
                'cargo': r['cargo'],
                'dir_domiciliaria': r['dir_domiciliaria'],
                'dir_emergencia': r['dir_emergencia'],
            }

    print("  Personas unicas: %d" % len(personal_data))

    print("\n[2/4] Creando personal.db...")
    new_personal = os.path.join(DATA_DIR, 'personal.db')
    if os.path.exists(new_personal):
        os.remove(new_personal)

    conn_personal = sqlite3.connect(new_personal)
    conn_personal.execute("PRAGMA journal_mode=WAL")
    conn_personal.execute("""
        CREATE TABLE personal (
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
    conn_personal.execute("CREATE INDEX idx_cedula ON personal(cedula)")
    conn_personal.execute("CREATE INDEX idx_nombres ON personal(nombres)")
    conn_personal.execute("CREATE INDEX idx_apellidos ON personal(apellidos)")
    conn_personal.execute("CREATE INDEX idx_grado ON personal(grado_jerarquia)")

    for pid, pdata in personal_data.items():
        conn_personal.execute("""
            INSERT INTO personal (id, nombres, apellidos, cedula, telefono,
                                  grado_jerarquia, cargo, dir_domiciliaria, dir_emergencia)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pid, pdata['nombres'], pdata['apellidos'], pdata['cedula'],
              pdata['telefono'], pdata['grado_jerarquia'], pdata['cargo'],
              pdata['dir_domiciliaria'], pdata['dir_emergencia']))

    conn_personal.commit()
    count_personal = conn_personal.execute("SELECT COUNT(*) FROM personal").fetchone()[0]
    print("  Registros: %d" % count_personal)

    print("\n[3/4] Recreando permisos.db...")
    new_permisos = os.path.join(DATA_DIR, 'permisos.db')

    import time
    retries = 5
    for i in range(retries):
        try:
            if os.path.exists(new_permisos):
                os.remove(new_permisos)
            break
        except PermissionError:
            if i < retries - 1:
                time.sleep(1)
            else:
                tmp = new_permisos + '.old'
                if os.path.exists(tmp):
                    os.remove(tmp)
                os.rename(new_permisos, tmp)
                print("  Renombrado a permisos.db.old")

    conn_new = sqlite3.connect(new_permisos)
    conn_new.execute("PRAGMA journal_mode=WAL")
    conn_new.execute("""
        CREATE TABLE permisos (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            personal_id       INTEGER NOT NULL,
            tipo_permiso      TEXT,
            fecha_elaboracion TEXT,
            fecha_desde       TEXT,
            fecha_hasta       TEXT,
            observaciones     TEXT
        )
    """)
    conn_new.execute("CREATE INDEX idx_personal ON permisos(personal_id)")
    conn_new.execute("CREATE INDEX idx_fecha_hasta ON permisos(fecha_hasta)")
    conn_new.execute("CREATE INDEX idx_fecha_desde ON permisos(fecha_desde)")
    conn_new.execute("CREATE INDEX idx_tipo ON permisos(tipo_permiso)")

    permisos_count = 0
    for r in rows:
        cedula = r['cedula']
        personal_id = personal_map[cedula]
        conn_new.execute("""
            INSERT INTO permisos (personal_id, tipo_permiso, fecha_elaboracion,
                                  fecha_desde, fecha_hasta, observaciones)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (personal_id, r['tipo_permiso'], r['fecha_elaboracion'],
              r['fecha_desde'], r['fecha_hasta'], r['observaciones']))
        permisos_count += 1

    conn_new.commit()
    print("  Registros: %d" % permisos_count)

    print("\n[4/4] Verificando integridad...")
    conn_check = sqlite3.connect(new_permisos)
    huerfanos = 0
    for row in conn_check.execute("SELECT personal_id FROM permisos"):
        exists = conn_personal.execute("SELECT COUNT(*) FROM personal WHERE id = ?", (row[0],)).fetchone()[0]
        if exists == 0:
            huerfanos += 1
    conn_check.close()

    conn_old.close()
    conn_personal.close()
    conn_new.close()

    if not os.path.exists(USUARIOS_DB):
        print("\n  Creando usuarios.db...")
        import hashlib
        conn_u = sqlite3.connect(USUARIOS_DB)
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac("sha256", b"admin123", salt, 100000)
        conn_u.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_key BLOB NOT NULL,
                password_salt BLOB NOT NULL,
                nombre TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'admin',
                activo INTEGER NOT NULL DEFAULT 1,
                creado_en TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn_u.execute("INSERT INTO usuarios (username, password_key, password_salt, nombre, rol) VALUES (?, ?, ?, ?, ?)",
                       ("admin", key, salt, "Administrador", "admin"))
        conn_u.commit()
        conn_u.close()
        print("  Admin: admin / admin123")

    print("\n" + "=" * 60)
    if huerfanos == 0:
        print("MIGRACION EXITOSA")
    else:
        print("MIGRACION COMPLETADA CON %d REGISTROS HUERFANOS" % huerfanos)
    print("=" * 60)
    print("\n  personal.db  -> %d personas" % count_personal)
    print("  permisos.db  -> %d permisos" % permisos_count)
    print("  Respaldos    -> %s" % BACKUP_DIR)


if __name__ == '__main__':
    migrar()
