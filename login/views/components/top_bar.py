import flet as ft


class TopBar(ft.Container):
    def __init__(self, on_search=None, on_toggle_filters=None, on_add_permission=None, on_confirm_logout=None, on_toggle_notifications=None, notification_count=0, usuario=None, on_open_export=None, on_backup=None, on_change_password=None):
        super().__init__()
        self.padding = ft.padding.all(15)
        self.bgcolor = ft.Colors.GREEN_800
        self.border = ft.border.all(2, ft.Colors.GREEN_900)
        self.border_radius = 10
        self.offset = ft.Offset(0, -0.5)
        self.animate_offset = ft.Animation(400, ft.AnimationCurve.EASE_OUT)
        self.opacity = 0
        self.animate_opacity = ft.Animation(400, ft.AnimationCurve.EASE_IN)

        nombre_usuario = usuario.get("nombre", "Admin") if usuario else "Admin"

        badge_notif = ft.Container(
            content=ft.Text(str(notification_count), size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            bgcolor=ft.Colors.RED_600 if notification_count > 0 else ft.Colors.TRANSPARENT,
            border_radius=10,
            width=20, height=20,
            alignment=ft.Alignment(0, 0),
            visible=notification_count > 0,
        )
        self._badge_notif = badge_notif

        btn_notificaciones = ft.Stack([
            ft.IconButton(
                icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                icon_color=ft.Colors.WHITE,
                icon_size=24,
                tooltip="Notificaciones",
                on_click=on_toggle_notifications,
            ),
            ft.Container(content=badge_notif, right=2, top=2),
        ], width=48, height=48)
        self.btn_notificaciones = btn_notificaciones

        buscador = ft.TextField(
            hint_text="Buscar por nombre o cedula...",
            hint_style=ft.TextStyle(color=ft.Colors.WHITE54),
            width=280,
            height=40,
            bgcolor=ft.Colors.WHITE24,
            color=ft.Colors.WHITE,
            border_color=ft.Colors.TRANSPARENT,
            border_radius=15,
            content_padding=ft.padding.only(left=15, right=15),
            text_size=15,
            prefix=ft.Icon(ft.Icons.SEARCH, color=ft.Colors.WHITE, size=20),
            cursor_color=ft.Colors.WHITE,
            on_change=lambda e: on_search(e.control.value) if on_search else None,
        )
        self.buscador = buscador

        btn_toggle_filtros = ft.IconButton(
            icon=ft.Icons.FILTER_LIST,
            icon_color=ft.Colors.WHITE,
            icon_size=22,
            tooltip="Mostrar filtros",
            on_click=on_toggle_filters,
        )
        self.btn_toggle_filtros = btn_toggle_filtros

        self.menu_abierto = False
        self._on_add_permission = on_add_permission
        self._on_open_export = on_open_export
        self._on_backup = on_backup
        self._on_change_password = on_change_password

        self._panel_menu = ft.Container(
            content=ft.Column([
                ft.GestureDetector(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PERSON_ADD_OUTLINED, color=ft.Colors.GREEN_300, size=16),
                            ft.Text("Agregar Permiso", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_300),
                        ], spacing=8),
                        padding=ft.padding.symmetric(horizontal=8, vertical=6),
                        border_radius=6,
                    ),
                    on_tap=lambda e: self._on_add_permission() if self._on_add_permission else None,
                    mouse_cursor=ft.MouseCursor.CLICK,
                ),
                ft.GestureDetector(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.DOWNLOAD_OUTLINED, color=ft.Colors.CYAN_300, size=16),
                            ft.Text("Exportar Datos", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
                        ], spacing=8),
                        padding=ft.padding.symmetric(horizontal=8, vertical=6),
                        border_radius=6,
                    ),
                    on_tap=lambda e: self._on_open_export() if self._on_open_export else None,
                    mouse_cursor=ft.MouseCursor.CLICK,
                ),
                ft.GestureDetector(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.BACKUP_OUTLINED, color=ft.Colors.AMBER_300, size=16),
                            ft.Text("Backup BD", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300),
                        ], spacing=8),
                        padding=ft.padding.symmetric(horizontal=8, vertical=6),
                        border_radius=6,
                    ),
                    on_tap=lambda e: self._on_backup() if self._on_backup else None,
                    mouse_cursor=ft.MouseCursor.CLICK,
                ),
                ft.GestureDetector(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LOCK_OUTLINE, color=ft.Colors.PURPLE_300, size=16),
                            ft.Text("Cambiar Contrasena", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_300),
                        ], spacing=8),
                        padding=ft.padding.symmetric(horizontal=8, vertical=6),
                        border_radius=6,
                    ),
                    on_tap=lambda e: self._on_change_password() if self._on_change_password else None,
                    mouse_cursor=ft.MouseCursor.CLICK,
                ),
            ], spacing=2),
            bgcolor=ft.Colors.GREEN_800,
            border=ft.border.all(1, ft.Colors.GREEN_600),
            border_radius=10,
            padding=12,
            width=200,
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=2, color=ft.Colors.BLACK54),
        )

        btn_menu = ft.IconButton(
            icon=ft.Icons.MENU,
            icon_color=ft.Colors.WHITE,
            icon_size=22,
            tooltip="Menu",
        )
        self.btn_menu = btn_menu

        btn_logout = ft.IconButton(
            icon=ft.Icons.LOGOUT,
            icon_color=ft.Colors.WHITE,
            icon_size=22,
            tooltip="Cerrar sesion",
            on_click=lambda e: on_confirm_logout() if on_confirm_logout else None,
        )

        self.content = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text("Panel de Administrador", size=20, weight="bold", color=ft.Colors.WHITE),
                    ft.Text(f"Sesion: {nombre_usuario}", size=11, color=ft.Colors.WHITE54),
                ], spacing=0),
                padding=ft.padding.only(left=15)
            ),
            ft.Row([
                btn_notificaciones,
                buscador,
                btn_toggle_filtros,
                btn_menu,
                btn_logout,
            ], spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def update_badge(self, count):
        self._badge_notif.visible = count > 0
        self._badge_notif.bgcolor = ft.Colors.RED_600 if count > 0 else ft.Colors.TRANSPARENT
        self._badge_notif.content.value = str(count)
