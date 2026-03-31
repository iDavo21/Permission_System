from models.user_model import UserModel
from models.permiso_model import PermisoModel
from views.admin_view import AdminView
from views.permission_view import PermissionView

class MainController:
    def __init__(self, page):
        self.page = page
        self.login_view = None
        # Garantizar que la tabla exista al arrancar
        PermisoModel.create_table()

    def set_login_view(self, login_view):
        self.login_view = login_view

    def attempt_login(self, username, password):
        if UserModel.authenticate(username, password):
            self.show_admin_panel()
        else:
            if self.login_view:
                self.login_view.show_error("Usuario o contraseña incorrectos")

    # ── PANEL PRINCIPAL ───────────────────────────────────────────────────────
    def show_admin_panel(self):
        self.page.clean()
        permisos = PermisoModel.get_all()
        admin_view = AdminView(
            on_add_permission=self.show_permission_panel,
            lista_permisos=permisos,
            on_edit=self.show_edit_panel,
            on_delete=self.delete_permiso,
        )
        self.page.add(admin_view)
        self.page.update()

    # ── CREAR PERMISO ─────────────────────────────────────────────────────────
    def show_permission_panel(self):
        self.page.clean()
        permission_view = PermissionView(
            on_save=self.save_permiso,
            on_back=self.show_admin_panel,
        )
        self.page.add(permission_view)
        self.page.update()

    def save_permiso(self, datos: dict):
        PermisoModel.save(datos)
        self.show_admin_panel()

    # ── EDITAR PERMISO ────────────────────────────────────────────────────────
    def show_edit_panel(self, permiso_id: int):
        self.page.clean()
        datos = PermisoModel.get_by_id(permiso_id)
        permission_view = PermissionView(
            on_save=lambda d: self.update_permiso(permiso_id, d),
            on_back=self.show_admin_panel,
            datos_iniciales=datos,
            permiso_id=permiso_id,
        )
        self.page.add(permission_view)
        self.page.update()

    def update_permiso(self, permiso_id: int, datos: dict):
        PermisoModel.update(permiso_id, datos)
        self.show_admin_panel()

    # ── ELIMINAR PERMISO ──────────────────────────────────────────────────────
    def delete_permiso(self, permiso_id: int):
        PermisoModel.delete(permiso_id)
        self.show_admin_panel()
