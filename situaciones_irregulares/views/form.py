import flet as ft
import asyncio
from datetime import datetime
from core.constants import FECHA_FORMAT, TIPOS_SITUACION
from core.theme import theme_colors
from personal.models.personal_model import PersonalModel


class SituacionFormView(ft.Container):
    def __init__(self, controller, situacion_id=None, personal_id=None, on_save=None, on_back=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.alignment = ft.Alignment.CENTER
        self.controller = controller
        self.situacion_id = situacion_id
        self.personal_id = personal_id
        self.on_save = on_save
        self.on_back = on_back
        self.dark_mode = dark_mode

        self.datos_situacion = None
        self.personal_seleccionado = None
        self.fecha_inicio = None
        self.modo_edicion = bool(situacion_id)

        if personal_id:
            persona = PersonalModel.get_by_id(personal_id)
            if persona:
                self.personal_seleccionado = persona

        if self.modo_edicion and not self.personal_seleccionado:
            datos_situacion = controller.obtener_por_id(situacion_id)
            if datos_situacion:
                self.personal_seleccionado = {
                    "id": datos_situacion.get("personal_id"),
                    "nombres": datos_situacion.get("nombres", ""),
                    "apellidos": datos_situacion.get("apellidos", ""),
                    "cedula": datos_situacion.get("cedula", ""),
                    "grado_jerarquia": datos_situacion.get("grado_jerarquia", ""),
                    "cargo": datos_situacion.get("cargo", ""),
                }

        self._build_ui()

    def _build_ui(self):
        tc = theme_colors(self.dark_mode)
        W_FULL = 440

        self.lbl_persona_resumen = ft.Text("Sin persona seleccionada", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
        self.lbl_persona_detalle = ft.Text("Haga click en 'Seleccionar Personal'", size=13, color=tc["text_secondary"])
        self.lbl_persona_extras = ft.Text("", size=13, color=tc["text_tertiary"], visible=False)

        self.btn_seleccionar_personal = ft.ElevatedButton(
            "Seleccionar Personal",
            icon=ft.Icons.PERSON_SEARCH,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600, shape=ft.RoundedRectangleBorder(radius=6)),
            on_click=self.abrir_modal_seleccion_personal,
            visible=not self.modo_edicion
        )

        self.panel_personal = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        self.lbl_persona_resumen,
                        self.lbl_persona_detalle,
                        self.lbl_persona_extras
                    ], spacing=2, tight=True, expand=True),
                    self.btn_seleccionar_personal
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ]),
            bgcolor=tc["badge_green"],
            border_radius=10,
            padding=ft.padding.all(14),
            width=W_FULL,
        )

        self.actualizar_etiquetas_personal()

        self.tipo_situacion = ft.Dropdown(
            label="Tipo de Situación*",
            width=W_FULL,
            options=[ft.dropdown.Option(t) for t in TIPOS_SITUACION],
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

        self.fecha_inicio = None
        self.input_fecha_inicio = ft.TextField(
            expand=True, read_only=True, hint_text="DD/MM/AAAA",
            bgcolor=tc["input_bg"], border_color=tc["input_border"],
            color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]),
            label="Fecha de Inicio"
        )
        self.btn_fecha_inicio = ft.IconButton(icon=ft.Icons.CALENDAR_TODAY, icon_color=tc["text_secondary"], on_click=self.abrir_calendario_inicio)
        self.dp_fecha_inicio = ft.DatePicker(
            first_date=datetime(2000, 1, 1),
            last_date=datetime(2050, 12, 31),
            on_change=self.cambio_fecha_inicio,
        )

        self.observaciones = ft.TextField(
            label="Observaciones", icon=ft.Icons.NOTES,
            width=W_FULL, multiline=True, min_lines=3, max_lines=5,
            hint_text="Notas adicionales (opcional)",
            bgcolor=tc["input_bg"], border_color=tc["input_border"],
            color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]),
            hint_style=ft.TextStyle(color=tc["text_hint"]),
        )

        if self.modo_edicion:
            datos = self.controller.obtener_por_id(self.situacion_id)
            if datos:
                self.tipo_situacion.value = datos.get("tipo_situacion", "")
                self.txt_fecha_elaboracion.value = datos.get("fecha_elaboracion", "")
                self.input_fecha_inicio.value = datos.get("fecha_inicio", "")
                self.observaciones.value = datos.get("observaciones", "")
                try:
                    self.fecha_inicio = datetime.strptime(self.input_fecha_inicio.value, FECHA_FORMAT)
                except ValueError:
                    pass

        btn_label = "Actualizar Situación" if self.modo_edicion else "Guardar Situación"
        btn_icon = ft.Icons.UPDATE if self.modo_edicion else ft.Icons.SAVE

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
                padding=ft.padding.only(top=16, bottom=8),
            )

        header_title = "Editar Situación Irregular" if self.modo_edicion else "Registrar Situación Irregular"
        header_icon = ft.Icons.EDIT_DOCUMENT if self.modo_edicion else ft.Icons.WARNING_AMBER_ROUNDED

        formulario = ft.Column(
            controls=[
                ft.Icon(header_icon, size=48, color=ft.Colors.ORANGE_400),
                ft.Text(header_title, size=24, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Container(height=5),
                self.panel_personal,
                ft.Divider(color=tc["divider"]),
                seccion_titulo("Detalles de la Situación", ft.Icons.WARNING),
                self.tipo_situacion,
                self.txt_fecha_elaboracion,
                seccion_titulo("Inicio", ft.Icons.EVENT),
                ft.Row([self.input_fecha_inicio, self.btn_fecha_inicio], vertical_alignment=ft.CrossAxisAlignment.CENTER, width=W_FULL),
                ft.Container(height=10),
                seccion_titulo("Observaciones", ft.Icons.NOTES),
                self.observaciones,
                ft.Divider(color=tc["divider"]),
                self.btn_guardar,
                ft.Container(height=8),
                self.btn_volver,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
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

    def actualizar_etiquetas_personal(self):
        if self.personal_seleccionado:
            p = self.personal_seleccionado
            self.lbl_persona_resumen.value = f"{p.get('nombres', '')} {p.get('apellidos', '')}".strip()
            self.lbl_persona_detalle.value = f"C.I.: {p.get('cedula', '')}"
            self.lbl_persona_extras.value = f"{p.get('grado_jerarquia', '')} | {p.get('cargo', '')}"
            self.lbl_persona_extras.visible = True
        else:
            self.lbl_persona_resumen.value = "Sin persona seleccionada"
            self.lbl_persona_detalle.value = "Haga click en 'Seleccionar Personal'"
            self.lbl_persona_extras.visible = False

        if hasattr(self, "lbl_persona_resumen"):
            try:
                self.lbl_persona_resumen.update()
                self.lbl_persona_detalle.update()
                self.lbl_persona_extras.update()
            except Exception:
                pass

    def abrir_modal_seleccion_personal(self, e):
        tc = theme_colors(self.dark_mode)
        
        todos_personal = PersonalModel.get_all()
        seleccion_temporal = {self.personal_seleccionado["id"]} if self.personal_seleccionado else set()

        def on_search(e):
            term = e.control.value.lower()
            for row in list_view.controls:
                persona_row = row.data
                texto_busqueda = f"{persona_row.get('nombres','')} {persona_row.get('apellidos','')} {persona_row.get('cedula','')}".lower()
                row.visible = term in texto_busqueda
            try:
                list_view.update()
            except RuntimeError:
                pass

        list_view = ft.ListView(expand=True, spacing=10, height=300)
        
        for p in todos_personal:
            check = ft.Checkbox(
                label=f"{p.get('nombres','')} {p.get('apellidos','')} - C.I: {p.get('cedula','')}",
                value=p["id"] in seleccion_temporal,
                data=p["id"]
            )
            fila = ft.Container(content=check, data=p)
            list_view.controls.append(fila)

        def confirmar_seleccion(e):
            for row in list_view.controls:
                chk = row.content
                if chk.value:
                    self.personal_seleccionado = row.data
                    break
            self.actualizar_etiquetas_personal()
            self.page.pop_dialog()

        def cancelar(e):
            self.page.pop_dialog()

        txt_buscar = ft.TextField(
            label="Buscar por nombre o cédula",
            icon=ft.Icons.SEARCH,
            on_change=on_search,
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            color=tc["input_text"],
        )

        modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Seleccionar Personal", color=tc["text_primary"]),
            content=ft.Container(
                width=450,
                content=ft.Column([txt_buscar, ft.Divider(), list_view], tight=True)
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.ElevatedButton("Confirmar", on_click=confirmar_seleccion, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700)),
            ],
            bgcolor=tc["bg_dialog"]
        )

        self.page.show_dialog(modal)

    def abrir_calendario_inicio(self, e):
        if self.dp_fecha_inicio not in self.page.overlay:
            self.page.overlay.append(self.dp_fecha_inicio)
        self.dp_fecha_inicio.open = True
        self.page.update()

    def cambio_fecha_inicio(self, e):
        if self.dp_fecha_inicio.value:
            self.fecha_inicio = self.dp_fecha_inicio.value
            self.input_fecha_inicio.value = self.dp_fecha_inicio.value.strftime(FECHA_FORMAT)
            try:
                self.input_fecha_inicio.update()
            except RuntimeError:
                pass

    def _validar(self):
        errores = []

        if not self.personal_seleccionado:
            errores.append("Debe seleccionar un personal")

        if not self.tipo_situacion.value:
            errores.append("Debe seleccionar el tipo de situación")

        if not self.input_fecha_inicio.value:
            errores.append("Debe seleccionar la fecha de inicio")

        return errores

    def _guardar(self, e):
        errores = self._validar()
        if errores:
            self.page.snack_bar = ft.SnackBar(
                ft.Row([
                    ft.Icon(ft.Icons.WARNING, color=ft.Colors.WHITE, size=20),
                    ft.Text("Error: " + "; ".join(errores), color=ft.Colors.WHITE),
                ], spacing=10),
                bgcolor=ft.Colors.RED_700,
                duration=4000,
                open=True,
            )
            self.page.update()
            return

        datos = {
            "personal_id": self.personal_seleccionado.get("id"),
            "tipo_situacion": self.tipo_situacion.value,
            "fecha_inicio": self.input_fecha_inicio.value,
            "observaciones": self.observaciones.value or "",
            "estado": "Activo",
            "fecha_resolucion": None,
        }

        if self.situacion_id:
            ok, err, msg = self.controller.actualizar(self.situacion_id, datos)
        else:
            ok, err, msg = self.controller.guardar(datos)

        if ok:
            self.page.snack_bar = ft.SnackBar(
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                    ft.Text(msg, color=ft.Colors.WHITE),
                ], spacing=10),
                bgcolor=ft.Colors.GREEN_700,
                duration=3000,
                open=True,
            )
            if self.on_save:
                self.on_save()
        else:
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

    def did_mount(self):
        async def animate():
            await asyncio.sleep(0.05)
            self._card_wrapper.opacity = 1
            self._card_wrapper.offset = ft.Offset(0, 0)
            try:
                self.update()
            except RuntimeError:
                pass
        asyncio.create_task(animate())