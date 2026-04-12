from comisiones.models.comision_model import ComisionModel
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
        if ComisionModel.existe_duplicado(datos):
            return None, "Ya existe una comisión idéntica para este personal en ese rango de fechas.", None
        try:
            cid = ComisionModel.save(datos)
            self.log_info("Comisión creada", comision_id=cid, personal_id=datos.get('personal_id'), tipo=datos.get('tipo_comision'))
            return cid, None, "✓ Comisión registrada exitosamente"
        except Exception as e:
            self.log_error("Error al crear comisión", error=e, personal_id=datos.get('personal_id'))
            return None, str(e), None

    def actualizar(self, comision_id, datos):
        if ComisionModel.existe_duplicado(datos, excluir_id=comision_id):
            return None, "Ya existe otra comisión idéntica para este personal en ese rango de fechas.", None
        try:
            ComisionModel.update(comision_id, datos)
            self.log_info("Comisión actualizada", comision_id=comision_id, personal_id=datos.get('personal_id'))
            return True, None, "✓ Comisión actualizada correctamente"
        except Exception as e:
            self.log_error("Error al actualizar comisión", error=e, comision_id=comision_id)
            return None, str(e), None

    def eliminar(self, comision_id):
        try:
            ComisionModel.delete(comision_id)
            self.log_info("Comisión eliminada", comision_id=comision_id)
            return True, None, "✓ Comisión eliminada correctamente"
        except Exception as e:
            self.log_error("Error al eliminar comisión", error=e, comision_id=comision_id)
            return None, str(e), None

    def eliminar_por_personal(self, personal_id):
        try:
            ComisionModel.delete_by_personal_id(personal_id)
            self.log_info("Comisiones eliminadas para personal", personal_id=personal_id)
            return True, None, "✓ Comisiones eliminadas correctamente"
        except Exception as e:
            self.log_error("Error al eliminar comisiones", error=e, personal_id=personal_id)
            return None, str(e), None
