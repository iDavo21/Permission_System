import flet as ft
import asyncio
from core.theme import theme_colors, create_input, create_primary_button, create_secondary_button
from core.constants import CEDULA_MIN, CEDULA_MAX, TELEFONO_MIN, TELEFONO_MAX


class PersonalForm(ft.Container):
    def __init__(self, controller, on_save, on_cancel, personal_id=None, datos_iniciales=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.padding = ft.padding.all(24)
        self.controller = controller
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.personal_id = personal_id
        self.datos_iniciales = datos_iniciales or {}
        self.dark_mode = dark_mode
        self.is_edit = personal_id is not None

        self._build_ui()

        if self.is_edit:
            self._populate_fields()

    def _build_ui(self):
        tc = theme_colors(self.dark_mode)

        self.txt_1er_nombre = self._input("1er Nombre *", expand=True)
        self.txt_2do_nombre = self._input("2do Nombre", expand=True)
        self.txt_1er_apellido = self._input("1er Apellido *", expand=True)
        self.txt_2do_apellido = self._input("2do Apellido", expand=True)
        self.txt_cedula = self._input("Cedula *", width=200, max_length=8, input_filter="number")
        self.txt_telefono = self._input("Telefono *", width=200, max_length=11, input_filter="number")
        self.txt_grado = self._input("Grado Jerarquico", width=200)
        self.txt_cargo = self._input("Cargo", expand=True)
        self.txt_dir_dom = self._input("Direccion Domiciliaria", expand=True)
        self.txt_dir_eme = self._input("Direccion de Emergencia", expand=True)

        self.lbl_error = ft.Text("", color=ft.Colors.RED_400, size=13, weight=ft.FontWeight.W_500)

        self.btn_save = create_primary_button("Guardar", icon=ft.Icons.SAVE, on_click=self._on_save, dark=self.dark_mode)
        self.btn_cancel = create_secondary_button("Cancelar", icon=ft.Icons.ARROW_BACK, on_click=lambda e: self.on_cancel(), dark=self.dark_mode)

        titulo = "Editar Personal" if self.is_edit else "Registrar Personal"
        subtitulo = "Modifique los datos del miembro" if self.is_edit else "Complete los datos del miembro"

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
                                ft.Text(titulo, size=20, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                                ft.Text(subtitulo, size=12, color=tc["text_secondary"]),
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

    def _input(self, label, expand=False, width=None, max_length=None, input_filter=None):
        return create_input(
            dark=self.dark_mode,
            label=label,
            expand=expand,
            width=width,
            max_length=max_length,
            input_filter=input_filter,
        )

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

    def _populate_fields(self):
        d = self.datos_iniciales
        if d and isinstance(d, dict):
            nombres = d.get("nombres", "").split(" ", 1)
            self.txt_1er_nombre.value = nombres[0] if nombres else ""
            self.txt_2do_nombre.value = nombres[1] if len(nombres) > 1 else ""
            
            apellidos = d.get("apellidos", "").split(" ", 1)
            self.txt_1er_apellido.value = apellidos[0] if apellidos else ""
            self.txt_2do_apellido.value = apellidos[1] if len(apellidos) > 1 else ""
            
            self.txt_cedula.value = str(d.get("cedula", ""))
            self.txt_telefono.value = str(d.get("telefono", ""))
            self.txt_grado.value = str(d.get("grado_jerarquia", ""))
            self.txt_cargo.value = str(d.get("cargo", ""))
            self.txt_dir_dom.value = str(d.get("dir_domiciliaria", ""))
            self.txt_dir_eme.value = str(d.get("dir_emergencia", ""))

    def _on_save(self, e):
        self.lbl_error.value = ""

        if not self.txt_1er_nombre.value or not self.txt_1er_apellido.value or not self.txt_cedula.value:
            self.lbl_error.value = "1er Nombre, 1er Apellido y Cedula son obligatorios"
            try:
                self.update()
            except RuntimeError:
                pass
            return

        cedula_val = self.txt_cedula.value or ""
        telefono_val = self.txt_telefono.value or ""

        if len(cedula_val) < CEDULA_MIN or len(cedula_val) > CEDULA_MAX:
            self.lbl_error.value = f"La cédula debe tener entre {CEDULA_MIN} y {CEDULA_MAX} dígitos"
            try:
                self.update()
            except RuntimeError:
                pass
            return

        if telefono_val and (len(telefono_val) < TELEFONO_MIN or len(telefono_val) > TELEFONO_MAX):
            self.lbl_error.value = f"El teléfono debe tener entre {TELEFONO_MIN} y {TELEFONO_MAX} dígitos"
            try:
                self.update()
            except RuntimeError:
                pass
            return

        def _v(val):
            if isinstance(val, tuple):
                val = " ".join(str(v) for v in val)
            return str(val).strip() if val is not None else ""

        datos = {
            "nombres": "%s %s" % (_v(self.txt_1er_nombre.value), _v(self.txt_2do_nombre.value)),
            "apellidos": "%s %s" % (_v(self.txt_1er_apellido.value), _v(self.txt_2do_apellido.value)),
            "cedula": _v(self.txt_cedula.value),
            "telefono": _v(self.txt_telefono.value),
            "grado_jerarquia": _v(self.txt_grado.value),
            "cargo": _v(self.txt_cargo.value),
            "dir_domiciliaria": _v(self.txt_dir_dom.value),
            "dir_emergencia": _v(self.txt_dir_eme.value),
        }

        if self.is_edit:
            pid, err, msg = self.controller.actualizar(self.personal_id, datos)
        else:
            pid, err, msg = self.controller.guardar(datos)
        
        if err:
            self.lbl_error.value = err
            self.update()
        else:
            if not msg:
                nombre = f"{datos.get('nombres', '')} {datos.get('apellidos', '')}"
                msg = f"✓ {nombre} registrado exitosamente" if not self.is_edit else "✓ Datos actualizados correctamente"
            snack = ft.SnackBar(
                content=ft.Text(msg),
                bgcolor=ft.Colors.GREEN_700,
                duration=4000,
            )
            self.page.controls.append(snack)
            snack.open = True
            self.page.update()
            self.on_save(pid)

    def did_mount(self):
        async def animate():
            await asyncio.sleep(0.05)
            self.opacity = 1
            self.update()
        asyncio.create_task(animate())