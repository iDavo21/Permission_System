class UserModel:
    # Credenciales (por ahora quemadas en el código)
    ADMIN_USER = "admin"
    ADMIN_PASS = "1234"

    @classmethod
    def authenticate(cls, username, password):
        """
        Verifica si las credenciales de un usuario son válidas.
        """
        return username == cls.ADMIN_USER and password == cls.ADMIN_PASS
