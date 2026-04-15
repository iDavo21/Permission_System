from personal.models.personal_model import PersonalModel
from core.validators import validar_personal
from core.logger import logger, LoggerMixin


class PersonalController(LoggerMixin):
    def __init__(self):
        pass

    def obtener_todos(self):
        return PersonalModel.get_all()

    def obtener_por_id(self, personal_id):
        return PersonalModel.get_by_id(personal_id)

    def guardar(self, datos):
        ok, msg, errores = validar_personal(datos)
        if not ok:
            return None, msg, None
        
        if PersonalModel.existe_cedula(datos.get("cedula", "")):
            return None, "Ya existe una persona con esa cédula", None
        try:
            pid = PersonalModel.save(datos)
            nombre = f"{datos.get('nombres', '')} {datos.get('apellidos', '')}"
            self.log_info("Personal creado", personal_id=pid, nombre=nombre, cedula=datos.get('cedula'))
            return pid, None, f"✓ {nombre} registrado exitosamente"
        except ValueError as e:
            self.log_error("Error de validación al crear personal", error=str(e), cedula=datos.get('cedula'))
            return None, str(e), None
        except Exception as e:
            self.log_error("Error al crear personal", error=e, cedula=datos.get('cedula'))
            return None, str(e), None

    def actualizar(self, personal_id, datos):
        ok, msg, errores = validar_personal(datos)
        if not ok:
            return None, msg, None
        
        if PersonalModel.existe_cedula(datos.get("cedula", ""), excluir_id=personal_id):
            return None, "Ya existe otra persona con esa cédula", None
        try:
            PersonalModel.update(personal_id, datos)
            self.log_info("Personal actualizado", personal_id=personal_id, cedula=datos.get('cedula'))
            return True, None, "✓ Datos actualizados correctamente"
        except ValueError as e:
            self.log_error("Error de validación al actualizar personal", error=str(e), personal_id=personal_id)
            return None, str(e), None
        except Exception as e:
            self.log_error("Error al actualizar personal", error=e, personal_id=personal_id)
            return None, str(e), None

    def eliminar(self, personal_id):
        try:
            PersonalModel.delete(personal_id)
            self.log_info("Personal eliminado", personal_id=personal_id)
            return True, None, "✓ Registro eliminado correctamente"
        except Exception as e:
            self.log_error("Error al eliminar personal", error=e, personal_id=personal_id)
            return None, str(e), None

    def buscar(self, termino):
        self.log_debug("Búsqueda realizada", termino=termino)
        return PersonalModel.buscar(termino)

    def contar(self):
        return PersonalModel.contar()
