from personal.models.personal_model import PersonalModel
from permisos.models.permiso_model import PermisoModel
from comisiones.models.comision_model import ComisionModel
from auth.models.user_model import UserModel


def inicializar_sistema():
    PersonalModel.create_table()
    PermisoModel.create_table()
    ComisionModel.create_table()
    UserModel.create_table()
    UserModel.crear_admin_default()


def verificar_tablas():
    from core.database import get_connection
    
    dbs = ["personal.db", "permisos.db", "comisiones.db", "usuarios.db"]
    for db in dbs:
        conn = get_connection(db)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        print(f"{db}: {[r[0] for r in cursor]}")
        conn.close()


if __name__ == "__main__":
    inicializar_sistema()
    print("Sistema inicializado correctamente")