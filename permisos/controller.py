from permisos.models.permiso_model import PermisoModel
from core.validators import validar_permiso
from core.logger import logger, LoggerMixin


class PermisosController(LoggerMixin):
    def __init__(self):
        pass

    def obtener_todos(self):
        return PermisoModel.get_all()

    def obtener_por_id(self, permiso_id):
        return PermisoModel.get_by_id(permiso_id)

    def obtener_por_personal(self, personal_id):
        return PermisoModel.get_by_personal_id(personal_id)

    def guardar(self, datos):
        ok, msg, errores = validar_permiso(datos)
        if not ok:
            return None, msg, None
        
        if PermisoModel.tiene_permiso_activo(datos.get("personal_id")):
            return None, "Esta persona ya tiene un permiso activo", None
        
        if PermisoModel.existe_duplicado(datos):
            return None, "Ya existe un permiso igual para esta persona en las mismas fechas.", None
        try:
            pid = PermisoModel.save(datos)
            self.log_info("Permiso creado", permiso_id=pid, personal_id=datos.get('personal_id'), tipo=datos.get('tipo_permiso'))
            return pid, None, "✓ Permiso registrado exitosamente"
        except ValueError as e:
            self.log_error("Error de validación al crear permiso", error=str(e), personal_id=datos.get('personal_id'))
            return None, str(e), None
        except Exception as e:
            self.log_error("Error al crear permiso", error=e, personal_id=datos.get('personal_id'))
            return None, "No se pudo guardar el permiso. Verifique que los datos sean correctos.", None

    def actualizar(self, permiso_id, datos):
        ok, msg, errores = validar_permiso(datos)
        if not ok:
            return None, msg, None
        
        if PermisoModel.existe_duplicado(datos, excluir_id=permiso_id):
            return None, "Ya existe otro permiso igual para esta persona en las mismas fechas.", None
        try:
            PermisoModel.update(permiso_id, datos)
            self.log_info("Permiso actualizado", permiso_id=permiso_id, personal_id=datos.get('personal_id'))
            return True, None, "✓ Permiso actualizado correctamente"
        except ValueError as e:
            self.log_error("Error de validación al actualizar permiso", error=str(e), permiso_id=permiso_id)
            return None, str(e), None
        except Exception as e:
            self.log_error("Error al actualizar permiso", error=e, permiso_id=permiso_id)
            return None, "No se pudo actualizar el permiso. Verifique que los datos sean correctos.", None

    def eliminar(self, permiso_id):
        try:
            PermisoModel.delete(permiso_id)
            self.log_info("Permiso eliminado", permiso_id=permiso_id)
            return True, None, "✓ Permiso eliminado correctamente"
        except Exception as e:
            self.log_error("Error al eliminar permiso", error=e, permiso_id=permiso_id)
            return None, str(e), None

    def eliminar_por_personal(self, personal_id):
        try:
            PermisoModel.delete_by_personal_id(personal_id)
            self.log_info("Permisos eliminados para personal", personal_id=personal_id)
            return True, None, "✓ Permisos eliminados correctamente"
        except Exception as e:
            self.log_error("Error al eliminar permisos", error=e, personal_id=personal_id)
            return None, str(e), None
