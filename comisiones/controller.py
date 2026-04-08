from comisiones.models.comision_model import ComisionModel


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
        try:
            cid = ComisionModel.save(datos)
            return cid, None
        except Exception as e:
            return None, str(e)

    def actualizar(self, comision_id, datos):
        try:
            ComisionModel.update(comision_id, datos)
            return True, None
        except Exception as e:
            return None, str(e)

    def eliminar(self, comision_id):
        try:
            ComisionModel.delete(comision_id)
            return True, None
        except Exception as e:
            return None, str(e)

    def eliminar_por_personal(self, personal_id):
        try:
            ComisionModel.delete_by_personal_id(personal_id)
            return True, None
        except Exception as e:
            return None, str(e)
