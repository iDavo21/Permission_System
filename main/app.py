import flet as ft
from core.logger import logger
from core.theme import apply_page_theme, theme_colors
from core.preferencias import cargar_preferencias, set_preferencia
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
        
        self.preferencias = cargar_preferencias()
        self.dark_mode = self.preferencias.get("theme_oscuro", True)
        apply_page_theme(self.page, is_dark=self.dark_mode)

        from auth.controller import AuthController
        from personal.controller import PersonalController
        from permisos.controller import PermisosController
        from comisiones.controller import ComisionesController
        from situaciones_irregulares.controller import SituacionesController
        
        self.auth_ctrl = AuthController()
        self.personal_ctrl = PersonalController()
        self.permisos_ctrl = PermisosController()
        self.comisiones_ctrl = ComisionesController()
        self.situaciones_ctrl = SituacionesController()

        self.usuario_actual = None
        self.current_section = "inicio"
        self.sidebar = None
        self.content_area = None
        self.main_layout = None
        
        self._comisiones_dashboard = None
        
        self.export_file_picker = None

        self.mostrar_login()
        self.page.on_keyboard_event = self._handle_keyboard
        self.page.update()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        apply_page_theme(self.page, is_dark=self.dark_mode)
        set_preferencia("theme_oscuro", self.dark_mode)
        
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
        tc = theme_colors(self.dark_mode)
        self.content_area = ft.Container(
            content=None,
            expand=True,
            padding=0,
            margin=0,
            bgcolor=tc["bg_primary"],
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )
        self.main_layout = ft.Row(
            controls=[self.sidebar, self.content_area],
            spacing=0,
            expand=True,
        )

    def _load_section_content(self, section):
        self.current_section = section
        self.sidebar.update_active(section)
        
        from main.sections import inicio, personal, permisos, comisiones, situaciones, configuracion
        
        if section == "inicio":
            self.content_area.content = inicio.build(self)
        elif section == "personal":
            self.content_area.content = personal.build(self)
        elif section == "permisos":
            self.content_area.content = permisos.build(self)
        elif section == "comisiones":
            self.content_area.content = comisiones.build(self)
        elif section == "situaciones":
            self.content_area.content = situaciones.build(self)
        elif section == "configuracion":
            self.content_area.content = configuracion.build(self)
        
        self.page.update()

    def _on_sidebar_navigate(self, section):
        self._load_section_content(section)

    def limpiar_pagina(self):
        self.page.controls.clear()
        self.page.update()

    def mostrar_login(self, e=None):
        self.page.controls.clear()
        self.usuario_actual = None
        self.current_section = "inicio"
        
        from auth.views.login_view import LoginView
        login = LoginView(
            on_login_click=self.intentar_login,
            on_toggle_theme=self.toggle_theme,
            dark_mode=self.dark_mode
        )
        self.page.add(login)
        self.page.update()

    def intentar_login(self, username, password):
        from auth.views.login_view import LoginView
        from core.components.common import NotificationService
        
        user, err = self.auth_ctrl.login(username, password)
        
        if err or not user:
            if hasattr(self, 'page') and self.page:
                login_view = self.page.controls[0] if self.page.controls else None
                if login_view and hasattr(login_view, 'show_error'):
                    login_view.show_error(err or "Credenciales inválidas")
            return

        self.usuario_actual = user
        logger.info("Usuario %s inició sesión" % username)
        self.mostrar_main_dashboard()

    def mostrar_main_dashboard(self):
        def builder():
            self._build_main_layout()
            self._load_section_content(self.current_section)
            self.page.add(self.main_layout)
        self.limpiar_pagina()
        builder()
        self._verificar_permisos_por_expirar()
        self.page.update()

    def _verificar_permisos_por_expirar(self):
        from core.estado_utils import fecha_a_datetime
        from core.preferencias import get_preferencia
        from core.theme import theme_colors
        from datetime import datetime
        
        notificaciones_activas = get_preferencia("notificaciones_activadas", True)
        dias_anticipacion = get_preferencia("dias_anticipacion", 3)
        
        if not notificaciones_activas:
            return
        
        permisos = self.permisos_ctrl.obtener_todos()
        hoy = datetime.now().date()
        vence_hoy, vence_manana, vence_proximos = [], [], []
        
        for p in permisos:
            fecha_hasta = p.get("fecha_hasta", "")
            if fecha_hasta:
                fecha = fecha_a_datetime(fecha_hasta)
                if fecha:
                    diff = (fecha - hoy).days
                    if diff == 0:
                        vence_hoy.append({**p, "_dias_restantes": diff})
                    elif diff == 1:
                        vence_manana.append({**p, "_dias_restantes": diff})
                    elif 2 <= diff <= dias_anticipacion:
                        vence_proximos.append({**p, "_dias_restantes": diff})
        
        total = len(vence_hoy) + len(vence_manana) + len(vence_proximos)
        if total > 0:
            self._mostrar_dialogo_notificaciones(vence_hoy, vence_manana, vence_proximos)

    def _mostrar_dialogo_notificaciones(self, vence_hoy, vence_manana, vence_proximos):
        from core.theme import theme_colors
        tc = theme_colors(self.dark_mode)
        
        contenido = []
        if vence_hoy:
            contenido.append(ft.Text(f"⚠️ {len(vence_hoy)} permiso(s) expira(n) hoy:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400))
            for p in vence_hoy:
                contenido.append(ft.Text(f"  • {p.get('nombres', '')} {p.get('apellidos', '')} - Hasta: {p.get('fecha_hasta', '')}", size=12, color=tc["text_secondary"]))
            contenido.append(ft.Container(height=8))
        
        if vence_manana:
            contenido.append(ft.Text(f"⏰ {len(vence_manana)} permiso(s) expira(n) mañana:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400))
            for p in vence_manana:
                contenido.append(ft.Text(f"  • {p.get('nombres', '')} {p.get('apellidos', '')} - Hasta: {p.get('fecha_hasta', '')}", size=12, color=tc["text_secondary"]))
            contenido.append(ft.Container(height=8))
        
        if vence_proximos:
            contenido.append(ft.Text(f"📅 {len(vence_proximos)} permiso(s) expira(n) en los próximos días:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400))
            for p in vence_proximos:
                dias = p.get("_dias_restantes", "")
                contenido.append(ft.Text(f"  • {p.get('nombres', '')} {p.get('apellidos', '')} - Expira en {dias} día(s)", size=12, color=tc["text_secondary"]))

        def cerrar(e):
            self.page.pop_dialog()
            self.page.update()

        dialogo = ft.AlertDialog(
            modal=False,
            title=ft.Row([
                ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color=ft.Colors.AMBER_400, size=24),
                ft.Text("Permisos por Expirar", size=18, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
            ], spacing=10),
            content=ft.Column(contenido, tight=True, spacing=4),
            actions=[
                ft.ElevatedButton("Ver Permisos", on_click=lambda e: (self.page.pop_dialog(), self._load_section_content("permisos")),
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700, shape=ft.RoundedRectangleBorder(radius=8))),
                ft.TextButton("Cerrar", on_click=cerrar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=tc["bg_dialog"],
        )
        self.page.show_dialog(dialogo)

    def _go_to_personal(self):
        self._load_section_content("personal")

    def _go_to_permisos(self):
        self._load_section_content("permisos")

    def _go_to_comisiones(self):
        self._load_section_content("comisiones")

    def _go_to_situaciones(self):
        self._load_section_content("situaciones")

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
            from main.handlers.actions import crear_backup
            crear_backup(self)
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

    def mostrar_form_personal(self, personal_id=None):
        from main.handlers.forms import mostrar_form_personal
        mostrar_form_personal(self, personal_id)

    def mostrar_form_edicion_personal(self, personal_id):
        from main.handlers.forms import mostrar_form_personal
        mostrar_form_personal(self, personal_id)

    def eliminar_personal(self, personal_id):
        from main.handlers.actions import eliminar_personal
        eliminar_personal(self, personal_id)

    def mostrar_form_permiso(self, personal_id=None, permiso_id=None):
        from main.handlers.forms import mostrar_form_permiso
        mostrar_form_permiso(self, personal_id, permiso_id)

    def mostrar_form_edicion_permiso(self, permiso_id):
        from main.handlers.forms import mostrar_form_permiso
        permiso = self.permisos_ctrl.obtener_por_id(permiso_id)
        if permiso:
            mostrar_form_permiso(self, personal_id=permiso.get("personal_id"), permiso_id=permiso_id)

    def guardar_permiso(self, datos):
        permiso_id = datos.get("id")
        if permiso_id:
            return self.permisos_ctrl.actualizar(permiso_id, datos)
        else:
            return self.permisos_ctrl.guardar(datos)

    def eliminar_permiso(self, permiso_id):
        from main.handlers.actions import eliminar_permiso
        eliminar_permiso(self, permiso_id)

    def mostrar_detalle_permiso(self, permiso_id):
        from main.handlers.forms import mostrar_detalle_permiso
        mostrar_detalle_permiso(self, permiso_id)

    def mostrar_form_comision(self, personal_id=None, comision_id=None):
        from main.handlers.forms import mostrar_form_comision
        mostrar_form_comision(self, personal_id, comision_id)

    def mostrar_form_edicion_comision(self, comision_id):
        from main.handlers.forms import mostrar_form_comision
        mostrar_form_comision(self, comision_id=comision_id)

    def eliminar_comision(self, comision_id):
        from main.handlers.actions import eliminar_comision
        eliminar_comision(self, comision_id)

    def mostrar_detalle_comision(self, comision_id):
        from main.handlers.forms import mostrar_detalle_comision
        mostrar_detalle_comision(self, comision_id)

    def mostrar_form_situacion(self, personal_id=None, situacion_id=None):
        from main.handlers.forms import mostrar_form_situacion
        mostrar_form_situacion(self, personal_id, situacion_id)

    def mostrar_form_edicion_situacion(self, situacion_id):
        from main.handlers.forms import mostrar_form_situacion
        mostrar_form_situacion(self, situacion_id=situacion_id)

    def eliminar_situacion(self, situacion_id):
        from main.handlers.actions import eliminar_situacion
        eliminar_situacion(self, situacion_id)

    def mostrar_detalle_situacion(self, situacion_id):
        from main.handlers.forms import mostrar_detalle_situacion
        mostrar_detalle_situacion(self, situacion_id)


    def crear_backup(self):
        from main.handlers.actions import crear_backup
        crear_backup(self)

    def _guardar_preferencias_handler(self, e):
        from core.preferencias import set_preferencia
        set_preferencia("notificaciones_activadas", self.chk_notificaciones.value)
        set_preferencia("dias_anticipacion", int(self.drp_dias_anticipacion.value or 3))
        self.preferencias = {
            "notificaciones_activadas": self.chk_notificaciones.value,
            "dias_anticipacion": int(self.drp_dias_anticipacion.value or 3),
            "theme_oscuro": self.dark_mode,
        }
        self.page.snack_bar = ft.SnackBar(
            ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                ft.Text("Preferencias guardadas", color=ft.Colors.WHITE)], spacing=10),
            bgcolor=ft.Colors.GREEN_700, duration=2000, open=True,
        )
        self.page.update()

    def cambiar_password(self):
        from main.handlers.forms import mostrar_dialogo_cambiar_password
        mostrar_dialogo_cambiar_password(self)