import flet as ft
import asyncio
from datetime import datetime
from comisiones.models.comision_model import ComisionModel
from core.constants import FECHA_FORMAT, TIPOS_COMISION
from core.theme import theme_colors


class ComisionForm(ft.Container):
    def __init__(self, controller, personal_id=None, comision_id=None, on_save=None, on_back=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.controller = controller
        self.personal_id = personal_id
        self.comision_id = comision_id
        self.on_save = on_save
        self.on_back = on_back
        self.dark_mode = dark_mode

        self._build_ui()

    def _build_ui(self):
        tc = theme_colors(self.dark_mode)
        W_FULL = 440

        self.persona = None
        if self.personal_id:
            from personal.models.personal_model import PersonalModel
            self.persona = PersonalModel.get_by_id(self.personal_id)

        if self.comision_id and not self.persona:
            datos_comision = ComisionModel.get_by_id(self.comision_id)
            if datos_comision:
                self.persona = {
                    "id": datos_comision.get("personal_id"),
                    "nombres": datos_comision.get("nombres", ""),
                    "apellidos": datos_comision.get("apellidos", ""),
                    "cedula": datos_comision.get("cedula", ""),
                    "grado_jerarquia": datos_comision.get("grado_jerarquia", ""),
                    "cargo": datos_comision.get("cargo", ""),
                }

        nombre_completo = ""
        cedula = ""
        if self.persona:
            nombre_completo = "%s %s" % (self.persona.get("nombres", ""), self.persona.get("apellidos", ""))
            cedula = self.persona.get("cedula", "")

        lbl_persona = ft.Text(nombre_completo if nombre_completo else "Sin persona seleccionada",
                              size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
        lbl_cedula = ft.Text("C.I.: %s" % cedula, size=13, color=tc["text_secondary"])

        self.tipo_comision = ft.Dropdown(
            label="Tipo de Comisión*",
            width=W_FULL,
            options=[ft.dropdown.Option(t) for t in TIPOS_COMISION],
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            text_style=ft.TextStyle(color=tc["input_text"]),
            border=ft.InputBorder.OUTLINE,
        )

        self.destino = ft.TextField(label="Destino*", icon=ft.Icons.LOCATION_ON, width=W_FULL,
                                    bgcolor=tc["input_bg"], border_color=tc["input_border"],
                                    color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]))

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
            bgcolor=tc["input_bg"], border_color=tc["input_border"],
            color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]),
        )
        self.btn_desde = ft.IconButton(icon=ft.Icons.CALENDAR_TODAY, icon_color=tc["text_secondary"], on_click=self.abrir_calendario_desde)
        self.dp_desde = ft.DatePicker(
            first_date=datetime(2000, 1, 1),
            last_date=datetime(2050, 12, 31),
            on_change=self.cambio_desde,
        )

        self.fecha_hasta = None
        self.input_hasta = ft.TextField(
            label="Vencimiento*", icon=ft.Icons.EVENT_BUSY,
            width=W_FULL, read_only=True, hint_text="DD/MM/AAAA",
            bgcolor=tc["input_bg"], border_color=tc["input_border"],
            color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]),
        )
        self.btn_hasta = ft.IconButton(icon=ft.Icons.CALENDAR_TODAY, icon_color=tc["text_secondary"], on_click=self.abrir_calendario_hasta)
        self.dp_hasta = ft.DatePicker(
            first_date=datetime(2000, 1, 1),
            last_date=datetime(2050, 12, 31),
            on_change=self.cambio_hasta,
        )

        self.lbl_total_dias = ft.Text("Días totales: —", weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400, size=14)

        self.observaciones = ft.TextField(
            label="Observaciones", icon=ft.Icons.NOTES,
            width=W_FULL, multiline=True, min_lines=3, max_lines=5,
            hint_text="Notas adicionales (opcional)",
            bgcolor=tc["input_bg"], border_color=tc["input_border"],
            color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]),
            hint_style=ft.TextStyle(color=tc["text_hint"]),
        )

        if self.comision_id:
            datos = ComisionModel.get_by_id(self.comision_id)
            if datos:
                self.tipo_comision.value = datos.get("tipo_comision", "")
                self.destino.value = datos.get("destino", "")
                self.txt_fecha_elaboracion.value = datos.get("fecha_elaboracion", "")
                self.input_desde.value = datos.get("fecha_desde", "")
                self.input_hasta.value = datos.get("fecha_hasta", "")
                self.observaciones.value = datos.get("observaciones", "")
                try:
                    self.fecha_desde = datetime.strptime(self.input_desde.value, FECHA_FORMAT)
                    self.fecha_hasta = datetime.strptime(self.input_hasta.value, FECHA_FORMAT)
                    self.calcular_dias()
                except ValueError:
                    pass

        btn_label = "Actualizar Comisión" if self.comision_id else "Guardar Comisión"
        btn_icon = ft.Icons.UPDATE if self.comision_id else ft.Icons.SAVE

        self.btn_guardar = ft.Container(
            content=ft.Row([
                ft.Icon(btn_icon, color=ft.Colors.WHITE, size=20),
                ft.Text(btn_label, color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.CENTER_LEFT,
                end=ft.Alignment.CENTER_RIGHT,
                colors=["#1b5e20", "#2e7d32"],
            ),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=28, vertical=14),
            ink=True,
            on_click=self._guardar,
        )

        self.btn_volver = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ARROW_BACK, color=tc["text_secondary"], size=20),
                ft.Text("Volver", color=tc["text_secondary"], size=14, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            border=ft.border.all(1, tc["border_primary"]),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=28, vertical=14),
            ink=True,
            on_click=lambda e: self.on_back() if self.on_back else None,
        )

        def seccion_titulo(texto, icono):
            return ft.Container(
                content=ft.Row([ft.Icon(icono, color=ft.Colors.GREEN_400, size=18),
                                ft.Text(texto, size=14, weight=ft.FontWeight.BOLD, color=tc["text_secondary"])],
                               spacing=10),
                padding=ft.padding.only(bottom=8),
            )

        header_title = "Editar Comision" if self.comision_id else "Registrar Comision"
        header_icon = ft.Icons.EDIT_DOCUMENT if self.comision_id else ft.Icons.BUSINESS_CENTER

        formulario = ft.Column(
            controls=[
                ft.Icon(header_icon, size=48, color=ft.Colors.GREEN_400),
                ft.Text(header_title, size=24, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Container(height=5),
                ft.Container(
                    content=ft.Column([lbl_persona, lbl_cedula], spacing=2, tight=True),
                    bgcolor=tc["badge_green"], border_radius=10,
                    padding=ft.padding.all(14), width=W_FULL,
                ),
                ft.Divider(color=tc["divider"]),
                seccion_titulo("Detalles de la Comision", ft.Icons.BUSINESS_CENTER),
                self.tipo_comision,
                self.destino,
                self.txt_fecha_elaboracion,
                seccion_titulo("Periodo", ft.Icons.DATE_RANGE),
                ft.Row([self.input_desde, self.btn_desde], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([ft.Icon(ft.Icons.ARROW_DOWNWARD, color=tc["text_tertiary"], size=20),
                        ft.Text("hasta", color=tc["text_tertiary"], size=12)],
                       alignment=ft.MainAxisAlignment.CENTER, spacing=4),
                ft.Row([self.input_hasta, self.btn_hasta], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=10),
                ft.Container(content=self.lbl_total_dias, bgcolor=tc["badge_green"], border_radius=8,
                             padding=ft.padding.symmetric(horizontal=14, vertical=8), width=W_FULL),
                seccion_titulo("Observaciones", ft.Icons.NOTES),
                self.observaciones,
                ft.Divider(color=tc["divider"]),
                self.btn_guardar,
                ft.Container(height=8),
                self.btn_volver,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True, scroll=ft.ScrollMode.AUTO, spacing=8,
        )

        card = ft.Card(
            elevation=10, shape=ft.RoundedRectangleBorder(radius=18),
            content=ft.Container(
                padding=ft.padding.only(top=35, bottom=35, left=40, right=40),
                content=formulario, height=680,
            )
        )

        self._card_wrapper = ft.Container(
            content=card, opacity=0, offset=ft.Offset(0, 0.15),
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN),
            animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
        )
        self.content = self._card_wrapper

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
                self.lbl_total_dias.value = "Fechas inválidas"
                self.lbl_total_dias.color = ft.Colors.RED_700
            else:
                self.lbl_total_dias.value = "Días totales: %d" % (diff + 1)
                self.lbl_total_dias.color = ft.Colors.GREEN_400
            try:
                self.lbl_total_dias.update()
            except Exception:
                pass

    def _guardar(self, e):
        if not self.personal_id:
            self.page.snack_bar = ft.SnackBar(ft.Text("No se ha seleccionado una persona"),
                                               bgcolor=ft.Colors.RED_700, open=True)
            self.page.update()
            return

        vacios = []
        if not self.tipo_comision.value:
            vacios.append("Tipo de Comisión")
        if not self.destino.value:
            vacios.append("Destino")
        if not self.input_desde.value:
            vacios.append("Fecha Inicio")
        if not self.input_hasta.value:
            vacios.append("Fecha Vencimiento")
        if vacios:
            self.page.snack_bar = ft.SnackBar(ft.Text("Campos obligatorios: %s" % ", ".join(vacios)),
                                               bgcolor=ft.Colors.RED_700, open=True)
            self.page.update()
            return

        if self.fecha_desde and self.fecha_hasta:
            desde = self.fecha_desde.replace(tzinfo=None) if self.fecha_desde.tzinfo else self.fecha_desde
            hasta = self.fecha_hasta.replace(tzinfo=None) if self.fecha_hasta.tzinfo else self.fecha_hasta
            if desde > hasta:
                self.page.snack_bar = ft.SnackBar(ft.Text("La fecha de inicio debe ser anterior al vencimiento"),
                                                   bgcolor=ft.Colors.RED_700, open=True)
                self.page.update()
                return

        datos = {
            "personal_id": self.personal_id,
            "tipo_comision": self.tipo_comision.value,
            "destino": self.destino.value,
            "fecha_elaboracion": self.txt_fecha_elaboracion.value,
            "fecha_desde": self.input_desde.value,
            "fecha_hasta": self.input_hasta.value,
            "observaciones": self.observaciones.value,
        }

        if self.comision_id:
            datos["id"] = self.comision_id
            ok, err = self.controller.actualizar(self.comision_id, datos)
        else:
            ok, err = self.controller.guardar(datos)

        if err:
            self.page.snack_bar = ft.SnackBar(ft.Text(err), bgcolor=ft.Colors.RED_700, open=True)
        else:
            msg = "¡Comisión actualizada!" if self.comision_id else "¡Comisión registrada!"
            self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN_700, open=True)
        self.page.update()
        if ok and self.on_save:
            self.on_save()

    def did_mount(self):
        async def animate():
            await asyncio.sleep(0.05)
            self._card_wrapper.opacity = 1
            self._card_wrapper.offset = ft.Offset(0, 0)
            self.update()
        asyncio.create_task(animate())
