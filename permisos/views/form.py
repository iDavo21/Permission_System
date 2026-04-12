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
        self.personal_id_inicial = personal_id
        self.permiso_id = permiso_id
        self.dark_mode = dark_mode
        
        self.personal_seleccionados = []
        
        # Modo de edicion: Restringir a 1 persona
        self.modo_edicion = bool(permiso_id)

        if personal_id:
            persona = PersonalModel.get_by_id(personal_id)
            if persona:
                self.personal_seleccionados.append(persona)

        if self.modo_edicion and not self.personal_seleccionados:
            datos_permiso = PermisoModel.get_by_id(permiso_id)
            if datos_permiso:
                self.personal_seleccionados.append({
                    "id": datos_permiso.get("personal_id"),
                    "nombres": datos_permiso.get("nombres", ""),
                    "apellidos": datos_permiso.get("apellidos", ""),
                    "cedula": datos_permiso.get("cedula", ""),
                    "telefono": datos_permiso.get("telefono", ""),
                    "grado_jerarquia": datos_permiso.get("grado_jerarquia", ""),
                    "cargo": datos_permiso.get("cargo", ""),
                    "dir_domiciliaria": datos_permiso.get("dir_domiciliaria", ""),
                    "dir_emergencia": datos_permiso.get("dir_emergencia", ""),
                })

        self._build_ui()

    def _build_ui(self):
        tc = theme_colors(self.dark_mode)
        W_FULL = 440

        self.lbl_persona_resumen = ft.Text("Sin persona seleccionada", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
        self.lbl_persona_detalle = ft.Text("Seleccione al menos a una persona", size=13, color=tc["text_secondary"])
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
            expand=True, read_only=True, hint_text="DD/MM/AAAA",
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
            expand=True, read_only=True, hint_text="DD/MM/AAAA",
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

        if self.modo_edicion:
            datos_permiso = PermisoModel.get_by_id(self.permiso_id)
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

        btn_label = "Actualizar Permiso" if self.modo_edicion else "Guardar Permiso(s)"
        btn_icon = ft.Icons.UPDATE if self.modo_edicion else ft.Icons.SAVE

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

        header_title = "Editar Permiso" if self.modo_edicion else "Registrar Permiso(s)"
        header_icon = ft.Icons.EDIT_DOCUMENT if self.modo_edicion else ft.Icons.ASSIGNMENT_ADD

        formulario = ft.Column(
            controls=[
                ft.Icon(header_icon, size=48, color=ft.Colors.GREEN_400),
                ft.Text(header_title, size=24, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Container(height=5),
                self.panel_personal,
                ft.Divider(color=tc["divider"]),

                seccion_titulo("Detalles del Permiso", ft.Icons.ASSIGNMENT),
                self.tipo_permiso,
                self.txt_fecha_elaboracion,

                seccion_titulo("Periodo", ft.Icons.DATE_RANGE),
                ft.Row([self.input_desde, self.btn_desde], vertical_alignment=ft.CrossAxisAlignment.CENTER, width=W_FULL),
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ARROW_DOWNWARD, color=tc["text_tertiary"], size=20),
                        ft.Text("hasta", color=tc["text_tertiary"], size=12),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=4,
                ),
                ft.Row([self.input_hasta, self.btn_hasta], vertical_alignment=ft.CrossAxisAlignment.CENTER, width=W_FULL),
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

    def actualizar_etiquetas_personal(self):
        cantidad = len(self.personal_seleccionados)
        if cantidad == 0:
            self.lbl_persona_resumen.value = "Sin persona seleccionada"
            self.lbl_persona_detalle.value = "Haga click en 'Seleccionar Personal'"
            self.lbl_persona_extras.visible = False
        elif cantidad == 1:
            p = self.personal_seleccionados[0]
            self.lbl_persona_resumen.value = f"{p.get('nombres', '')} {p.get('apellidos', '')}".strip()
            self.lbl_persona_detalle.value = f"C.I.: {p.get('cedula', '')}"
            self.lbl_persona_extras.value = f"{p.get('grado_jerarquia', '')} | {p.get('cargo', '')}"
            self.lbl_persona_extras.visible = True
        else:
            self.lbl_persona_resumen.value = f"{cantidad} personas seleccionadas"
            nombres = [f"{p.get('nombres', '').split(' ')[0]} {p.get('apellidos', '').split(' ')[0]}" for p in self.personal_seleccionados]
            resumen_nombres = ", ".join(nombres)
            self.lbl_persona_detalle.value = resumen_nombres if len(resumen_nombres) <= 40 else resumen_nombres[:40] + "..."
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
        seleccion_temporal = {p["id"] for p in self.personal_seleccionados}

        def on_search(e):
            term = e.control.value.lower()
            for row in list_view.controls:
                persona_row = row.data
                texto_busqueda = f"{persona_row.get('nombres','')} {persona_row.get('apellidos','')} {persona_row.get('cedula','')}".lower()
                row.visible = term in texto_busqueda
            list_view.update()

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
            ids_existentes = {p["id"] for p in self.personal_seleccionados}
            for row in list_view.controls:
                chk = row.content
                if chk.value and row.data["id"] not in ids_existentes:
                    self.personal_seleccionados.append(row.data)
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
                content=ft.Column([
                    txt_buscar,
                    ft.Divider(),
                    list_view
                ], tight=True)
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.ElevatedButton("Confirmar", on_click=confirmar_seleccion, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700)),
            ],
            bgcolor=tc["bg_dialog"]
        )

        self.page.show_dialog(modal)


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
        if not self.personal_seleccionados:
            self.page.snack_bar = ft.SnackBar(
                ft.Row([
                    ft.Icon(ft.Icons.WARNING, color=ft.Colors.WHITE, size=20),
                    ft.Text("No se ha seleccionado ninguna persona", color=ft.Colors.WHITE),
                ], spacing=10),
                bgcolor=ft.Colors.RED_700,
                duration=4000,
                open=True,
            )
            self.page.update()
            return

        campos_obligatorios = {
            "Tipo de Permiso": self.tipo_permiso.value,
            "Fecha Inicio": self.input_desde.value,
            "Fecha Vencimiento": self.input_hasta.value,
        }

        vacios = [k for k, v in campos_obligatorios.items() if not v or not str(v).strip()]
        if vacios:
            self.page.snack_bar = ft.SnackBar(
                ft.Row([
                    ft.Icon(ft.Icons.WARNING, color=ft.Colors.WHITE, size=20),
                    ft.Text("Campo(s) obligatorio(s) vacío(s): %s" % ", ".join(vacios), color=ft.Colors.WHITE),
                ], spacing=10),
                bgcolor=ft.Colors.RED_700,
                duration=4000,
                open=True,
            )
            self.page.update()
            return

        if self.fecha_desde and self.fecha_hasta:
            desde = self.fecha_desde.replace(tzinfo=None) if self.fecha_desde.tzinfo else self.fecha_desde
            hasta = self.fecha_hasta.replace(tzinfo=None) if self.fecha_hasta.tzinfo else self.fecha_hasta
            if desde > hasta:
                self.page.snack_bar = ft.SnackBar(
                    ft.Row([
                        ft.Icon(ft.Icons.WARNING, color=ft.Colors.WHITE, size=20),
                        ft.Text("La fecha de inicio debe ser anterior al vencimiento", color=ft.Colors.WHITE),
                    ], spacing=10),
                    bgcolor=ft.Colors.RED_700,
                    duration=4000,
                    open=True,
                )
                self.page.update()
                return

        datos_base = {
            "tipo_permiso":       self.tipo_permiso.value,
            "fecha_elaboracion":  self.txt_fecha_elaboracion.value,
            "fecha_desde":        self.input_desde.value,
            "fecha_hasta":        self.input_hasta.value,
            "observaciones":      self.observaciones.value,
        }

        errores = []
        exitos = 0

        for p in self.personal_seleccionados:
            datos_actuales = datos_base.copy()
            datos_actuales["personal_id"] = p["id"]

            if self.modo_edicion:
                datos_actuales["id"] = self.permiso_id
            
            ok, err, msg = self.on_save(datos_actuales) if self.on_save else (None, "No handler", None)
            if err:
                errores.append(f"{p.get('nombres', '').split(' ')[0]}: {err}")
            else:
                exitos += 1

        if errores:
            msg = "Errores: " + " | ".join(errores)
            snack = ft.SnackBar(
                content=ft.Text(msg),
                bgcolor=ft.Colors.RED_700,
                duration=6000,
            )
            self.page.controls.append(snack)
            snack.open = True
        else:
            success_msg = msg or ("¡Permiso actualizado con éxito!" if self.modo_edicion else f"¡{exitos} permiso(s) registrado(s) con éxito!")
            snack = ft.SnackBar(
                content=ft.Text(success_msg),
                bgcolor=ft.Colors.GREEN_700,
                duration=4000,
            )
            self.page.controls.append(snack)
            snack.open = True

        self.page.update()
        if exitos > 0 and self.on_back:
            self.on_back()
