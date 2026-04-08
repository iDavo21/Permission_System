import flet as ft
import asyncio
from datetime import datetime
from permisos.models.permiso_model import PermisoModel
from personal.models.personal_model import PersonalModel
from core.constants import (
    FECHA_FORMAT, TIPOS_PERMISO,
)
from core.estado_utils import fecha_a_datetime
from core.theme import theme_colors

class PermissionView(ft.Container):
    def __init__(self, on_back, on_save=None, personal_id=None, permiso_id=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.alignment = ft.Alignment.CENTER
        self.on_back = on_back
        self.on_save = on_save
        self.personal_id = personal_id
        self.permiso_id = permiso_id
        self.dark_mode = dark_mode

        W_FULL = 440

        self.persona = None
        if personal_id:
            self.persona = PersonalModel.get_by_id(personal_id)

        if permiso_id and not self.persona:
            datos_permiso = PermisoModel.get_by_id(permiso_id)
            if datos_permiso:
                self.persona = {
                    "id": datos_permiso.get("personal_id"),
                    "nombres": datos_permiso.get("nombres", ""),
                    "apellidos": datos_permiso.get("apellidos", ""),
                    "cedula": datos_permiso.get("cedula", ""),
                    "telefono": datos_permiso.get("telefono", ""),
                    "grado_jerarquia": datos_permiso.get("grado_jerarquia", ""),
                    "cargo": datos_permiso.get("cargo", ""),
                    "dir_domiciliaria": datos_permiso.get("dir_domiciliaria", ""),
                    "dir_emergencia": datos_permiso.get("dir_emergencia", ""),
                }

        nombre_completo = ""
        cedula = ""
        grado = ""
        cargo = ""
        if self.persona:
            nombre_completo = "%s %s" % (self.persona.get("nombres", ""), self.persona.get("apellidos", ""))
            cedula = self.persona.get("cedula", "")
            grado = self.persona.get("grado_jerarquia", "")
            cargo = self.persona.get("cargo", "")

        tc = theme_colors(self.dark_mode)

        lbl_persona = ft.Text(
            nombre_completo if nombre_completo else "Sin persona seleccionada",
            size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400,
        )
        lbl_cedula = ft.Text("C.I.: %s" % cedula, size=13, color=tc["text_secondary"])
        lbl_info = ft.Text("%s | %s" % (grado, cargo), size=13, color=tc["text_tertiary"])

        self.tipo_permiso = ft.Dropdown(
            label="Tipo de Permiso*",
            width=W_FULL,
            options=[ft.dropdown.Option(t) for t in TIPOS_PERMISO],
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            text_style=ft.TextStyle(color=tc["input_text"]),
            border=ft.InputBorder.OUTLINE,
        )

        hoy = datetime.now()
        self.txt_fecha_elaboracion = ft.TextField(
            label="Fecha de Elaboración",
            icon=ft.Icons.EDIT_DOCUMENT,
            width=W_FULL,
            value=hoy.strftime("%d/%m/%Y"),
            read_only=True,
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            color=tc["input_text"],
            label_style=ft.TextStyle(color=tc["input_label"]),
        )

        self.fecha_desde = None
        self.input_desde = ft.TextField(
            label="Inicio*", icon=ft.Icons.EVENT_AVAILABLE,
            width=W_FULL, read_only=True, hint_text="DD/MM/AAAA",
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            color=tc["input_text"],
            label_style=ft.TextStyle(color=tc["input_label"]),
        )
        self.btn_desde = ft.IconButton(
            icon=ft.Icons.CALENDAR_TODAY,
            icon_color=tc["text_secondary"],
            on_click=self.abrir_calendario_desde,
            tooltip="Seleccionar Fecha Inicio"
        )
        self.dp_desde = ft.DatePicker(
            first_date=datetime(2000, 1, 1),
            last_date=datetime(2050, 12, 31),
            on_change=self.cambio_desde,
        )

        self.fecha_hasta = None
        self.input_hasta = ft.TextField(
            label="Vencimiento*", icon=ft.Icons.EVENT_BUSY,
            width=W_FULL, read_only=True, hint_text="DD/MM/AAAA",
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            color=tc["input_text"],
            label_style=ft.TextStyle(color=tc["input_label"]),
        )
        self.btn_hasta = ft.IconButton(
            icon=ft.Icons.CALENDAR_TODAY,
            icon_color=tc["text_secondary"],
            on_click=self.abrir_calendario_hasta,
            tooltip="Seleccionar Fecha Fin"
        )
        self.dp_hasta = ft.DatePicker(
            first_date=datetime(2000, 1, 1),
            last_date=datetime(2050, 12, 31),
            on_change=self.cambio_hasta,
        )

        self.lbl_total_dias = ft.Text(
            "Días totales del permiso: —",
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREEN_400,
            size=14
        )

        self.observaciones = ft.TextField(
            label="Observaciones", icon=ft.Icons.NOTES,
            width=W_FULL, multiline=True, min_lines=3, max_lines=5,
            hint_text="Notas adicionales (opcional)",
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            color=tc["input_text"],
            label_style=ft.TextStyle(color=tc["input_label"]),
            hint_style=ft.TextStyle(color=tc["text_hint"]),
        )

        if permiso_id:
            datos_permiso = PermisoModel.get_by_id(permiso_id)
            if datos_permiso:
                self.tipo_permiso.value = datos_permiso.get("tipo_permiso", "")
                self.txt_fecha_elaboracion.value = datos_permiso.get("fecha_elaboracion", "")
                self.input_desde.value = datos_permiso.get("fecha_desde", "")
                self.input_hasta.value = datos_permiso.get("fecha_hasta", "")
                self.observaciones.value = datos_permiso.get("observaciones", "")
                try:
                    self.fecha_desde = datetime.strptime(self.input_desde.value, FECHA_FORMAT)
                    self.fecha_hasta = datetime.strptime(self.input_hasta.value, FECHA_FORMAT)
                    self.calcular_dias()
                except ValueError:
                    self.fecha_desde = None
                    self.fecha_hasta = None

        btn_label = "Actualizar Permiso" if permiso_id else "Guardar Permiso"
        btn_icon = ft.Icons.UPDATE if permiso_id else ft.Icons.SAVE

        self.btn_guardar = ft.ElevatedButton(
            btn_label,
            icon=btn_icon,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_700,
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=15
            ),
            width=W_FULL,
            on_click=self.guardar_permiso
        )
        self._spinner = ft.ProgressRing(width=20, height=20, stroke_width=2, color=ft.Colors.WHITE, visible=False)
        self.btn_volver = ft.TextButton(
            "Volver",
            icon=ft.Icons.ARROW_BACK,
            icon_color=tc["text_secondary"],
            on_click=self.volver_al_panel,
        )

        def seccion_titulo(texto, icono):
            return ft.Container(
                content=ft.Row([
                    ft.Icon(icono, color=ft.Colors.GREEN_400, size=18),
                    ft.Text(texto, size=13, weight=ft.FontWeight.BOLD, color=tc["text_secondary"])
                ], spacing=8),
                padding=ft.padding.only(top=16, bottom=4),
            )

        header_title = "Editar Permiso" if permiso_id else "Registrar Permiso"
        header_icon = ft.Icons.EDIT_DOCUMENT if permiso_id else ft.Icons.ASSIGNMENT_ADD

        formulario = ft.Column(
            controls=[
                ft.Icon(header_icon, size=48, color=ft.Colors.GREEN_400),
                ft.Text(header_title, size=24, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Container(height=5),
                ft.Container(
                    content=ft.Column([
                        lbl_persona,
                        lbl_cedula,
                        lbl_info,
                    ], spacing=2, tight=True),
                    bgcolor=tc["badge_green"],
                    border_radius=10,
                    padding=ft.padding.all(14),
                    width=W_FULL,
                ),
                ft.Divider(color=tc["divider"]),

                seccion_titulo("Detalles del Permiso", ft.Icons.ASSIGNMENT),
                self.tipo_permiso,
                self.txt_fecha_elaboracion,

                seccion_titulo("Periodo", ft.Icons.DATE_RANGE),
                ft.Row([self.input_desde, self.btn_desde], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ARROW_DOWNWARD, color=tc["text_tertiary"], size=20),
                        ft.Text("hasta", color=tc["text_tertiary"], size=12),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=4,
                ),
                ft.Row([self.input_hasta, self.btn_hasta], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=10),
                ft.Container(
                    content=self.lbl_total_dias,
                    bgcolor=tc["badge_green"],
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=14, vertical=8),
                    width=W_FULL,
                ),

                seccion_titulo("Observaciones", ft.Icons.NOTES),
                self.observaciones,

                ft.Divider(color=tc["divider"]),
                self.btn_guardar,
                self.btn_volver,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            tight=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=8,
        )

        card = ft.Card(
            elevation=10,
            shape=ft.RoundedRectangleBorder(radius=18),
            content=ft.Container(
                padding=ft.padding.only(top=35, bottom=35, left=40, right=40),
                content=formulario,
                height=680,
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

    def did_mount(self):
        async def animate():
            await asyncio.sleep(0.05)
            self._card_wrapper.opacity = 1
            self._card_wrapper.offset = ft.Offset(0, 0)
            self.update()
        asyncio.create_task(animate())

    def volver_al_panel(self, e):
        self.on_back()

    def abrir_calendario_desde(self, e):
        if self.dp_desde not in self.page.overlay:
            self.page.overlay.append(self.dp_desde)
        self.dp_desde.open = True
        self.page.update()

    def abrir_calendario_hasta(self, e):
        if self.dp_hasta not in self.page.overlay:
            self.page.overlay.append(self.dp_hasta)
        self.dp_hasta.open = True
        self.page.update()

    def cambio_desde(self, e):
        if self.dp_desde.value:
            self.fecha_desde = self.dp_desde.value
            self.input_desde.value = self.fecha_desde.strftime(FECHA_FORMAT)
            self.input_desde.update()
            self.calcular_dias()

    def cambio_hasta(self, e):
        if self.dp_hasta.value:
            self.fecha_hasta = self.dp_hasta.value
            self.input_hasta.value = self.fecha_hasta.strftime(FECHA_FORMAT)
            self.input_hasta.update()
            self.calcular_dias()

    def calcular_dias(self):
        if self.fecha_desde and self.fecha_hasta:
            desde = self.fecha_desde.replace(tzinfo=None) if self.fecha_desde.tzinfo else self.fecha_desde
            hasta = self.fecha_hasta.replace(tzinfo=None) if self.fecha_hasta.tzinfo else self.fecha_hasta
            diff = (hasta - desde).days
            if diff < 0:
                self.lbl_total_dias.value = "Fecha de vencimiento es anterior al inicio"
                self.lbl_total_dias.color = ft.Colors.RED_700
            else:
                self.lbl_total_dias.value = "Días totales del permiso: %d" % (diff + 1)
                self.lbl_total_dias.color = ft.Colors.GREEN_400
            try:
                self.lbl_total_dias.update()
            except Exception:
                pass

    def guardar_permiso(self, e):
        if not self.personal_id:
            snack = ft.SnackBar(
                ft.Text("No se ha seleccionado una persona"),
                bgcolor=ft.Colors.RED_700, duration=4000,
            )
            self.page.overlay.append(snack)
            snack.open = True
            self.update()
            return

        campos_obligatorios = {
            "Tipo de Permiso": self.tipo_permiso.value,
            "Fecha Inicio": self.input_desde.value,
            "Fecha Vencimiento": self.input_hasta.value,
        }

        vacios = [k for k, v in campos_obligatorios.items() if not v or not str(v).strip()]
        if vacios:
            snack = ft.SnackBar(
                ft.Text("Campo(s) obligatorio(s) vacío(s): %s" % ", ".join(vacios)),
                bgcolor=ft.Colors.RED_700, duration=4000,
            )
            self.page.overlay.append(snack)
            snack.open = True
            self.update()
            return

        if self.fecha_desde and self.fecha_hasta:
            desde = self.fecha_desde.replace(tzinfo=None) if self.fecha_desde.tzinfo else self.fecha_desde
            hasta = self.fecha_hasta.replace(tzinfo=None) if self.fecha_hasta.tzinfo else self.fecha_hasta
            if desde > hasta:
                snack = ft.SnackBar(
                    ft.Text("La fecha de inicio debe ser anterior al vencimiento"),
                    bgcolor=ft.Colors.RED_700, duration=4000,
                )
                self.page.overlay.append(snack)
                snack.open = True
                self.update()
                return

        datos = {
            "personal_id":        self.personal_id,
            "tipo_permiso":       self.tipo_permiso.value,
            "fecha_elaboracion":  self.txt_fecha_elaboracion.value,
            "fecha_desde":        self.input_desde.value,
            "fecha_hasta":        self.input_hasta.value,
            "observaciones":      self.observaciones.value,
        }

        if self.permiso_id:
            datos["id"] = self.permiso_id
            ok, err = self.on_save(datos) if self.on_save else (None, "No handler")
        else:
            ok, err = self.on_save(datos) if self.on_save else (None, "No handler")

        if err:
            snack = ft.SnackBar(ft.Text(err), bgcolor=ft.Colors.RED_700, duration=4000)
        else:
            msg = "¡Permiso actualizado con éxito!" if self.permiso_id else "¡Permiso registrado con éxito!"
            snack = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN_700, duration=4000)

        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()
