import os
import shutil
from datetime import datetime

BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'backups')
MAX_BACKUPS = 10


def crear_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, "backup_%s" % timestamp)
    os.makedirs(backup_path, exist_ok=True)

    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    dbs = ['personal.db', 'permisos.db', 'comisiones.db', 'usuarios.db']

    copiados = 0
    for db in dbs:
        src = os.path.join(data_dir, db)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(backup_path, db))
            copiados += 1

    _limpiar_backups()

    if copiados == 0:
        raise RuntimeError("No se encontraron bases de datos para respaldar")

    return "backup_%s" % timestamp


def _limpiar_backups():
    if not os.path.exists(BACKUP_DIR):
        return
    backups = sorted(os.listdir(BACKUP_DIR))
    while len(backups) > MAX_BACKUPS:
        viejo = backups.pop(0)
        ruta_viejo = os.path.join(BACKUP_DIR, viejo)
        if os.path.isdir(ruta_viejo):
            shutil.rmtree(ruta_viejo)


def listar_backups():
    if not os.path.exists(BACKUP_DIR):
        return []
    return sorted(os.listdir(BACKUP_DIR), reverse=True)
