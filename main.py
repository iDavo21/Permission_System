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
from core.components.shortcuts import show_shortcuts_help


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

        self.page.on_keyboard_event = self._handle_keyboard
        self.page.update()

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
            on_edit_personal=self.mostrar_form_edicion_personal,
            on_delete_personal=self.eliminar_personal,
            dark_mode=self.dark_mode,
        )
        self._personal_dashboard = dashboard
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
        self._permisos_dashboard = admin_view
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
        self._comisiones_dashboard = dashboard
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

    def mostrar_form_personal(self, personal_id=None):
        persona = None
        if personal_id:
            persona = self.personal_ctrl.obtener_por_id(personal_id)
        
        def builder():
            form = PersonalForm(
                controller=self.personal_ctrl,
                on_save=self._on_personal_saved,
                on_cancel=self._go_to_personal,
                personal_id=personal_id,
                datos_iniciales=persona,
                dark_mode=self.dark_mode,
            )
            self.content_area.content = form
            self.page.update()
        builder()

    def _on_personal_saved(self, personal_id):
        self._go_to_personal()

    def mostrar_form_edicion_personal(self, personal_id):
        persona = self.personal_ctrl.obtener_por_id(personal_id)
        if persona:
            self.mostrar_form_personal(personal_id=personal_id)

    def eliminar_personal(self, personal_id):
        persona = self.personal_ctrl.obtener_por_id(personal_id)
        nombre = ""
        if persona:
            nombre = "%s %s" % (persona.get("nombres", ""), persona.get("apellidos", ""))

        tc = theme_colors(self.dark_mode)

        n_permisos = len(self.permisos_ctrl.obtener_por_personal(personal_id))
        n_comisiones = len(self.comisiones_ctrl.obtener_por_personal(personal_id))

        lineas = [ft.Text("Esta accion eliminara permanentemente:", size=13, color=tc["text_secondary"])]
        if n_permisos > 0:
            lineas.append(ft.Row([
                ft.Icon(ft.Icons.EVENT_NOTE, size=16, color=ft.Colors.AMBER_400),
                ft.Text("%d permiso(s) asociado(s)" % n_permisos, size=13, color=ft.Colors.AMBER_400),
            ], spacing=6))
        if n_comisiones > 0:
            lineas.append(ft.Row([
                ft.Icon(ft.Icons.BUSINESS_CENTER, size=16, color=ft.Colors.AMBER_400),
                ft.Text("%d comision(es) asociada(s)" % n_comisiones, size=13, color=ft.Colors.AMBER_400),
            ], spacing=6))
        lineas.append(ft.Text("Esta accion no se puede deshacer.", size=12, color=ft.Colors.RED_400, weight=ft.FontWeight.W_500))

        def confirmar(e):
            self.page.pop_dialog()

            # Eliminacion en cascada: permisos -> comisiones -> personal
            self.permisos_ctrl.eliminar_por_personal(personal_id)
            self.comisiones_ctrl.eliminar_por_personal(personal_id)
            ok, err = self.personal_ctrl.eliminar(personal_id)

            if ok:
                self.page.snack_bar = ft.SnackBar(
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                        ft.Text("Personal \"%s\" eliminado correctamente" % nombre.strip(), color=ft.Colors.WHITE),
                    ], spacing=10),
                    open=True,
                    bgcolor=ft.Colors.GREEN_700,
                    duration=3000,
                )
                self._go_to_personal()
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Row([
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE, size=20),
                        ft.Text(err, color=ft.Colors.WHITE),
                    ], spacing=10),
                    open=True,
                    bgcolor=ft.Colors.RED_700,
                    duration=4000,
                )
            self.page.update()

        def cancelar(e):
            self.page.pop_dialog()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER_400, size=22),
                ft.Text("Eliminar Personal", color=tc["text_primary"], weight=ft.FontWeight.BOLD, size=16),
            ], spacing=10),
            content=ft.Container(
                width=380,
                content=ft.Column(lineas, spacing=8, tight=True),
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.ElevatedButton(
                    "Eliminar Todo",
                    on_click=confirmar,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED_700,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=tc["bg_dialog"],
        )

        self.page.show_dialog(dialogo)

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
            self.page.snack_bar = ft.SnackBar(
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                    ft.Text("Permiso eliminado correctamente", color=ft.Colors.WHITE),
                ], spacing=10),
                bgcolor=ft.Colors.GREEN_700,
                duration=3000,
                open=True,
            )
            self._go_to_permisos()
        else:
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    ft.Row([
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE, size=20),
                        ft.Text(err, color=ft.Colors.WHITE),
                    ], spacing=10),
                    bgcolor=ft.Colors.RED_700,
                    duration=4000,
                    open=True,
                )
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
            self.page.snack_bar = ft.SnackBar(
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                    ft.Text("Comisión eliminada correctamente", color=ft.Colors.WHITE),
                ], spacing=10),
                bgcolor=ft.Colors.GREEN_700,
                duration=3000,
                open=True,
            )
            self._go_to_comisiones()
        else:
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    ft.Row([
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE, size=20),
                        ft.Text(err, color=ft.Colors.WHITE),
                    ], spacing=10),
                    bgcolor=ft.Colors.RED_700,
                    duration=4000,
                    open=True,
                )
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
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                        ft.Text("Backup creado: %s" % nombre, color=ft.Colors.WHITE),
                    ], spacing=10),
                    bgcolor=ft.Colors.GREEN_700,
                    duration=3000,
                    open=True,
                )
                self.page.update()
        except Exception as e:
            logger.error("Error al crear backup: %s" % str(e))
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    ft.Row([
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE, size=20),
                        ft.Text("Error al crear backup: %s" % str(e), color=ft.Colors.WHITE),
                    ], spacing=10),
                    bgcolor=ft.Colors.RED_700,
                    duration=4000,
                    open=True,
                )
                self.page.update()

    def cambiar_password(self):
        pass

    def _handle_keyboard(self, e: ft.KeyboardEvent):
        if not self.main_layout:
            return

        if e.key == "Escape":
            if hasattr(self.page, "dialog") and self.page.dialog and self.page.dialog.open:
                self.page.dialog.open = False
                self.page.update()
            return

        if e.ctrl and e.key == "h":
            show_shortcuts_help(self.page, dark_mode=self.dark_mode)
            return

        if e.ctrl and e.key == "b":
            self.crear_backup()
            return

        if e.key == "F1":
            self.toggle_theme()
            return

        if e.ctrl and e.key == "1":
            self._go_to_personal()
            return

        if e.ctrl and e.key == "2":
            self._go_to_permisos()
            return

        if e.ctrl and e.key == "3":
            self._go_to_comisiones()
            return

        if e.ctrl and self.current_section == "personal":
            if e.key == "f" and hasattr(self, '_personal_dashboard'):
                self._personal_dashboard.search_field.focus()
                self.page.update()
            elif e.key == "n":
                self.mostrar_form_personal()
            return

        if e.ctrl and self.current_section == "permisos":
            if e.key == "f" and hasattr(self, '_permisos_dashboard'):
                self._permisos_dashboard.search_field.focus()
                self.page.update()
            return

        if e.ctrl and self.current_section == "comisiones":
            if e.key == "f" and hasattr(self, '_comisiones_dashboard'):
                self._comisiones_dashboard.search_field.focus()
                self.page.update()
            return


def main(page: ft.Page):
    MainApp(page)

 
if __name__ == "__main__":
    ft.run(main)
