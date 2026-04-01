import flet as ft
from datetime import datetime, timedelta


class AdminView(ft.Stack):
    def __init__(self, on_add_permission=None, lista_permisos=None, on_edit=None, on_delete=None):
        super().__init__()
        self.expand = True

        self.on_edit = on_edit
        self.on_delete = on_delete

        self.todos_los_permisos = lista_permisos or []
        self.permisos_filtrados = list(self.todos_los_permisos)

        tipos = sorted(set(p.get("tipo_permiso", "") for p in self.todos_los_permisos if p.get("tipo_permiso")))

        # ── MENÚ ───────────────────────────────────────────────────────────────
        menu_opciones = ft.PopupMenuButton(
            icon=ft.Icons.MENU,
            icon_color=ft.Colors.WHITE,
            items=[
                ft.PopupMenuItem(
                    content=ft.Text("Agregar Permiso"),
                    icon=ft.Icons.PERSON_ADD,
                    on_click=lambda e: on_add_permission() if on_add_permission else None
                ),
                ft.PopupMenuItem(
                    content=ft.Text("Ver Solicitudes"),
                    icon=ft.Icons.ASSIGNMENT,
                    on_click=lambda e: print("Navegar a Solicitudes")
                ),
            ]
        )

        # ── BUSCADOR ───────────────────────────────────────────────────────────
        self.buscador = ft.TextField(
            hint_text="Buscar por nombre o cédula...",
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
            on_change=lambda e: self.aplicar_filtros(),
        )

        # ── FILTROS ────────────────────────────────────────────────────────────
        self.filtro_tipo = ft.Dropdown(
            label="Tipo",
            width=196,
            height=35,
            text_size=11,
            options=[ft.dropdown.Option("Todos")] + [ft.dropdown.Option(t) for t in tipos],
            value="Todos",
            bgcolor=ft.Colors.WHITE24,
            border_color=ft.Colors.TRANSPARENT,
            border_radius=8,
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
        )

        self.filtro_estado = ft.Dropdown(
            label="Estado",
            width=196,
            height=35,
            text_size=11,
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Vigente"),
                ft.dropdown.Option("Por Expirar"),
                ft.dropdown.Option("Expirado"),
            ],
            value="Todos",
            bgcolor=ft.Colors.WHITE24,
            border_color=ft.Colors.TRANSPARENT,
            border_radius=8,
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
        )

        self.filtro_fecha_desde = ft.TextField(
            label="Desde",
            width=165,
            height=35,
            text_size=11,
            read_only=True,
            hint_text="DD/MM/AAAA",
            hint_style=ft.TextStyle(color=ft.Colors.WHITE54),
            bgcolor=ft.Colors.WHITE24,
            color=ft.Colors.WHITE,
            border_color=ft.Colors.TRANSPARENT,
            border_radius=8,
            label_style=ft.TextStyle(color=ft.Colors.WHITE70),
        )
        self.btn_fecha_desde = ft.IconButton(
            icon=ft.Icons.CALENDAR_TODAY,
            icon_color=ft.Colors.WHITE,
            icon_size=16,
            tooltip="Desde",
            on_click=self.abrir_calendario_desde_filtro,
        )
        self.dp_filtro_desde = ft.DatePicker(
            first_date=datetime(2000, 1, 1),
            last_date=datetime(2050, 12, 31),
            on_change=self.cambio_filtro_desde,
        )

        self.filtro_fecha_hasta = ft.TextField(
            label="Hasta",
            width=165,
            height=35,
            text_size=11,
            read_only=True,
            hint_text="DD/MM/AAAA",
            hint_style=ft.TextStyle(color=ft.Colors.WHITE54),
            bgcolor=ft.Colors.WHITE24,
            color=ft.Colors.WHITE,
            border_color=ft.Colors.TRANSPARENT,
            border_radius=8,
            label_style=ft.TextStyle(color=ft.Colors.WHITE70),
        )
        self.btn_fecha_hasta = ft.IconButton(
            icon=ft.Icons.CALENDAR_TODAY,
            icon_color=ft.Colors.WHITE,
            icon_size=16,
            tooltip="Hasta",
            on_click=self.abrir_calendario_hasta_filtro,
        )
        self.dp_filtro_hasta = ft.DatePicker(
            first_date=datetime(2000, 1, 1),
            last_date=datetime(2050, 12, 31),
            on_change=self.cambio_filtro_hasta,
        )

        self.fecha_filtro_desde = None
        self.fecha_filtro_hasta = None

        btn_aplicar = ft.IconButton(
            icon=ft.Icons.CHECK_CIRCLE,
            icon_color=ft.Colors.GREEN_300,
            icon_size=20,
            tooltip="Aplicar filtros",
            on_click=lambda e: self.aplicar_filtros(),
        )

        btn_limpiar = ft.IconButton(
            icon=ft.Icons.FILTER_ALT_OFF,
            icon_color=ft.Colors.AMBER_300,
            icon_size=20,
            tooltip="Limpiar filtros",
            on_click=lambda e: self.limpiar_filtros(),
        )

        # ── PANEL PLEGABLE DE FILTROS (OVERLAY) ─────────────────────────────────
        self.filtros_abiertos = False

        btn_cerrar_filtros = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_color=ft.Colors.WHITE70,
            icon_size=16,
            tooltip="Cerrar",
            on_click=lambda e: self.toggle_filtros(e),
        )

        self.panel_filtros = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.FILTER_LIST, color=ft.Colors.GREEN_300, size=16),
                    ft.Text("Filtros", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_300),
                    btn_cerrar_filtros,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.filtro_tipo,
                self.filtro_estado,
                ft.Row([self.filtro_fecha_desde, self.btn_fecha_desde], spacing=0),
                ft.Row([self.filtro_fecha_hasta, self.btn_fecha_hasta], spacing=0),
                ft.Row([btn_aplicar, btn_limpiar], spacing=5, alignment=ft.MainAxisAlignment.END),
            ], spacing=6),
            bgcolor=ft.Colors.GREEN_800,
            border=ft.border.all(1, ft.Colors.GREEN_600),
            border_radius=10,
            padding=12,
            width=220,
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=2, color=ft.Colors.BLACK54),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )

        # ── BOTÓN TOGGLE FILTROS ───────────────────────────────────────────────
        self.btn_toggle_filtros = ft.IconButton(
            icon=ft.Icons.FILTER_LIST,
            icon_color=ft.Colors.WHITE,
            icon_size=22,
            tooltip="Mostrar filtros",
            on_click=self.toggle_filtros,
        )

        # ── BARRA SUPERIOR ─────────────────────────────────────────────────────
        barra_superior = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text("Panel de Administrador", size=24, weight="bold", color=ft.Colors.WHITE),
                    padding=ft.padding.only(left=15)
                ),
                ft.Row([
                    self.buscador,
                    self.btn_toggle_filtros,
                    menu_opciones,
                ], spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(15),
            bgcolor=ft.Colors.GREEN_800,
            border=ft.border.all(2, ft.Colors.GREEN_900),
            border_radius=10,
            offset=ft.Offset(0, -0.5),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT),
            opacity=0,
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_IN),
        )

        # ── TABLA ──────────────────────────────────────────────────────────────
        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre Completo", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=13)),
                ft.DataColumn(ft.Text("Jerarquía", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=13)),
                ft.DataColumn(ft.Text("Tipo de Permiso", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=13)),
                ft.DataColumn(ft.Text("Inicio", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=13)),
                ft.DataColumn(ft.Text("Vencimiento", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=13)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=13)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=13)),
            ],
            rows=[],
            border_radius=10,
            column_spacing=25,
            heading_row_color=ft.Colors.GREEN_800,
            heading_row_height=50,
            data_row_min_height=48,
            data_row_max_height=60,
            divider_thickness=1,
        )

        self.lbl_titulo = ft.Text(
            f"Permisos Registrados  ({len(self.todos_los_permisos)})",
            size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE
        )

        self.tabla_container = ft.Container(
            content=self.tabla,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREEN_200),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )

        self.mensaje_vacio = ft.Column(
            controls=[
                ft.Container(height=40),
                ft.Icon(ft.Icons.INBOX_OUTLINED, size=70, color=ft.Colors.GREY_300),
                ft.Text("No hay permisos que coincidan con los filtros.", color=ft.Colors.GREY_400, size=16),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            visible=False,
        )

        self.actualizar_tabla(self.permisos_filtrados)

        # ── PANELES DE RESUMEN ─────────────────────────────────────────────────
        panel_totales, panel_por_expirar, panel_expirados = self._crear_paneles()

        fila_paneles = ft.Row(
            controls=[panel_totales, panel_por_expirar, panel_expirados],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        cuerpo = ft.Column(
            controls=[
                self.lbl_titulo,
                self.tabla_container,
                self.mensaje_vacio,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        contenido_animado = ft.Container(
            content=cuerpo,
            padding=ft.padding.all(25),
            expand=True,
            offset=ft.Offset(0, 0.3),
            animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
            opacity=0,
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN),
        )

        columna_principal = ft.Column(
            controls=[barra_superior, fila_paneles, contenido_animado],
            expand=True,
        )

        self._panel_filtros_flotante = ft.Container(
            content=self.panel_filtros,
            right=20,
            top=55,
        )

        self.controls = [columna_principal]

        self._barra = barra_superior
        self._panel_totales = panel_totales
        self._panel_por_expirar = panel_por_expirar
        self._panel_expirados = panel_expirados
        self._contenido = contenido_animado

    # ── TOGGLE FILTROS ────────────────────────────────────────────────────────

    def toggle_filtros(self, e):
        self.filtros_abiertos = not self.filtros_abiertos
        if self.filtros_abiertos:
            self.btn_toggle_filtros.icon = ft.Icons.FILTER_LIST_OFF
            self.btn_toggle_filtros.tooltip = "Ocultar filtros"
            self.btn_toggle_filtros.icon_color = ft.Colors.AMBER_300
            self.controls.append(self._panel_filtros_flotante)
        else:
            self.btn_toggle_filtros.icon = ft.Icons.FILTER_LIST
            self.btn_toggle_filtros.tooltip = "Mostrar filtros"
            self.btn_toggle_filtros.icon_color = ft.Colors.WHITE
            if self._panel_filtros_flotante in self.controls:
                self.controls.remove(self._panel_filtros_flotante)
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

    # ── MÉTODOS DE FILTRADO ───────────────────────────────────────────────────

    def aplicar_filtros(self):
        texto = (self.buscador.value or "").strip().lower()
        tipo = self.filtro_tipo.value
        estado = self.filtro_estado.value
        hoy = datetime.now().date()
        manana = hoy + timedelta(days=1)

        resultado = []
        for p in self.todos_los_permisos:
            if texto:
                nombre_completo = f"{p.get('nombres', '')} {p.get('apellidos', '')}".lower()
                cedula = p.get('cedula', '').lower()
                if texto not in nombre_completo and texto not in cedula:
                    continue

            if tipo and tipo != "Todos":
                if p.get('tipo_permiso', '') != tipo:
                    continue

            if estado and estado != "Todos":
                fecha_hasta_str = p.get("fecha_hasta", "")
                if not fecha_hasta_str:
                    continue
                try:
                    fecha_hasta = datetime.strptime(fecha_hasta_str, "%d/%m/%Y").date()
                    if estado == "Expirado" and fecha_hasta >= hoy:
                        continue
                    if estado == "Por Expirar" and fecha_hasta != manana:
                        continue
                    if estado == "Vigente" and fecha_hasta <= hoy:
                        continue
                except ValueError:
                    continue

            fecha_desde_permiso = p.get("fecha_desde", "")
            if self.fecha_filtro_desde and fecha_desde_permiso:
                try:
                    fd = datetime.strptime(fecha_desde_permiso, "%d/%m/%Y").date()
                    if fd < self.fecha_filtro_desde:
                        continue
                except ValueError:
                    pass

            if self.fecha_filtro_hasta and fecha_desde_permiso:
                try:
                    fd = datetime.strptime(fecha_desde_permiso, "%d/%m/%Y").date()
                    if fd > self.fecha_filtro_hasta:
                        continue
                except ValueError:
                    pass

            resultado.append(p)

        self.permisos_filtrados = resultado
        self.actualizar_tabla(resultado)

    def limpiar_filtros(self):
        self.buscador.value = ""
        self.filtro_tipo.value = "Todos"
        self.filtro_estado.value = "Todos"
        self.filtro_fecha_desde.value = ""
        self.filtro_fecha_hasta.value = ""
        self.fecha_filtro_desde = None
        self.fecha_filtro_hasta = None
        self.permisos_filtrados = list(self.todos_los_permisos)
        self.actualizar_tabla(self.todos_los_permisos)
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

    # ── ACTUALIZAR TABLA ──────────────────────────────────────────────────────

    def actualizar_tabla(self, permisos):
        hoy = datetime.now().date()

        def obtener_estado(p):
            fecha_hasta_str = p.get("fecha_hasta", "")
            if not fecha_hasta_str:
                return "Sin fecha", ft.Colors.GREY
            try:
                fecha_hasta = datetime.strptime(fecha_hasta_str, "%d/%m/%Y").date()
                diff = (fecha_hasta - hoy).days
                if diff < 0:
                    return "Expirado", ft.Colors.RED
                elif diff == 0:
                    return "Expira hoy", ft.Colors.ORANGE
                elif diff == 1:
                    return "Por Expirar", ft.Colors.AMBER
                else:
                    return "Vigente", ft.Colors.GREEN
            except ValueError:
                return "—", ft.Colors.GREY

        filas = []
        for p in permisos:
            estado_texto, estado_color = obtener_estado(p)
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(
                            f"{p.get('nombres', '')} {p.get('apellidos', '')}",
                            size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500
                        )),
                        ft.DataCell(ft.Text(
                            p.get('grado_jerarquia', ''),
                            size=13, color=ft.Colors.WHITE
                        )),
                        ft.DataCell(ft.Container(
                            content=ft.Text(p.get('tipo_permiso', ''), size=12, color=ft.Colors.BLUE_800),
                            bgcolor=ft.Colors.BLUE_50,
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )),
                        ft.DataCell(ft.Container(
                            content=ft.Text(p.get("fecha_desde", ""), size=13, color=ft.Colors.GREEN_800),
                            bgcolor=ft.Colors.GREEN_50,
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )),
                        ft.DataCell(ft.Container(
                            content=ft.Text(p.get("fecha_hasta", ""), size=13, color=ft.Colors.RED_800),
                            bgcolor=ft.Colors.RED_50,
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )),
                        ft.DataCell(ft.Container(
                            content=ft.Text(estado_texto, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            bgcolor=estado_color,
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    icon_color=ft.Colors.BLUE_700,
                                    icon_size=20,
                                    tooltip="Editar",
                                    on_click=lambda e, pid=p.get('id'): self.on_edit(pid) if self.on_edit else None
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=ft.Colors.RED_700,
                                    icon_size=20,
                                    tooltip="Eliminar",
                                    on_click=lambda e, pid=p.get('id'): self.confirmar_eliminacion(pid)
                                ),
                            ], spacing=0)
                        ),
                    ],
                    color={ft.ControlState.HOVERED: ft.Colors.GREEN_50}
                )
            )

        self.tabla.rows = filas

        total = len(self.todos_los_permisos)
        filtrados = len(permisos)

        if filtrados == total:
            self.lbl_titulo.value = f"Permisos Registrados  ({total})"
        else:
            self.lbl_titulo.value = f"Permisos Filtrados  ({filtrados} de {total})"

        self.tabla_container.visible = len(permisos) > 0
        self.mensaje_vacio.visible = len(permisos) == 0

        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

    # ── CALENDARIOS DE FILTRO ─────────────────────────────────────────────────

    def abrir_calendario_desde_filtro(self, e):
        if self.dp_filtro_desde not in self.page.overlay:
            self.page.overlay.append(self.dp_filtro_desde)
        self.dp_filtro_desde.open = True
        self.page.update()

    def cambio_filtro_desde(self, e):
        if self.dp_filtro_desde.value:
            self.fecha_filtro_desde = self.dp_filtro_desde.value.replace(tzinfo=None).date()
            self.filtro_fecha_desde.value = self.fecha_filtro_desde.strftime("%d/%m/%Y")
            self.filtro_fecha_desde.update()
            self.aplicar_filtros()

    def abrir_calendario_hasta_filtro(self, e):
        if self.dp_filtro_hasta not in self.page.overlay:
            self.page.overlay.append(self.dp_filtro_hasta)
        self.dp_filtro_hasta.open = True
        self.page.update()

    def cambio_filtro_hasta(self, e):
        if self.dp_filtro_hasta.value:
            self.fecha_filtro_hasta = self.dp_filtro_hasta.value.replace(tzinfo=None).date()
            self.filtro_fecha_hasta.value = self.fecha_filtro_hasta.strftime("%d/%m/%Y")
            self.filtro_fecha_hasta.update()
            self.aplicar_filtros()

    # ── PANELES DE RESUMEN ────────────────────────────────────────────────────

    def _crear_paneles(self):
        hoy = datetime.now().date()
        manana = hoy + timedelta(days=1)

        total_permisos = len(self.todos_los_permisos)
        por_expirar = 0
        expirados = 0

        for p in self.todos_los_permisos:
            fecha_hasta_str = p.get("fecha_hasta", "")
            if fecha_hasta_str:
                try:
                    fecha_hasta = datetime.strptime(fecha_hasta_str, "%d/%m/%Y").date()
                    if fecha_hasta == manana:
                        por_expirar += 1
                    elif fecha_hasta < hoy:
                        expirados += 1
                except ValueError:
                    pass

        panel_totales = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.ASSIGNMENT_OUTLINED, size=22, color=ft.Colors.GREEN_300),
                    ft.Text(str(total_permisos), size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("Permisos Totales", size=10, color=ft.Colors.GREEN_200),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            bgcolor=ft.Colors.GREEN_800,
            border_radius=10,
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
            expand=True,
            alignment=ft.Alignment(0, 0),
            border=ft.border.all(1, ft.Colors.GREEN_600),
            offset=ft.Offset(0, 0.3),
            animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
            opacity=0,
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN),
        )

        panel_por_expirar = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=22, color=ft.Colors.AMBER_300),
                    ft.Text(str(por_expirar), size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("Por Expirar (1 día)", size=10, color=ft.Colors.AMBER_200),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            bgcolor=ft.Colors.AMBER_800,
            border_radius=10,
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
            expand=True,
            alignment=ft.Alignment(0, 0),
            border=ft.border.all(1, ft.Colors.AMBER_600),
            offset=ft.Offset(0, 0.3),
            animate_offset=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
            opacity=0,
            animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_IN),
        )

        panel_expirados = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.CANCEL_OUTLINED, size=22, color=ft.Colors.RED_300),
                    ft.Text(str(expirados), size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("Expirados", size=10, color=ft.Colors.RED_200),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            bgcolor=ft.Colors.RED_800,
            border_radius=10,
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
            expand=True,
            alignment=ft.Alignment(0, 0),
            border=ft.border.all(1, ft.Colors.RED_600),
            offset=ft.Offset(0, 0.3),
            animate_offset=ft.Animation(700, ft.AnimationCurve.EASE_OUT),
            opacity=0,
            animate_opacity=ft.Animation(700, ft.AnimationCurve.EASE_IN),
        )

        return panel_totales, panel_por_expirar, panel_expirados

    # ── CONFIRMAR ELIMINACIÓN ─────────────────────────────────────────────────

    def confirmar_eliminacion(self, permiso_id):
        def cerrar_dialogo(e):
            dialogo.open = False
            self.page.update()

        def eliminar_y_cerrar(e):
            if self.on_delete:
                self.on_delete(permiso_id)
            dialogo.open = False
            self.page.update()

        dialogo = ft.AlertDialog(
            title=ft.Text("¿Confirmar eliminación?"),
            content=ft.Text("Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.TextButton("Eliminar", on_click=eliminar_y_cerrar, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialogo)
        dialogo.open = True
        self.page.update()

    # ── ANIMACIONES AL MONTAR ─────────────────────────────────────────────────

    def did_mount(self):
        self._barra.opacity = 1
        self._barra.offset = ft.Offset(0, 0)
        self._panel_totales.opacity = 1
        self._panel_totales.offset = ft.Offset(0, 0)
        self._panel_por_expirar.opacity = 1
        self._panel_por_expirar.offset = ft.Offset(0, 0)
        self._panel_expirados.opacity = 1
        self._panel_expirados.offset = ft.Offset(0, 0)
        self._contenido.opacity = 1
        self._contenido.offset = ft.Offset(0, 0)
        self.page.update()
