from auth.models.user_model import UserModel


class AuthController:
    def __init__(self):
        UserModel.create_table()

    def login(self, username, password):
        user = UserModel.authenticate(username, password)
        if not user:
            return None, "Usuario o contraseña incorrectos"
        if not user.get("activo", 1):
            return None, "Usuario desactivado"
        return user, None

    def crear_usuario(self, username, password, nombre, rol="admin"):
        try:
            uid = UserModel.crear_usuario(username, password, nombre, rol)
            return uid, None
        except Exception as e:
            return None, str(e)

    def obtener_usuarios(self):
        return UserModel.obtener_todos()

    def desactivar_usuario(self, user_id):
        UserModel.desactivar_usuario(user_id)
