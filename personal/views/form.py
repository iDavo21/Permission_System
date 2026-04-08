import flet as ft
import asyncio
from core.theme import theme_colors


class PersonalForm(ft.Container):
    def __init__(self, controller, on_save, on_cancel, dark_mode=True):
        super().__init__()
        self.expand = True
        self.controller = controller
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.dark_mode = dark_mode

        self._build_ui()

    def _build_ui(self):
        tc = theme_colors(self.dark_mode)

        self.txt_1er_nombre = self._input("1er Nombre *", expand=True)
        self.txt_2do_nombre = self._input("2do Nombre", expand=True)
        self.txt_1er_apellido = self._input("1er Apellido *", expand=True)
        self.txt_2do_apellido = self._input("2do Apellido", expand=True)
        self.txt_cedula = self._input("Cedula *", width=200)
        self.txt_telefono = self._input("Telefono *", width=200)
        self.txt_grado = self._input("Grado Jerarquico", width=200)
        self.txt_cargo = self._input("Cargo", expand=True)
        self.txt_dir_dom = self._input("Direccion Domiciliaria", expand=True)
        self.txt_dir_eme = self._input("Direccion de Emergencia", expand=True)

        self.lbl_error = ft.Text("", color=ft.Colors.RED_400, size=13, weight=ft.FontWeight.W_500)

        self.btn_save = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SAVE, color=ft.Colors.WHITE, size=20),
                ft.Text("Guardar", color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.CENTER_LEFT,
                end=ft.Alignment.CENTER_RIGHT,
                colors=["#1b5e20", "#2e7d32"],
            ),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=28, vertical=14),
            ink=True,
            on_click=self._on_save,
        )

        self.btn_cancel = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ARROW_BACK, color=tc["text_secondary"], size=20),
                ft.Text("Cancelar", color=tc["text_secondary"], size=14, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            border=ft.border.all(1, tc["border_primary"]),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=28, vertical=14),
            ink=True,
            on_click=lambda e: self.on_cancel(),
        )

        self.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.PERSON_ADD, color=ft.Colors.GREEN_400, size=26),
                                bgcolor=tc["icon_bg"],
                                border_radius=10,
                                padding=10,
                            ),
                            ft.Column([
                                ft.Text("Registrar Personal", size=20, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                                ft.Text("Complete los datos del miembro", size=12, color=tc["text_secondary"]),
                            ], spacing=2),
                        ], spacing=14),
                        ft.Container(expand=True),
                        self.btn_cancel,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(horizontal=24, vertical=16),
                    bgcolor=tc["header_bg"],
                    border=ft.border.all(1, tc["header_border"]),
                    border_radius=14,
                ),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Column([
                        self._section("Datos Personales", ft.Icons.PERSON, [
                            ft.Row([self.txt_1er_nombre, self.txt_2do_nombre], spacing=16),
                            ft.Row([self.txt_1er_apellido, self.txt_2do_apellido], spacing=16),
                            ft.Row([self.txt_cedula, self.txt_telefono], spacing=16),
                        ]),
                        self._section("Datos Laborales", ft.Icons.WORK, [
                            ft.Row([self.txt_grado, self.txt_cargo], spacing=16),
                        ]),
                        self._section("Direcciones", ft.Icons.HOME, [
                            ft.Row([self.txt_dir_dom, self.txt_dir_eme], spacing=16),
                        ]),
                        ft.Container(height=8),
                        self.lbl_error,
                        ft.Container(height=12),
                        self.btn_save,
                    ], spacing=12),
                    bgcolor=tc["bg_card"],
                    border_radius=14,
                    border=ft.border.all(1, tc["border_primary"]),
                    padding=ft.padding.all(24),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _input(self, label, expand=False, width=None):
        tc = theme_colors(self.dark_mode)
        kw = {
            "label": label,
            "border_radius": 10,
            "filled": True,
            "bgcolor": tc["input_bg"],
            "border_color": tc["input_border"],
            "focused_border_color": ft.Colors.GREEN_400,
            "color": tc["input_text"],
            "label_style": ft.TextStyle(color=tc["input_label"]),
            "content_padding": ft.padding.symmetric(horizontal=14, vertical=12),
        }
        if expand:
            kw["expand"] = True
        if width:
            kw["width"] = width
        return ft.TextField(**kw)

    def _section(self, title, icon, fields):
        tc = theme_colors(self.dark_mode)
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Icon(icon, color=ft.Colors.GREEN_400, size=18),
                    ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=tc["text_secondary"]),
                ], spacing=10),
                padding=ft.padding.only(bottom=8),
            ),
            *fields,
        ], spacing=10)

    def _on_save(self, e):
        self.lbl_error.value = ""

        if not self.txt_1er_nombre.value or not self.txt_1er_apellido.value or not self.txt_cedula.value:
            self.lbl_error.value = "1er Nombre, 1er Apellido y Cedula son obligatorios"
            self.update()
            return

        datos = {
            "nombres": "%s %s" % (self.txt_1er_nombre.value.strip(), self.txt_2do_nombre.value.strip()).strip(),
            "apellidos": "%s %s" % (self.txt_1er_apellido.value.strip(), self.txt_2do_apellido.value.strip()).strip(),
            "cedula": self.txt_cedula.value.strip(),
            "telefono": self.txt_telefono.value.strip(),
            "grado_jerarquia": self.txt_grado.value.strip(),
            "cargo": self.txt_cargo.value.strip(),
            "dir_domiciliaria": self.txt_dir_dom.value.strip(),
            "dir_emergencia": self.txt_dir_eme.value.strip(),
        }

        pid, err = self.controller.guardar(datos)
        if err:
            self.lbl_error.value = err
            self.update()
        else:
            self.on_save(pid)

    def did_mount(self):
        async def animate():
            await asyncio.sleep(0.05)
            self.opacity = 1
            self.update()
        asyncio.create_task(animate())
