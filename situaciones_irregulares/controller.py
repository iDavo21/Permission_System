from situaciones_irregulares.models.situacion_model import SituacionIrregularModel
from core.validators import validar_situacion
from core.logger import logger, LoggerMixin


class SituacionesController(LoggerMixin):
    def __init__(self):
        pass

    def obtener_todos(self):
        return SituacionIrregularModel.get_all()

    def obtener_por_id(self, situacion_id):
        return SituacionIrregularModel.get_by_id(situacion_id)

    def obtener_por_personal(self, personal_id):
        return SituacionIrregularModel.get_by_personal_id(personal_id)

    def guardar(self, datos):
        ok, msg, errores = validar_situacion(datos)
        if not ok:
            return None, msg, None
        
        if SituacionIrregularModel.tiene_situacion_activa(datos.get("personal_id")):
            return None, "Esta persona ya tiene una situación irregular activa", None
        
        if SituacionIrregularModel.existe_duplicado(datos):
            return None, "Ya existe una situación activa igual para esta persona.", None
        try:
            cid = SituacionIrregularModel.save(datos)
            self.log_info("Situación irregular creada", situacion_id=cid, personal_id=datos.get('personal_id'), tipo=datos.get('tipo_situacion'))
            return cid, None, "✓ Situación irregular registrada exitosamente"
        except ValueError as e:
            self.log_error("Error de validación al crear situación", error=str(e), personal_id=datos.get('personal_id'))
            return None, str(e), None
        except Exception as e:
            self.log_error("Error al crear situación irregular", error=e, personal_id=datos.get('personal_id'))
            return None, "No se pudo guardar la situación. Verifique que los datos sean correctos.", None

    def actualizar(self, situacion_id, datos):
        ok, msg, errores = validar_situacion(datos)
        if not ok:
            return None, msg, None
        
        if SituacionIrregularModel.existe_duplicado(datos, excluir_id=situacion_id):
            return None, "Ya existe otra situación activa igual para esta persona.", None
        try:
            SituacionIrregularModel.update(situacion_id, datos)
            self.log_info("Situación irregular actualizada", situacion_id=situacion_id, personal_id=datos.get('personal_id'))
            return True, None, "✓ Situación irregular actualizada correctamente"
        except ValueError as e:
            self.log_error("Error de validación al actualizar situación", error=str(e), situacion_id=situacion_id)
            return None, str(e), None
        except Exception as e:
            self.log_error("Error al actualizar situación irregular", error=e, situacion_id=situacion_id)
            return None, "No se pudo actualizar la situación. Verifique que los datos sean correctos.", None

    def eliminar(self, situacion_id):
        try:
            SituacionIrregularModel.delete(situacion_id)
            self.log_info("Situación irregular eliminada", situacion_id=situacion_id)
            return True, None, "✓ Situación irregular eliminada correctamente"
        except Exception as e:
            self.log_error("Error al eliminar situación irregular", error=e, situacion_id=situacion_id)
            return None, "No se pudo eliminar la situación. Verifique que los datos sean correctos.", None

    def eliminar_por_personal(self, personal_id):
        try:
            SituacionIrregularModel.delete_by_personal_id(personal_id)
            self.log_info("Situaciones irregulares eliminadas para personal", personal_id=personal_id)
            return True, None, "✓ Situaciones eliminadas correctamente"
        except Exception as e:
            self.log_error("Error al eliminar situaciones", error=e, personal_id=personal_id)
            return None, "No se pudieron eliminar las situaciones. Verifique que los datos sean correctos.", None

    def resolver(self, situacion_id, fecha_resolucion):
        try:
            SituacionIrregularModel.resolver(situacion_id, fecha_resolucion)
            self.log_info("Situación irregular resuelta", situacion_id=situacion_id)
            return True, None, "✓ Situación resuelta correctamente"
        except Exception as e:
            self.log_error("Error al resolver situación", error=e, situacion_id=situacion_id)
            return None, "No se pudo resolver la situación. Verifique que los datos sean correctos.", None
