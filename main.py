import flet as ft
from auth.controller import AuthController
from auth.views.login_view import LoginView
from personal.controller import PersonalController
from personal.views.dashboard import PersonalDashboard
from personal.views.form import PersonalForm
from permisos.controller import PermisosController
from permisos.views.dashboard import AdminView
from permisos.views.form import PermissionView
from permisos.views.detail_view import DetailView
from comisiones.controller import ComisionesController
from comisiones.views.dashboard import ComisionesDashboard
from comisiones.views.form import ComisionForm
from core.backup import crear_backup
from core.logger import logger
from core.theme import apply_page_theme, theme_colors
from core.components.sidebar import Sidebar


class MainApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Control de Personal"
        self.page.window.min_width = 1000
        self.page.window.min_height = 650
        self.page.window.width = 1280
        self.page.window.height = 800
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.DARK
        self.dark_mode = True
        apply_page_theme(self.page, is_dark=True)

        self.auth_ctrl = AuthController()
        self.personal_ctrl = PersonalController()
        self.permisos_ctrl = PermisosController()
        self.comisiones_ctrl = ComisionesController()

        self.usuario_actual = None
        self.current_section = "personal"
        self.sidebar = None
        self.content_area = None
        self.main_layout = None

        self.mostrar_login()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        apply_page_theme(self.page, is_dark=self.dark_mode)
        if self.main_layout:
            self.sidebar.rebuild(dark_mode=self.dark_mode)
            self._load_section_content(self.current_section)
            self.page.update()

    def _build_sidebar(self):
        self.sidebar = Sidebar(
            active_section=self.current_section,
            on_navigate=self._on_sidebar_navigate,
            on_logout=self.mostrar_login,
            on_toggle_theme=self.toggle_theme,
            dark_mode=self.dark_mode,
        )

    def _build_main_layout(self):
        self._build_sidebar()
        
        self.content_area = ft.Container(
            content=ft.Container(),
            expand=True,
            padding=0,
        )

        self.main_layout = ft.Row(
            controls=[
                self.sidebar,
                self.content_area,
            ],
            spacing=0,
            expand=True,
        )

    def _load_section_content(self, section):
        self.current_section = section
        self.sidebar.update_active(section)
        
        if section == "personal":
            self._build_personal_content()
        elif section == "permisos":
            self._build_permisos_content()
        elif section == "comisiones":
            self._build_comisiones_content()
        
        self.content_area.content = ft.Container(
            content=self.content_area.content,
            expand=True,
            padding=0,
        )
        self.page.update()

    def _build_personal_content(self):
        dashboard = PersonalDashboard(
            controller=self.personal_ctrl,
            on_navigate_permisos=self._navigate_to_permisos_from_section,
            on_navigate_comisiones=self._navigate_to_comisiones_from_section,
            on_add_personal=self.mostrar_form_personal,
            dark_mode=self.dark_mode,
        )
        self.content_area.content = dashboard

    def _build_permisos_content(self):
        permisos = self.permisos_ctrl.obtener_todos()
        admin_view = AdminView(
            on_add_permission=self.mostrar_form_permiso,
            lista_permisos=permisos,
            on_edit=self.mostrar_form_edicion_permiso,
            on_delete=self.eliminar_permiso,
            on_view_detail=self.mostrar_detalle_permiso,
            personal_id=None,
            dark_mode=self.dark_mode,
        )
        self.content_area.content = admin_view

    def _build_comisiones_content(self):
        dashboard = ComisionesDashboard(
            controller=self.comisiones_ctrl,
            personal_id=None,
            on_back=self._go_to_personal,
            on_add=self.mostrar_form_comision,
            on_edit=self.mostrar_form_edicion_comision,
            on_delete=self.eliminar_comision,
            on_view_detail=self.mostrar_detalle_comision,
            dark_mode=self.dark_mode,
        )
        self.content_area.content = dashboard

    def _on_sidebar_navigate(self, section):
        self._load_section_content(section)

    def _navigate_to_permisos_from_section(self, personal_id=None):
        self._load_section_content("permisos")

    def _navigate_to_comisiones_from_section(self, personal_id=None):
        self._load_section_content("comisiones")

    def _go_to_personal(self):
        self._load_section_content("personal")

    def limpiar_pagina(self):
        self.page.controls.clear()
        if hasattr(self.page, "dialog") and self.page.dialog:
            self.page.dialog.open = False
        self.page.update()

    def mostrar_login(self):
        self.usuario_actual = None
        self.current_section = "personal"
        
        def builder():
            login = LoginView(
                on_login_click=self.intentar_login,
                on_toggle_theme=self.toggle_theme,
                dark_mode=self.dark_mode
            )
            self.page.add(login)
        self.limpiar_pagina()
        builder()
        self.page.update()

    def intentar_login(self, username, password):
        user, err = self.auth_ctrl.login(username, password)
        if err or not user:
            for ctrl in self.page.controls:
                if hasattr(ctrl, "show_error"):
                    ctrl.show_error(err or "Credenciales invalidas")
                    break
            return

        self.usuario_actual = user
        logger.info("Usuario %s inicio sesion" % username)
        self.mostrar_main_dashboard()

    def mostrar_main_dashboard(self):
        def builder():
            self._build_main_layout()
            self._load_section_content(self.current_section)
            self.page.add(self.main_layout)
        self.limpiar_pagina()
        builder()
        self.page.update()

    def mostrar_form_personal(self):
        def builder():
            form = PersonalForm(
                controller=self.personal_ctrl,
                on_save=self._on_personal_saved,
                on_cancel=self._go_to_personal,
                dark_mode=self.dark_mode,
            )
            self.content_area.content = form
            self.page.update()
        builder()

    def _on_personal_saved(self, personal_id):
        self._go_to_personal()
        self.page.snack_bar = ft.SnackBar(ft.Text("Personal registrado correctamente"), open=True)
        self.page.update()

    def mostrar_form_permiso(self, personal_id=None, permiso_id=None):
        def builder():
            form = PermissionView(
                on_back=self._go_to_permisos,
                on_save=self.guardar_permiso,
                personal_id=personal_id,
                permiso_id=permiso_id,
                dark_mode=self.dark_mode,
            )
            self.content_area.content = form
            self.page.update()
        builder()

    def mostrar_form_edicion_permiso(self, permiso_id):
        permiso = self.permisos_ctrl.obtener_por_id(permiso_id)
        if permiso:
            self.mostrar_form_permiso(personal_id=permiso.get("personal_id"), permiso_id=permiso_id)

    def guardar_permiso(self, datos):
        permiso_id = datos.get("id")
        if permiso_id:
            return self.permisos_ctrl.actualizar(permiso_id, datos)
        else:
            return self.permisos_ctrl.guardar(datos)

    def eliminar_permiso(self, permiso_id):
        ok, err = self.permisos_ctrl.eliminar(permiso_id)
        if ok:
            logger.info("Permiso %d eliminado" % permiso_id)
            self._go_to_permisos()
        else:
            if self.page:
                self.page.snack_bar = ft.SnackBar(ft.Text(err), bgcolor=ft.Colors.RED_700, open=True)
                self.page.update()

    def mostrar_detalle_permiso(self, permiso_id):
        permiso = self.permisos_ctrl.obtener_por_id(permiso_id)
        if permiso:
            def builder():
                detail = DetailView(
                    datos=permiso,
                    on_back=self._go_to_permisos,
                    on_edit=self.mostrar_form_edicion_permiso,
                    dark_mode=self.dark_mode,
                )
                self.content_area.content = detail
                self.page.update()
            builder()

    def _go_to_permisos(self):
        self._load_section_content("permisos")

    def mostrar_form_comision(self, personal_id=None, comision_id=None):
        def builder():
            form = ComisionForm(
                controller=self.comisiones_ctrl,
                personal_id=personal_id,
                comision_id=comision_id,
                on_save=self._go_to_comisiones,
                on_back=self._go_to_comisiones,
                dark_mode=self.dark_mode,
            )
            self.content_area.content = form
            self.page.update()
        builder()

    def mostrar_form_edicion_comision(self, comision_id):
        comision = self.comisiones_ctrl.obtener_por_id(comision_id)
        if comision:
            self.mostrar_form_comision(personal_id=comision.get("personal_id"), comision_id=comision_id)

    def eliminar_comision(self, comision_id):
        ok, err = self.comisiones_ctrl.eliminar(comision_id)
        if ok:
            logger.info("Comision %d eliminada" % comision_id)
            self._go_to_comisiones()
        else:
            if self.page:
                self.page.snack_bar = ft.SnackBar(ft.Text(err), bgcolor=ft.Colors.RED_700, open=True)
                self.page.update()

    def mostrar_detalle_comision(self, comision_id):
        pass

    def _go_to_comisiones(self):
        self._load_section_content("comisiones")

    def exportar_permisos(self, permisos, template_key):
        pass

    def crear_backup(self):
        try:
            nombre = crear_backup()
            logger.info("Backup creado: %s" % nombre)
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("Backup creado: %s" % nombre),
                    bgcolor=ft.Colors.GREEN_700,
                    open=True,
                )
                self.page.update()
        except Exception as e:
            logger.error("Error al crear backup: %s" % str(e))
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("Error al crear backup: %s" % str(e)),
                    bgcolor=ft.Colors.RED_700,
                    open=True,
                )
                self.page.update()

    def cambiar_password(self):
        pass


def main(page: ft.Page):
    MainApp(page)


if __name__ == "__main__":
    ft.run(main)
