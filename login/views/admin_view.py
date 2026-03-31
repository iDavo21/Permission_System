import flet as ft

class AdminView(ft.Column):
    def __init__(self, on_add_permission=None, lista_permisos=None, on_edit=None, on_delete=None):
        super().__init__()
        self.expand = True
        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        self.on_edit = on_edit
        self.on_delete = on_delete

        permisos = lista_permisos or []

        # --- Menú con opciones ---
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

        # --- Buscador ---
        buscador = ft.TextField(
            hint_text="Buscar...",
            hint_style=ft.TextStyle(color=ft.Colors.WHITE54),
            width=250,
            height=40,
            bgcolor=ft.Colors.WHITE24,
            color=ft.Colors.WHITE,
            border_color=ft.Colors.TRANSPARENT,
            border_radius=15,
            content_padding=ft.padding.only(left=15, right=15),
            text_size=15,
            prefix=ft.Icon(ft.Icons.SEARCH, color=ft.Colors.WHITE, size=20),
            cursor_color=ft.Colors.WHITE
        )

        # --- Barra superior con animación ---
        acciones_derecha = ft.Row(
            controls=[buscador, menu_opciones],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        encabezado = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text("Panel de Administrador", size=24, weight="bold", color=ft.Colors.WHITE),
                    padding=ft.padding.only(left=15)
                ),
                acciones_derecha
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        barra_superior = ft.Container(
            content=encabezado,
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.GREEN_800,
            border=ft.border.all(2, ft.Colors.GREEN_900),
            border_radius=10,
            # Animación de entrada: desliza desde arriba
            offset=ft.Offset(0, -0.5),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT),
            opacity=0,
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_IN),
        )

        # --- Construir filas de la tabla ---
        filas = [
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
                    # Nueva Celda: Acciones
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
            for p in permisos
        ]

        # --- Tabla estilizada ---
        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre Completo", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=13)),
                ft.DataColumn(ft.Text("Jerarquía", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=13)),
                ft.DataColumn(ft.Text("Tipo de Permiso", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=13)),
                ft.DataColumn(ft.Text("Inicio", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=13)),
                ft.DataColumn(ft.Text("Vencimiento", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=13)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=13)),
            ],
            rows=filas,
            border_radius=10,
            column_spacing=30,  # Reducido un poco para que quepan las acciones
            heading_row_color=ft.Colors.GREEN_800,
            heading_row_height=50,
            data_row_min_height=48,
            data_row_max_height=60,
            divider_thickness=1,
        )

        # --- Área de contenido con animación de entrada ---
        if not permisos:
            cuerpo = ft.Column(
                controls=[
                    ft.Container(height=40),
                    ft.Icon(ft.Icons.INBOX_OUTLINED, size=70, color=ft.Colors.GREY_300),
                    ft.Text("No hay permisos registrados aún.", color=ft.Colors.GREY_400, size=16),
                    ft.Text(
                        "Usa el menú ☰ para agregar el primero.",
                        color=ft.Colors.GREY_300, size=13
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        else:
            cuerpo = ft.Column(
                controls=[
                    ft.Container(height=8),
                    ft.Text(
                        f"Permisos Registrados  ({len(permisos)})",
                        size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE
                    ),
                    ft.Container(
                        content=tabla,
                        border_radius=12,
                        border=ft.border.all(1, ft.Colors.GREEN_200),
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.START,
                expand=True
            )

        contenido_animado = ft.Container(
            content=cuerpo,
            padding=ft.padding.all(25),
            expand=True,
            # Anima en deslizando desde abajo
            offset=ft.Offset(0, 0.3),
            animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
            opacity=0,
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN),
        )

        self.controls = [barra_superior, contenido_animado]

        # Referencia a los contenedores para activar animaciones al montar
        self._barra = barra_superior
        self._contenido = contenido_animado

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

    def did_mount(self):
        # Se ejecuta al añadirse a la página: dispara las animaciones
        self._barra.opacity = 1
        self._barra.offset = ft.Offset(0, 0)
        self._contenido.opacity = 1
        self._contenido.offset = ft.Offset(0, 0)
        self.page.update()

