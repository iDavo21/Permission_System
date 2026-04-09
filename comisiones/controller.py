from comisiones.models.comision_model import ComisionModel
from core.logger import logger


class ComisionesController:
    def __init__(self):
        ComisionModel.create_table()

    def obtener_todos(self):
        return ComisionModel.get_all()

    def obtener_por_id(self, comision_id):
        return ComisionModel.get_by_id(comision_id)

    def obtener_por_personal(self, personal_id):
        return ComisionModel.get_by_personal_id(personal_id)

    def guardar(self, datos):
        if ComisionModel.existe_duplicado(datos):
            return None, "Ya existe una comisión idéntica para este personal en ese rango de fechas."
        try:
            cid = ComisionModel.save(datos)
            logger.info(f"Comisión creada ID: {cid} - Personal: {datos.get('personal_id')}")
            return cid, None
        except Exception as e:
            logger.error(f"Error al crear comisión: {str(e)}")
            return None, str(e)

    def actualizar(self, comision_id, datos):
        if ComisionModel.existe_duplicado(datos, excluir_id=comision_id):
            return None, "Ya existe otra comisión idéntica para este personal en ese rango de fechas."
        try:
            ComisionModel.update(comision_id, datos)
            logger.info(f"Comisión actualizada ID: {comision_id}")
            return True, None
        except Exception as e:
            logger.error(f"Error al actualizar comisión ID {comision_id}: {str(e)}")
            return None, str(e)

    def eliminar(self, comision_id):
        try:
            ComisionModel.delete(comision_id)
            logger.info(f"Comisión eliminada ID: {comision_id}")
            return True, None
        except Exception as e:
            logger.error(f"Error al eliminar comisión ID {comision_id}: {str(e)}")
            return None, str(e)

    def eliminar_por_personal(self, personal_id):
        try:
            ComisionModel.delete_by_personal_id(personal_id)
            logger.info(f"Comisiones eliminadas para personal ID: {personal_id}")
            return True, None
        except Exception as e:
            logger.error(f"Error al eliminar comisiones para personal ID {personal_id}: {str(e)}")
            return None, str(e)
