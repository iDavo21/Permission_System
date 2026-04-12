import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from personal.controller import PersonalController
from permisos.controller import PermisosController
from comisiones.controller import ComisionesController
from auth.controller import AuthController


class TestPersonalController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controller = PersonalController()

    def test_obtener_todos(self):
        result = self.controller.obtener_todos()
        self.assertIsInstance(result, list)

    def test_obtener_por_id(self):
        result = self.controller.obtener_por_id(9999)
        self.assertIsInstance(result, dict)

    def test_buscar(self):
        result = self.controller.buscar("test")
        self.assertIsInstance(result, list)

    def test_contar(self):
        result = self.controller.contar()
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)

    def test_guardar_datos_invalidos(self):
        datos = {
            "nombres": "",
            "apellidos": "",
            "cedula": "",
            "telefono": "",
        }
        result, err, msg = self.controller.guardar(datos)
        self.assertIsNone(result)
        self.assertIsNotNone(err)

    def test_actualizar_datos_invalidos(self):
        result, err, msg = self.controller.actualizar(9999, {})
        self.assertIsNone(result)


class TestPermisosController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controller = PermisosController()

    def test_obtener_todos(self):
        result = self.controller.obtener_todos()
        self.assertIsInstance(result, list)

    def test_obtener_por_id(self):
        result = self.controller.obtener_por_id(9999)
        self.assertIsInstance(result, dict)

    def test_obtener_por_personal(self):
        result = self.controller.obtener_por_personal(9999)
        self.assertIsInstance(result, list)


class TestComisionesController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controller = ComisionesController()

    def test_obtener_todos(self):
        result = self.controller.obtener_todos()
        self.assertIsInstance(result, list)

    def test_obtener_por_id(self):
        result = self.controller.obtener_por_id(9999)
        self.assertIsInstance(result, dict)

    def test_obtener_por_personal(self):
        result = self.controller.obtener_por_personal(9999)
        self.assertIsInstance(result, list)


class TestAuthController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controller = AuthController()

    def test_login_credenciales_vacias(self):
        user, err = self.controller.login("", "")
        self.assertIsNone(user)
        self.assertIsNotNone(err)

    def test_login_credenciales_invalidas(self):
        user, err = self.controller.login("usuario_invalido", "password_invalida")
        self.assertIsNone(user)

    def test_login_admin_defecto(self):
        user, err = self.controller.login("admin", "admin123")
        self.assertIsNotNone(user)
        self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()