import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from personal.models.personal_model import PersonalModel
from permisos.models.permiso_model import PermisoModel
from comisiones.models.comision_model import ComisionModel
from auth.models.user_model import UserModel


class TestPersonalModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        PersonalModel.create_table()

    def test_save_and_get(self):
        datos = {
            "nombres": "Test User",
            "apellidos": "Test Apellido",
            "cedula": f"TEST{os.urandom(4).hex()}",
            "telefono": "04141234567",
            "grado_jerarquia": "Soldado",
            "cargo": "Milicia",
            "dir_domiciliaria": "Test dir",
            "dir_emergencia": "Test emergencia"
        }
        pid = PersonalModel.save(datos)
        self.assertIsInstance(pid, int)
        
        result = PersonalModel.get_by_id(pid)
        self.assertEqual(result["nombres"], "Test User")
        self.assertEqual(result["cedula"], datos["cedula"])
        PersonalModel.delete(pid)

    def test_update(self):
        datos = {
            "nombres": "Original",
            "apellidos": "Apellido",
            "cedula": f"TEST-U{os.urandom(4).hex()}",
            "telefono": "04141234567",
            "grado_jerarquia": "Soldado",
            "cargo": "Milicia",
            "dir_domiciliaria": "Dir",
            "dir_emergencia": "Emergencia"
        }
        pid = PersonalModel.save(datos)
        
        datos["nombres"] = "Actualizado"
        datos["id"] = pid
        PersonalModel.update(pid, datos)
        
        result = PersonalModel.get_by_id(pid)
        self.assertEqual(result["nombres"], "Actualizado")
        PersonalModel.delete(pid)

    def test_delete(self):
        datos = {
            "nombres": "Delete Test",
            "apellidos": "Apellido",
            "cedula": f"TEST-D{os.urandom(4).hex()}",
            "telefono": "04141234567",
            "grado_jerarquia": "Soldado",
            "cargo": "Milicia",
            "dir_domiciliaria": "Dir test",
            "dir_emergencia": "Emergencia test",
        }
        pid = PersonalModel.save(datos)
        PersonalModel.delete(pid)
        
        result = PersonalModel.get_by_id(pid)
        self.assertEqual(result, {})

    def test_buscar(self):
        resultados = PersonalModel.buscar("test")
        self.assertIsInstance(resultados, list)

    def test_contar(self):
        count = PersonalModel.contar()
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)


class TestPermisoModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        PermisoModel.create_table()

    def test_save_and_get(self):
        pid = PersonalModel.save({
            "nombres": "Permiso Test",
            "apellidos": "Apellido",
            "cedula": f"PT{os.urandom(4).hex()}",
            "telefono": "04141234567",
            "grado_jerarquia": "Soldado",
            "cargo": "Milicia",
            "dir_domiciliaria": "Dir test",
            "dir_emergencia": "Emergencia test",
        })
        
        datos = {
            "personal_id": pid,
            "tipo_permiso": "Médico",
            "fecha_elaboracion": "2026-04-12",
            "fecha_desde": "2026-04-13",
            "fecha_hasta": "2026-04-14",
            "observaciones": "Test permiso"
        }
        permisos_id = PermisoModel.save(datos)
        self.assertIsInstance(permisos_id, int)
        PermisoModel.delete(permisos_id)
        PersonalModel.delete(pid)

    def test_get_all(self):
        resultados = PermisoModel.get_all()
        self.assertIsInstance(resultados, list)

    def test_existe_duplicado(self):
        duplicado = PermisoModel.existe_duplicado({
            "personal_id": 1,
            "tipo_permiso": "Test",
            "fecha_desde": "2026-01-01",
            "fecha_hasta": "2026-01-02"
        })
        self.assertIsInstance(duplicado, bool)


class TestComisionModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ComisionModel.create_table()

    def test_save_and_get(self):
        pid = PersonalModel.save({
            "nombres": "Comision Test",
            "apellidos": "Apellido",
            "cedula": f"CT{os.urandom(4).hex()}",
            "telefono": "04141234567",
            "grado_jerarquia": "Soldado",
            "cargo": "Milicia",
            "dir_domiciliaria": "Dir test",
            "dir_emergencia": "Emergencia test",
        })
        
        datos = {
            "personal_id": pid,
            "tipo_comision": "Oficial",
            "destino": "Caracas",
            "fecha_elaboracion": "2026-04-12",
            "fecha_desde": "2026-04-13",
            "fecha_hasta": "2026-04-14",
            "observaciones": "Test comision"
        }
        comision_id = ComisionModel.save(datos)
        self.assertIsInstance(comision_id, int)
        ComisionModel.delete(comision_id)
        PersonalModel.delete(pid)

    def test_get_all(self):
        resultados = ComisionModel.get_all()
        self.assertIsInstance(resultados, list)


class TestUserModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        UserModel.create_table()
        UserModel.crear_admin_default()

    def test_authenticate(self):
        user = UserModel.authenticate("admin", "admin123")
        self.assertIsInstance(user, dict)

    def test_authenticate_invalid(self):
        user = UserModel.authenticate("admin", "wrongpass")
        self.assertEqual(user, {})

    def test_crear_usuario(self):
        uid = UserModel.crear_usuario(
            f"testuser{os.urandom(2).hex()}",
            "testpass123",
            "Test User",
            "admin"
        )
        self.assertIsInstance(uid, int)

    def test_obtener_todos(self):
        usuarios = UserModel.obtener_todos()
        self.assertIsInstance(usuarios, list)
        self.assertGreater(len(usuarios), 0)


class TestSecurity(unittest.TestCase):
    def test_sql_injection_buscar(self):
        resultados = PersonalModel.buscar("' OR '1'='1")
        self.assertIsInstance(resultados, list)

    def test_sql_injection_login(self):
        from auth.controller import AuthController
        ctrl = AuthController()
        user, err = ctrl.login("admin' --", "anything")
        self.assertIsNone(user)

    def test_rate_limiting(self):
        from auth.controller import AuthController
        ctrl = AuthController()
        
        for i in range(6):
            user, err = ctrl.login("admin", "wrongpass")
        
        user, err = ctrl.login("admin", "admin123")
        self.assertIsNone(user)
        self.assertIn("intentos", err or "")


if __name__ == '__main__':
    unittest.main()