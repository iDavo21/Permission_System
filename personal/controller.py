from personal.models.personal_model import PersonalModel
from core.logger import logger


class PersonalController:
    def __init__(self):
        PersonalModel.create_table()

    def obtener_todos(self):
        return PersonalModel.get_all()

    def obtener_por_id(self, personal_id):
        return PersonalModel.get_by_id(personal_id)

    def guardar(self, datos):
        if PersonalModel.existe_cedula(datos.get("cedula", "")):
            return None, "Ya existe una persona con esa cédula"
        try:
            pid = PersonalModel.save(datos)
            logger.info(f"Personal creado: {datos.get('nombres', '')} {datos.get('apellidos', '')} (ID: {pid})")
            return pid, None
        except Exception as e:
            logger.error(f"Error al crear personal: {str(e)}")
            return None, str(e)

    def actualizar(self, personal_id, datos):
        if PersonalModel.existe_cedula(datos.get("cedula", ""), excluir_id=personal_id):
            return None, "Ya existe otra persona con esa cédula"
        try:
            PersonalModel.update(personal_id, datos)
            logger.info(f"Personal actualizado ID: {personal_id}")
            return True, None
        except Exception as e:
            logger.error(f"Error al actualizar personal ID {personal_id}: {str(e)}")
            return None, str(e)

    def eliminar(self, personal_id):
        try:
            PersonalModel.delete(personal_id)
            logger.info(f"Personal eliminado ID: {personal_id}")
            return True, None
        except Exception as e:
            logger.error(f"Error al eliminar personal ID {personal_id}: {str(e)}")
            return None, str(e)

    def buscar(self, termino):
        return PersonalModel.buscar(termino)

    def contar(self):
        return PersonalModel.contar()
