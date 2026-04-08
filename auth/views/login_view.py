import flet as ft
import asyncio


class LoginView(ft.Container):
    def __init__(self, on_login_click, on_toggle_theme=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.on_login_click = on_login_click
        self.on_toggle_theme = on_toggle_theme
        self.dark_mode = dark_mode

        self._build_ui()

    def _build_ui(self):
        tc = self._colors()

        self.username = ft.TextField(
            label="Usuario",
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            border_radius=12,
            filled=True,
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            focused_border_color=ft.Colors.GREEN_400,
            color=tc["text_primary"],
            label_style=ft.TextStyle(color=tc["text_secondary"]),
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        )

        self.password = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border_radius=12,
            filled=True,
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            focused_border_color=ft.Colors.GREEN_400,
            color=tc["text_primary"],
            label_style=ft.TextStyle(color=tc["text_secondary"]),
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        )

        self.mensaje = ft.Text("", color=ft.Colors.RED_400, size=13, weight=ft.FontWeight.W_500)

        self.login_button = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOGIN, color=ft.Colors.WHITE, size=20),
                ft.Text("Iniciar Sesión", color=ft.Colors.WHITE, size=15, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.CENTER_LEFT,
                end=ft.Alignment.CENTER_RIGHT,
                colors=["#1b5e20", "#2e7d32", "#388e3c"],
            ),
            border_radius=12,
            padding=ft.padding.symmetric(vertical=16),
            ink=True,
            on_click=self.handle_login,
        )

        theme_icon = ft.Icons.DARK_MODE_OUTLINED if self.dark_mode else ft.Icons.LIGHT_MODE_OUTLINED
        self.theme_btn = ft.Container(
            content=ft.Icon(theme_icon, color=tc["text_secondary"], size=22),
            padding=10,
            border_radius=10,
            ink=True,
            on_click=self._toggle_theme,
        )

        branding_panel = ft.Container(
            content=ft.Column([
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Stack([
                        ft.Container(
                            content=ft.Icon(ft.Icons.MILITARY_TECH, size=80, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                            border_radius=24,
                            padding=24,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(
                            content=ft.Icon(ft.Icons.SHIELD, size=32, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            border_radius=50,
                            padding=12,
                            right=0,
                            bottom=-10,
                        ),
                    ]),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(height=30),
                ft.Text("Control de Personal", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Container(height=8),
                ft.Text("Sistema de gestión para unidades\nmilitares", size=14, color=ft.Colors.WHITE70, text_align=ft.TextAlign.CENTER),
                ft.Container(height=40),
                ft.Row([
                    self._stat_badge("Permisos", ft.Icons.ASSIGNMENT),
                    ft.Container(width=12),
                    self._stat_badge("Comisiones", ft.Icons.BUSINESS_CENTER),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(expand=True),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=["#0d3b0f", "#1b5e20", "#2e7d32"],
            ),
            width=400,
            padding=ft.padding.symmetric(horizontal=40, vertical=50),
        )

        form_panel = ft.Container(
            content=ft.Column([
                ft.Container(expand=True),
                ft.Column([
                    ft.Text("Bienvenido", size=32, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                    ft.Text("Inicia sesión para continuar", size=14, color=tc["text_secondary"]),
                    ft.Container(height=35),
                    self.username,
                    ft.Container(height=12),
                    self.password,
                    ft.Container(height=8),
                    self.mensaje,
                    ft.Container(height=20),
                    self.login_button,
                    ft.Container(height=20),
                    ft.Text("v2.0 — Sistema de Gestión de Personal", size=11, color=tc["text_tertiary"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.START, spacing=0),
                ft.Container(expand=True),
            ], spacing=0),
            padding=ft.padding.only(left=60, right=60, top=20, bottom=40),
        )

        self._branding_wrapper = ft.Container(
            content=branding_panel,
            opacity=0,
            offset=ft.Offset(-0.1, 0),
            animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
            animate_offset=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
        )

        self._form_wrapper = ft.Container(
            content=form_panel,
            opacity=0,
            offset=ft.Offset(0.1, 0),
            animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
            animate_offset=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
        )

        self.content = ft.Stack([
            ft.Row([
                self._branding_wrapper,
                self._form_wrapper,
            ], expand=True),
            ft.Container(
                content=self.theme_btn,
                right=16,
                top=16,
            ),
        ], expand=True)

    def _colors(self):
        if self.dark_mode:
            return {
                "text_primary": ft.Colors.WHITE,
                "text_secondary": ft.Colors.GREY_400,
                "text_tertiary": ft.Colors.GREY_600,
                "input_bg": "#1e1e1e",
                "input_border": "#333333",
            }
        else:
            return {
                "text_primary": ft.Colors.BLACK87,
                "text_secondary": ft.Colors.GREY_600,
                "text_tertiary": ft.Colors.GREY_400,
                "input_bg": ft.Colors.GREY_100,
                "input_border": ft.Colors.GREY_300,
            }

    def _stat_badge(self, text, icon):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=16, color=ft.Colors.WHITE70),
                ft.Text(text, size=12, color=ft.Colors.WHITE70),
            ], spacing=6),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
        )

    def _toggle_theme(self, e):
        if self.on_toggle_theme:
            self.on_toggle_theme()
            self.dark_mode = not self.dark_mode
            self._build_ui()
            self.update()
            self._animate_in()

    def handle_login(self, e):
        self.on_login_click(self.username.value, self.password.value)

    def show_error(self, message):
        self.mensaje.value = message
        self.update()

    def _animate_in(self):
        async def animate():
            await asyncio.sleep(0.05)
            self._branding_wrapper.opacity = 1
            self._branding_wrapper.offset = ft.Offset(0, 0)
            self._form_wrapper.opacity = 1
            self._form_wrapper.offset = ft.Offset(0, 0)
            self.update()
        asyncio.create_task(animate())

    def did_mount(self):
        self._animate_in()
