from permisos.models.permiso_model import PermisoModel
from core.logger import logger


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
        if PermisoModel.existe_duplicado(datos):
            return None, "Ya existe un permiso idéntico para este personal en ese rango de fechas."
        try:
            pid = PermisoModel.save(datos)
            logger.info(f"Permiso creado ID: {pid} - Personal: {datos.get('personal_id')}")
            return pid, None
        except Exception as e:
            logger.error(f"Error al crear permiso: {str(e)}")
            return None, str(e)

    def actualizar(self, permiso_id, datos):
        if PermisoModel.existe_duplicado(datos, excluir_id=permiso_id):
            return None, "Ya existe otro permiso idéntico para este personal en ese rango de fechas."
        try:
            PermisoModel.update(permiso_id, datos)
            logger.info(f"Permiso actualizado ID: {permiso_id}")
            return True, None
        except Exception as e:
            logger.error(f"Error al actualizar permiso ID {permiso_id}: {str(e)}")
            return None, str(e)

    def eliminar(self, permiso_id):
        try:
            PermisoModel.delete(permiso_id)
            logger.info(f"Permiso eliminado ID: {permiso_id}")
            return True, None
        except Exception as e:
            logger.error(f"Error al eliminar permiso ID {permiso_id}: {str(e)}")
            return None, str(e)

    def eliminar_por_personal(self, personal_id):
        try:
            PermisoModel.delete_by_personal_id(personal_id)
            logger.info(f"Permisos eliminados para personal ID: {personal_id}")
            return True, None
        except Exception as e:
            logger.error(f"Error al eliminar permisos para personal ID {personal_id}: {str(e)}")
            return None, str(e)
