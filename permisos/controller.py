from permisos.models.permiso_model import PermisoModel


class PermisosController:
    def __init__(self):
        PermisoModel.create_table()

    def obtener_todos(self):
        return PermisoModel.get_all()

    def obtener_por_id(self, permiso_id):
        return PermisoModel.get_by_id(permiso_id)

    def obtener_por_personal(self, personal_id):
        return PermisoModel.get_by_personal_id(personal_id)

    def guardar(self, datos):
        try:
            pid = PermisoModel.save(datos)
            return pid, None
        except Exception as e:
            return None, str(e)

    def actualizar(self, permiso_id, datos):
        try:
            PermisoModel.update(permiso_id, datos)
            return True, None
        except Exception as e:
            return None, str(e)

    def eliminar(self, permiso_id):
        try:
            PermisoModel.delete(permiso_id)
            return True, None
        except Exception as e:
            return None, str(e)

    def eliminar_por_personal(self, personal_id):
        try:
            PermisoModel.delete_by_personal_id(personal_id)
            return True, None
        except Exception as e:
            return None, str(e)
