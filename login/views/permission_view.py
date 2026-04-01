import flet as ft
from datetime import datetime

class PermissionView(ft.Container):
    def __init__(self, on_back, on_save=None, datos_iniciales=None, permiso_id=None):
        super().__init__()
        self.expand = True
        self.alignment = ft.Alignment.CENTER
        self.on_back = on_back
        self.on_save = on_save
        self.permiso_id = permiso_id

        W_FULL = 440  # Ancho total de una fila
        W_HALF = 205  # Ancho de media fila

        # ── SECCIÓN 1: Datos Personales ──────────────────────────────────────
        self.primer_nombre   = ft.TextField(label="1er Nombre*", icon=ft.Icons.PERSON, expand=True)
        self.segundo_nombre  = ft.TextField(label="2do Nombre", expand=True)
        self.primer_apellido = ft.TextField(label="1er Apellido*", icon=ft.Icons.PERSON_OUTLINE, expand=True)
        self.segundo_apellido = ft.TextField(label="2do Apellido", expand=True)

        self.cedula = ft.TextField(
            label="Cédula*", icon=ft.Icons.BADGE,
            expand=True, keyboard_type=ft.KeyboardType.NUMBER
        )
        self.telefono = ft.TextField(
            label="Teléfono*", icon=ft.Icons.PHONE,
            expand=True, keyboard_type=ft.KeyboardType.PHONE
        )

        # ── SECCIÓN 2: Información Laboral ────────────────────────────────────
        self.grado_jerarquia = ft.TextField(
            label="Grado de Jerarquía*", icon=ft.Icons.MILITARY_TECH,
            width=W_FULL
        )
        self.cargo = ft.TextField(
            label="Cargo*", icon=ft.Icons.WORK_OUTLINE,
            width=W_FULL
        )

        self.tipo_permiso = ft.Dropdown(
            label="Tipo de Permiso*",
            width=W_FULL,
            options=[
                ft.dropdown.Option("Extraordinario"),
                ft.dropdown.Option("Vacacional"),
                ft.dropdown.Option("Pre Maternal"),
                ft.dropdown.Option("Post Maternal"),
                ft.dropdown.Option("Paternal"),
                ft.dropdown.Option("Operacional"),
                ft.dropdown.Option("Reposo"),
            ]
        )

        # ── SECCIÓN 3: Fechas ─────────────────────────────────────────────────
        hoy = datetime.now()
        self.txt_fecha_elaboracion = ft.TextField(
            label="Fecha de Elaboración",
            icon=ft.Icons.EDIT_DOCUMENT,
            width=W_FULL,
            value=hoy.strftime("%d/%m/%Y"),
            read_only=True
        )

        self.fecha_desde = None
        self.input_desde = ft.TextField(
            label="Inicio*", icon=ft.Icons.EVENT_AVAILABLE,
            width=W_HALF, read_only=True, hint_text="DD/MM/AAAA"
        )
        self.btn_desde = ft.IconButton(
            icon=ft.Icons.CALENDAR_TODAY,
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
            width=W_HALF, read_only=True, hint_text="DD/MM/AAAA"
        )
        self.btn_hasta = ft.IconButton(
            icon=ft.Icons.CALENDAR_TODAY,
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
            color=ft.Colors.BLUE_700,
            size=14
        )

        # Contenedores visuales para cada fecha — Apilados verticalmente para mayor claridad
        bloque_desde = ft.Container(
            content=ft.Column([
                ft.Text("🟢 Inicio del Permiso", size=12, color=ft.Colors.GREEN_700, weight=ft.FontWeight.BOLD),
                ft.Row([self.input_desde, self.btn_desde],
                       vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ], tight=True, spacing=6),
            bgcolor=ft.Colors.BLACK_12,
            border=ft.border.all(1, ft.Colors.GREEN_200),
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            width=W_FULL,
        )
        bloque_hasta = ft.Container(
            content=ft.Column([
                ft.Text("🔴 Vencimiento del Permiso", size=12, color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD),
                ft.Row([self.input_hasta, self.btn_hasta],
                       vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ], tight=True, spacing=6),
            bgcolor=ft.Colors.BLACK_12,
            border=ft.border.all(1, ft.Colors.RED_200),
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            width=W_FULL,
        )

        # ── SECCIÓN 4: Direcciones ────────────────────────────────────────────
        self.dir_domiciliaria = ft.TextField(
            label="Dirección Domiciliaria*", icon=ft.Icons.HOME_OUTLINED,
            width=W_FULL, multiline=True, min_lines=2, max_lines=3
        )
        self.dir_emergencia = ft.TextField(
            label="Dirección de Emergencia*", icon=ft.Icons.LOCAL_HOSPITAL_OUTLINED,
            width=W_FULL, multiline=True, min_lines=2, max_lines=3
        )

        # ── SECCIÓN 5: Observaciones ──────────────────────────────────────────
        self.observaciones = ft.TextField(
            label="Observaciones", icon=ft.Icons.NOTES,
            width=W_FULL, multiline=True, min_lines=3, max_lines=5,
            hint_text="Notas adicionales (opcional)"
        )

        # ── PRE-POBLAR SI ES EDICIÓN ─────────────────────────────────────────
        if datos_iniciales:
            # Separar nombres y apellidos (asumiendo formato "Primero Segundo")
            n = datos_iniciales.get("nombres", "").split(" ")
            a = datos_iniciales.get("apellidos", "").split(" ")
            
            self.primer_nombre.value = n[0] if len(n) > 0 else ""
            self.segundo_nombre.value = n[1] if len(n) > 1 else ""
            self.primer_apellido.value = a[0] if len(a) > 0 else ""
            self.segundo_apellido.value = a[1] if len(a) > 1 else ""
            
            self.cedula.value = datos_iniciales.get("cedula", "")
            self.telefono.value = datos_iniciales.get("telefono", "")
            self.grado_jerarquia.value = datos_iniciales.get("grado_jerarquia", "")
            self.cargo.value = datos_iniciales.get("cargo", "")
            self.tipo_permiso.value = datos_iniciales.get("tipo_permiso", "")
            self.txt_fecha_elaboracion.value = datos_iniciales.get("fecha_elaboracion", "")
            
            self.input_desde.value = datos_iniciales.get("fecha_desde", "")
            self.input_hasta.value = datos_iniciales.get("fecha_hasta", "")
            
            # Parsear fechas para los objetos datetime
            try:
                self.fecha_desde = datetime.strptime(self.input_desde.value, "%d/%m/%Y")
                self.fecha_hasta = datetime.strptime(self.input_hasta.value, "%d/%m/%Y")
                self.calcular_dias()
            except:
                pass

            self.dir_domiciliaria.value = datos_iniciales.get("dir_domiciliaria", "")
            self.dir_emergencia.value = datos_iniciales.get("dir_emergencia", "")
            self.observaciones.value = datos_iniciales.get("observaciones", "")

        # ── BOTONES ───────────────────────────────────────────────────────────
        btn_label = "Actualizar Permiso" if permiso_id else "Guardar Permiso"
        btn_icon = ft.Icons.UPDATE if permiso_id else ft.Icons.SAVE
        
        self.btn_guardar = ft.ElevatedButton(
            btn_label,
            icon=btn_icon,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=15
            ),
            width=W_FULL,
            on_click=self.guardar_permiso
        )
        self.btn_volver = ft.TextButton(
            "Volver al Panel",
            icon=ft.Icons.ARROW_BACK,
            icon_color=ft.Colors.GREY_700,
            on_click=lambda e: self.on_back()
        )

        def seccion_titulo(texto, icono):
            """Cabecera de sección estilizada."""
            return ft.Container(
                content=ft.Row([
                    ft.Icon(icono, color=ft.Colors.BLUE_700, size=18),
                    ft.Text(texto, size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
                ], spacing=8),
                padding=ft.padding.only(top=16, bottom=4),
            )

        # ── FORMULARIO COMPLETO ───────────────────────────────────────────────
        header_title = "Editar Permiso" if permiso_id else "Registrar Permiso"
        header_icon = ft.Icons.EDIT_DOCUMENT if permiso_id else ft.Icons.ASSIGNMENT_ADD

        formulario = ft.Column(
            controls=[
                # Encabezado
                ft.Icon(header_icon, size=48, color=ft.Colors.BLUE_700),
                ft.Text(header_title, size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Completa todos los campos obligatorios (*)", color=ft.Colors.GREY_500, size=13),
                ft.Divider(color=ft.Colors.GREY_200),

                # — Datos Personales —
                seccion_titulo("Datos Personales", ft.Icons.PERSON),
                ft.Row([self.primer_nombre, self.segundo_nombre], spacing=15, width=W_FULL),
                ft.Row([self.primer_apellido, self.segundo_apellido], spacing=15, width=W_FULL),
                ft.Row([self.cedula, self.telefono], spacing=15, width=W_FULL),

                # — Información Laboral —
                seccion_titulo("Información Laboral", ft.Icons.WORK),
                self.grado_jerarquia,
                self.cargo,
                self.tipo_permiso,

                # — Fechas —
                seccion_titulo("Período del Permiso", ft.Icons.DATE_RANGE),
                self.txt_fecha_elaboracion,
                # Bloques de fecha apilados verticalmente con flecha separadora
                bloque_desde,
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ARROW_DOWNWARD, color=ft.Colors.GREY_400, size=20),
                        ft.Text("hasta", color=ft.Colors.GREY_500, size=12),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=4,
                ),
                bloque_hasta,
                ft.Container(height=10),  # espacio antes de días totales
                ft.Container(
                    content=self.lbl_total_dias,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=14, vertical=8),
                    width=W_FULL,
                ),

                # — Direcciones —
                seccion_titulo("Datos de Contacto", ft.Icons.LOCATION_ON_OUTLINED),
                self.dir_domiciliaria,
                self.dir_emergencia,

                # — Observaciones —
                seccion_titulo("Observaciones", ft.Icons.NOTES),
                self.observaciones,

                ft.Divider(color=ft.Colors.GREY_200),
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
            elevation=8,
            shape=ft.RoundedRectangleBorder(radius=15),
            content=ft.Container(
                padding=ft.padding.only(top=30, bottom=30, left=35, right=35),
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

    # ── CICLO DE VIDA ─────────────────────────────────────────────────────────
    def did_mount(self):
        self._card_wrapper.opacity = 1
        self._card_wrapper.offset = ft.Offset(0, 0)
        self.update()

    # ── CALENDARIOS ──────────────────────────────────────────────────────────
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
            self.input_desde.value = self.fecha_desde.strftime("%d/%m/%Y")
            self.input_desde.update()
            self.calcular_dias()

    def cambio_hasta(self, e):
        if self.dp_hasta.value:
            self.fecha_hasta = self.dp_hasta.value
            self.input_hasta.value = self.fecha_hasta.strftime("%d/%m/%Y")
            self.input_hasta.update()
            self.calcular_dias()

    def calcular_dias(self):
        if self.fecha_desde and self.fecha_hasta:
            desde = self.fecha_desde.replace(tzinfo=None) if self.fecha_desde.tzinfo else self.fecha_desde
            hasta = self.fecha_hasta.replace(tzinfo=None) if self.fecha_hasta.tzinfo else self.fecha_hasta
            diff = (hasta - desde).days
            if diff < 0:
                self.lbl_total_dias.value = "⚠ Fecha de vencimiento es anterior al inicio"
                self.lbl_total_dias.color = ft.Colors.RED_700
            else:
                self.lbl_total_dias.value = f"📅 Días totales del permiso: {diff + 1}"
                self.lbl_total_dias.color = ft.Colors.BLUE_700
            self.lbl_total_dias.update()

    # ── GUARDAR ──────────────────────────────────────────────────────────────
    def guardar_permiso(self, e):
        campos_obligatorios = {
            "Primer Nombre": self.primer_nombre.value,
            "Primer Apellido": self.primer_apellido.value,
            "Cédula": self.cedula.value,
            "Teléfono": self.telefono.value,
            "Grado de Jerarquía": self.grado_jerarquia.value,
            "Cargo": self.cargo.value,
            "Tipo de Permiso": self.tipo_permiso.value,
            "Fecha Inicio": self.input_desde.value,
            "Fecha Vencimiento": self.input_hasta.value,
            "Dirección Domiciliaria": self.dir_domiciliaria.value,
            "Dirección de Emergencia": self.dir_emergencia.value,
        }

        vacios = [k for k, v in campos_obligatorios.items() if not v or not str(v).strip()]
        if vacios:
            snack = ft.SnackBar(
                ft.Text(f"⚠️ Campo(s) obligatorio(s) vacío(s): {', '.join(vacios)}"),
                bgcolor=ft.Colors.RED_700
            )
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
            return

        nombres  = f"{self.primer_nombre.value} {self.segundo_nombre.value}".strip()
        apellidos = f"{self.primer_apellido.value} {self.segundo_apellido.value}".strip()

        datos = {
            "nombres":            nombres,
            "apellidos":          apellidos,
            "cedula":             self.cedula.value,
            "telefono":           self.telefono.value,
            "grado_jerarquia":    self.grado_jerarquia.value,
            "cargo":              self.cargo.value,
            "tipo_permiso":       self.tipo_permiso.value,
            "fecha_elaboracion":  self.txt_fecha_elaboracion.value,
            "fecha_desde":        self.input_desde.value,
            "fecha_hasta":        self.input_hasta.value,
            "dir_domiciliaria":   self.dir_domiciliaria.value,
            "dir_emergencia":     self.dir_emergencia.value,
            "observaciones":      self.observaciones.value,
        }

        success_msg = "¡Permiso actualizado con éxito!" if self.permiso_id else "¡Permiso registrado con éxito!"
        snack = ft.SnackBar(ft.Text(f"✅ {success_msg}"), bgcolor=ft.Colors.GREEN_700)
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()

        if self.on_save:
            self.on_save(datos)
        else:
            self.on_back()
