import time
from auth.models.user_model import UserModel

MAX_INTENTOS = 5
VENTANA_TIEMPO = 300
_bloqueos = {}


class AuthController:
    def __init__(self):
        from core.inicializador import inicializar_sistema
        inicializar_sistema()

    def _verificar_bloqueo(self, username):
        if username in _bloqueos:
            intentos, tiempo = _bloqueos[username]
            if time.time() - tiempo < VENTANA_TIEMPO:
                return intentos >= MAX_INTENTOS
            else:
                del _bloqueos[username]
        return False

    def _registrar_fallo(self, username):
        if username not in _bloqueos:
            _bloqueos[username] = [0, time.time()]
        _bloqueos[username][0] += 1
        _bloqueos[username][1] = time.time()

    def _limpiar_fallo(self, username):
        if username in _bloqueos:
            del _bloqueos[username]

    def login(self, username, password):
        if self._verificar_bloqueo(username):
            return None, f"Demasiados intentos fallidos. Intenta de nuevo en {VENTANA_TIEMPO // 60} minutos"
        
        if not username or not password:
            return None, "Por favor ingresa usuario y contraseña"
        
        user = UserModel.authenticate(username, password)
        if not user:
            self._registrar_fallo(username)
            return None, "Usuario o contraseña incorrectos"
        if not user.get("activo", 1):
            return None, "Usuario desactivado"
        
        self._limpiar_fallo(username)
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
