from comisiones.models.comision_model import ComisionModel
from core.validators import validar_comision
from core.logger import logger, LoggerMixin


class ComisionesController(LoggerMixin):
    def __init__(self):
        pass

    def obtener_todos(self):
        return ComisionModel.get_all()

    def obtener_por_id(self, comision_id):
        return ComisionModel.get_by_id(comision_id)

    def obtener_por_personal(self, personal_id):
        return ComisionModel.get_by_personal_id(personal_id)

    def guardar(self, datos):
        ok, msg, errores = validar_comision(datos)
        if not ok:
            return None, msg, None
        
        if ComisionModel.tiene_comision_activa(datos.get("personal_id")):
            return None, "Esta persona ya tiene una comisión activa", None
        
        if ComisionModel.existe_duplicado(datos):
            return None, "Ya existe una comisión igual para esta persona en las mismas fechas.", None
        try:
            cid = ComisionModel.save(datos)
            self.log_info("Comisión creada", comision_id=cid, personal_id=datos.get('personal_id'), tipo=datos.get('tipo_comision'))
            return cid, None, "✓ Comisión registrada exitosamente"
        except ValueError as e:
            self.log_error("Error de validación al crear comisión", error=str(e), personal_id=datos.get('personal_id'))
            return None, str(e), None
        except Exception as e:
            self.log_error("Error al crear comisión", error=e, personal_id=datos.get('personal_id'))
            return None, "No se pudo guardar la comisión. Verifique que los datos sean correctos.", None

    def actualizar(self, comision_id, datos):
        ok, msg, errores = validar_comision(datos)
        if not ok:
            return None, msg, None
        
        if ComisionModel.existe_duplicado(datos, excluir_id=comision_id):
            return None, "Ya existe otra comisión igual para esta persona en las mismas fechas.", None
        try:
            ComisionModel.update(comision_id, datos)
            self.log_info("Comisión actualizada", comision_id=comision_id, personal_id=datos.get('personal_id'))
            return True, None, "✓ Comisión actualizada correctamente"
        except ValueError as e:
            self.log_error("Error de validación al actualizar comisión", error=str(e), comision_id=comision_id)
            return None, str(e), None
        except Exception as e:
            self.log_error("Error al actualizar comisión", error=e, comision_id=comision_id)
            return None, "No se pudo actualizar la comisión. Verifique que los datos sean correctos.", None

    def eliminar(self, comision_id):
        try:
            ComisionModel.delete(comision_id)
            self.log_info("Comisión eliminada", comision_id=comision_id)
            return True, None, "✓ Comisión eliminada correctamente"
        except Exception as e:
            self.log_error("Error al eliminar comisión", error=e, comision_id=comision_id)
            return None, "No se pudo eliminar la comisión. Verifique que los datos sean correctos.", None

    def eliminar_por_personal(self, personal_id):
        try:
            ComisionModel.delete_by_personal_id(personal_id)
            self.log_info("Comisiones eliminadas para personal", personal_id=personal_id)
            return True, None, "✓ Comisiones eliminadas correctamente"
        except Exception as e:
            self.log_error("Error al eliminar comisiones", error=e, personal_id=personal_id)
            return None, "No se pudieron eliminar las comisiones. Verifique que los datos sean correctos.", None

    def finalizar(self, comision_id):
        try:
            ComisionModel.finalizar(comision_id)
            self.log_info("Comisión finalizada", comision_id=comision_id)
            return True, None, "✓ Comisión finalizada correctamente"
        except Exception as e:
            self.log_error("Error al finalizar comisión", error=e, comision_id=comision_id)
            return None, "No se pudo finalizar la comisión. Verifique que los datos sean correctos.", None
