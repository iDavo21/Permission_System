import flet as ft
import asyncio

class LoginView(ft.Container):
    def __init__(self, on_login_click):
        super().__init__()
        self.expand = True
        self.alignment = ft.Alignment.CENTER
        self.on_login_click = on_login_click

        self.username = ft.TextField(
            label="Usuario", 
            width=320,
            border=ft.InputBorder.UNDERLINE,
            prefix_icon=ft.Icons.PERSON_OUTLINE,
        )
        
        self.password = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=320,
            border=ft.InputBorder.UNDERLINE,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
        )

        self.mensaje = ft.Text(color=ft.Colors.RED_400, size=13)
        
        self.login_button = ft.ElevatedButton(
            "Iniciar Sesión",
            width=320,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_800,
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=15
            ),
            on_click=self.handle_login
        )

        card = ft.Card(
            elevation=5,
            shape=ft.RoundedRectangleBorder(radius=15),
            content=ft.Container(
                padding=ft.padding.only(top=40, bottom=40, left=30, right=30),
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=50, color=ft.Colors.GREEN_800),
                        ft.Text("Bienvenido", size=28, weight=ft.FontWeight.BOLD),
                        ft.Text("Inicia sesión en tu cuenta", color=ft.Colors.GREY_500, size=14),
                        ft.Container(height=20),
                        self.username,
                        self.password,
                        ft.Container(height=10),
                        self.login_button,
                        self.mensaje
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    tight=True
                )
            )
        )

        self._card_wrapper = ft.Container(
            content=card,
            opacity=0,
            offset=ft.Offset(0, 0.15),
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN),
            animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
        )

        self.content = self._card_wrapper

    def handle_login(self, e):
        self.on_login_click(self.username.value, self.password.value)

    def show_error(self, message):
        self.mensaje.value = message
        self.update()

    def did_mount(self):
        async def animate():
            await asyncio.sleep(0.05)
            self._card_wrapper.opacity = 1
            self._card_wrapper.offset = ft.Offset(0, 0)
            self.update()
        asyncio.create_task(animate())
