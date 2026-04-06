import flet as ft
import asyncio
from datetime import datetime
from utils.estado_utils import obtener_estado, fecha_a_datetime, obtener_estado_urgencia, contar_expiracion_proxima, nombre_completo
from utils.constants import FECHA_FORMAT, TIPOS_PERMISO, DIAS_EXPIRACION_PRONTO
from views.components import TopBar, SummaryCards, FilterPanel, NotificationPanel, PermisosTable, PaginationBar


class AdminView(ft.Stack):
    def __init__(self, on_add_permission=None, lista_permisos=None, on_edit=None, on_delete=None, on_view_detail=None, on_logout=None, usuario=None, on_export=None, on_backup=None, on_change_password=None):
        super().__init__()
        self.expand = True

        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_view_detail = on_view_detail
        self.on_logout = on_logout
        self.usuario = usuario
        self._on_export = on_export
        self._on_backup = on_backup
        self._on_change_password = on_change_password

        self.todos_los_permisos = lista_permisos or []
        self.permisos_filtrados = list(self.todos_los_permisos)

        self.pagina_actual = 1
        self.registros_por_pagina = 10

        self.filtros_abiertos = False
        self.notificaciones_abiertas = False
        self.menu_abierto = False

        notif_count = self._contar_notificaciones()

        self._filter_panel = FilterPanel(
            on_apply=self.aplicar_filtros,
            on_close=lambda: self.toggle_filtros(None),
            tipos_permiso=sorted(set(p.get("tipo_permiso", "") for p in self.todos_los_permisos if p.get("tipo_permiso")) or TIPOS_PERMISO),
        )

        self._notif_panel = NotificationPanel(
            permisos=self.todos_los_permisos,
            on_view_detail=self.on_view_detail,
            on_mark_read=self._marcar_notif_leida,
            on_filter_by_notif=self._filtrar_por_notif,
            on_close=lambda: self.toggle_notificaciones(None),
        )

        self._top_bar = TopBar(
            on_search=self._on_search,
            on_toggle_filters=self.toggle_filtros,
            on_add_permission=on_add_permission,
            on_confirm_logout=self.confirmar_logout,
            on_toggle_notifications=self.toggle_notificaciones,
            notification_count=notif_count,
            usuario=usuario,
            on_open_export=self._abrir_export_dialog,
            on_backup=self._crear_backup,
            on_change_password=self._abrir_cambio_password,
        )

        self._summary = SummaryCards(permisos=self.todos_los_permisos)

        self._table = PermisosTable(
            permisos=self.permisos_filtrados,
            on_edit=self.on_edit,
            on_delete_confirm=self.confirmar_eliminacion,
            on_view_detail=self.on_view_detail,
        )

        self._pagination = PaginationBar(
            on_change_page=self.cambiar_pagina,
            on_change_ppp=self.cambiar_registros_pagina,
        )

        self.lbl_titulo = ft.Text(
            f"Permisos Registrados  ({len(self.todos_los_permisos)})",
            size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE
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

        self.tabla_container = ft.Container(
            content=self._table,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREEN_200),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )

        cuerpo = ft.Column(
            controls=[
                self.lbl_titulo,
                self.tabla_container,
                self._pagination,
                self.mensaje_vacio,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        self._contenido = ft.Container(
            content=cuerpo,
            padding=ft.padding.all(25),
            expand=True,
            offset=ft.Offset(0, 0.3),
            animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
            opacity=0,
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN),
        )

        self._panel_filtros_flotante = ft.Container(
            content=self._filter_panel,
            right=20,
            top=55,
            opacity=0,
            animate_opacity=ft.Animation(150, ft.AnimationCurve.EASE_IN),
            visible=False,
        )

        self._panel_notif_flotante = ft.Container(
            content=self._notif_panel,
            right=60,
            top=55,
            opacity=0,
            animate_opacity=ft.Animation(150, ft.AnimationCurve.EASE_IN),
            visible=False,
        )

        self._panel_menu_flotante = ft.Container(
            content=self._top_bar._panel_menu,
            right=140,
            top=55,
            opacity=0,
            animate_opacity=ft.Animation(150, ft.AnimationCurve.EASE_IN),
            visible=False,
        )

        self._top_bar.btn_menu.on_click = self.toggle_menu

        self.controls = [
            ft.Column([
                self._top_bar,
                self._summary,
                self._contenido,
            ], expand=True),
            self._panel_filtros_flotante,
            self._panel_notif_flotante,
            self._panel_menu_flotante,
        ]

        self._export_pendiente = None

        self.actualizar_tabla(self.permisos_filtrados)

    def did_mount(self):
        if self.page:
            self._filter_panel.set_page(self.page)

        async def animate():
            try:
                await asyncio.sleep(0.05)
                self._top_bar.opacity = 1
                self._top_bar.offset = ft.Offset(0, 0)
                for card in self._summary.controls:
                    card.opacity = 1
                    card.offset = ft.Offset(0, 0)
                self._contenido.opacity = 1
                self._contenido.offset = ft.Offset(0, 0)
                self.page.update()

                if self._notif_panel.get_count() > 0:
                    await asyncio.sleep(0.6)
                    total = self._notif_panel.get_count()
                    snack = ft.SnackBar(
                        content=ft.Text(
                            "%d permiso%s vence%s en los proximos 3 dias" % (total, "s" if total > 1 else "", "n" if total > 1 else "")
                        ),
                        bgcolor=ft.Colors.AMBER_800,
                        duration=4000,
                    )
                    self.page.overlay.append(snack)
                    snack.open = True
                    self.page.update()
            except Exception:
                pass

        task = asyncio.create_task(animate())
        task.add_done_callback(lambda t: t.exception() if t.exception() else None)

    def _contar_notificaciones(self):
        return contar_expiracion_proxima(self.todos_los_permisos)

    def _actualizar_ui(self, *controles):
        if not self.page:
            return
        try:
            for c in controles:
                c.update()
        except RuntimeError:
            pass

    def _cerrar_paneles(self):
        cambios = []
        if self.notificaciones_abiertas:
            self.notificaciones_abiertas = False
            self._top_bar.btn_notificaciones.controls[0].icon = ft.Icons.NOTIFICATIONS_OUTLINED
            self._panel_notif_flotante.visible = False
            self._panel_notif_flotante.opacity = 0
            cambios += [self._top_bar.btn_notificaciones, self._panel_notif_flotante]
        if self.filtros_abiertos:
            self.filtros_abiertos = False
            self._top_bar.btn_toggle_filtros.icon = ft.Icons.FILTER_LIST
            self._top_bar.btn_toggle_filtros.tooltip = "Mostrar filtros"
            self._top_bar.btn_toggle_filtros.icon_color = ft.Colors.WHITE
            self._panel_filtros_flotante.visible = False
            self._panel_filtros_flotante.opacity = 0
            cambios += [self._top_bar.btn_toggle_filtros, self._panel_filtros_flotante]
        if self.menu_abierto:
            self.menu_abierto = False
            self._top_bar.btn_menu.icon = ft.Icons.MENU
            self._top_bar.btn_menu.tooltip = "Menu"
            self._top_bar.btn_menu.icon_color = ft.Colors.WHITE
            self._panel_menu_flotante.visible = False
            self._panel_menu_flotante.opacity = 0
            cambios += [self._top_bar.btn_menu, self._panel_menu_flotante]
        self._actualizar_ui(*cambios)

    def toggle_filtros(self, e):
        if self.filtros_abiertos:
            self.filtros_abiertos = False
            self._top_bar.btn_toggle_filtros.icon = ft.Icons.FILTER_LIST
            self._top_bar.btn_toggle_filtros.tooltip = "Mostrar filtros"
            self._top_bar.btn_toggle_filtros.icon_color = ft.Colors.WHITE
            self._panel_filtros_flotante.visible = False
            self._panel_filtros_flotante.opacity = 0
        else:
            self._cerrar_paneles()
            self.filtros_abiertos = True
            self._top_bar.btn_toggle_filtros.icon = ft.Icons.FILTER_LIST_OFF
            self._top_bar.btn_toggle_filtros.tooltip = "Ocultar filtros"
            self._top_bar.btn_toggle_filtros.icon_color = ft.Colors.AMBER_300
            self._panel_filtros_flotante.visible = True
            self._panel_filtros_flotante.opacity = 1
        self._actualizar_ui(self._top_bar.btn_toggle_filtros, self._panel_filtros_flotante)

    def toggle_notificaciones(self, e):
        if self.notificaciones_abiertas:
            self.notificaciones_abiertas = False
            self._top_bar.btn_notificaciones.controls[0].icon = ft.Icons.NOTIFICATIONS_OUTLINED
            self._panel_notif_flotante.visible = False
            self._panel_notif_flotante.opacity = 0
        else:
            self._cerrar_paneles()
            self.notificaciones_abiertas = True
            self._top_bar.btn_notificaciones.controls[0].icon = ft.Icons.NOTIFICATIONS
            self._panel_notif_flotante.visible = True
            self._panel_notif_flotante.opacity = 1
        self._actualizar_ui(self._top_bar.btn_notificaciones, self._panel_notif_flotante)

    def toggle_menu(self, e):
        if self.menu_abierto:
            self.menu_abierto = False
            self._top_bar.btn_menu.icon = ft.Icons.MENU
            self._top_bar.btn_menu.tooltip = "Menu"
            self._top_bar.btn_menu.icon_color = ft.Colors.WHITE
            self._panel_menu_flotante.visible = False
            self._panel_menu_flotante.opacity = 0
        else:
            self._cerrar_paneles()
            self.menu_abierto = True
            self._top_bar.btn_menu.icon = ft.Icons.CLOSE
            self._top_bar.btn_menu.tooltip = "Cerrar menu"
            self._top_bar.btn_menu.icon_color = ft.Colors.AMBER_300
            self._panel_menu_flotante.visible = True
            self._panel_menu_flotante.opacity = 1
        self._actualizar_ui(self._top_bar.btn_menu, self._panel_menu_flotante)

    def _on_search(self, texto):
        self.aplicar_filtros(texto_busqueda=texto)

    def aplicar_filtros(self, texto_busqueda=None):
        texto = (texto_busqueda if texto_busqueda is not None else (self._top_bar.buscador.value or "")).strip().lower()
        filtros = self._filter_panel.get_filtros()
        tipo = filtros["tipo"]
        estado = filtros["estado"]

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
                estado_texto, _ = obtener_estado(p.get("fecha_hasta", ""))
                if estado_texto != estado:
                    continue

            fd = fecha_a_datetime(p.get("fecha_desde", ""))
            if filtros["fecha_desde"] and fd:
                if fd < filtros["fecha_desde"]:
                    continue
            if filtros["fecha_hasta"] and fd:
                if fd > filtros["fecha_hasta"]:
                    continue

            resultado.append(p)

        self.permisos_filtrados = resultado
        self.pagina_actual = 1
        self.actualizar_tabla(resultado)

    def limpiar_filtros(self):
        self._top_bar.buscador.value = ""
        self._filter_panel.limpiar_filtros()
        self.permisos_filtrados = list(self.todos_los_permisos)
        self.pagina_actual = 1
        self.actualizar_tabla(self.todos_los_permisos)
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

    def cambiar_pagina(self, delta):
        total_registros = len(self.permisos_filtrados)
        total_paginas = max(1, (total_registros + self.registros_por_pagina - 1) // self.registros_por_pagina)
        nueva_pagina = self.pagina_actual + delta
        if 1 <= nueva_pagina <= total_paginas:
            self.pagina_actual = nueva_pagina

        self.actualizar_tabla(self.permisos_filtrados)

    def cambiar_registros_pagina(self):
        self.registros_por_pagina = self._pagination.get_ppp()
        self.pagina_actual = 1
        self.actualizar_tabla(self.permisos_filtrados)

    def actualizar_tabla(self, permisos):
        total_registros = len(permisos)
        total_paginas = max(1, (total_registros + self.registros_por_pagina - 1) // self.registros_por_pagina)
        self.pagina_actual = max(1, min(self.pagina_actual, total_paginas))

        inicio = (self.pagina_actual - 1) * self.registros_por_pagina
        fin = inicio + self.registros_por_pagina
        pagina_permisos = permisos[inicio:fin]

        permisos_ordenados = self._table.get_sorted(pagina_permisos)
        filas = self._table.render_filas(permisos_ordenados, inicio)
        self._table.tabla.rows = filas

        self._pagination.actualizar(self.pagina_actual, total_paginas, total_registros)

        total = len(self.todos_los_permisos)
        filtrados = total_registros

        if filtrados == total:
            self.lbl_titulo.value = f"Permisos Registrados  ({total})"
        else:
            self.lbl_titulo.value = f"Permisos Filtrados  ({filtrados} de {total})"

        self.tabla_container.visible = total_registros > 0
        self.mensaje_vacio.visible = total_registros == 0

        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

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
            title=ft.Text("Confirmar eliminacion"),
            content=ft.Text("Esta accion no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.TextButton("Eliminar", on_click=eliminar_y_cerrar, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialogo)
        dialogo.open = True
        self.page.update()

    def confirmar_logout(self):
        def cerrar_dialogo(e):
            dialogo.open = False
            self.page.update()

        def logout_y_cerrar(e):
            dialogo.open = False
            self.page.update()
            if self.on_logout:
                self.on_logout()

        dialogo = ft.AlertDialog(
            title=ft.Text("Cerrar sesion"),
            content=ft.Text("Estas seguro de que deseas cerrar sesion?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.TextButton("Cerrar sesion", on_click=logout_y_cerrar, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialogo)
        dialogo.open = True
        self.page.update()

    def _marcar_notif_leida(self):
        self._notif_panel.marcar_leida()
        self._top_bar.update_badge(0)
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

    def _filtrar_por_notif(self, tipo):
        hoy = datetime.now().date()

        resultado = []
        for p in self.todos_los_permisos:
            fecha_hasta = fecha_a_datetime(p.get("fecha_hasta", ""))
            if fecha_hasta:
                diff = (fecha_hasta - hoy).days
                if tipo == "hoy" and diff == 0:
                    resultado.append(p)
                elif tipo == "manana" and diff == 1:
                    resultado.append(p)
                elif tipo == "proximos" and 2 <= diff <= 3:
                    resultado.append(p)

        self._cerrar_paneles()
        self._top_bar.buscador.value = ""
        self._filter_panel.filtro_tipo.value = "Todos"
        self._filter_panel.filtro_estado.value = "Todos"
        self.permisos_filtrados = resultado
        self.pagina_actual = 1
        self.actualizar_tabla(resultado)

    def refrescar_datos(self):
        from models.permiso_model import PermisoModel
        self.todos_los_permisos = PermisoModel.get_all()
        self._summary.actualizar(self.todos_los_permisos)
        self._notif_panel.actualizar_permisos(self.todos_los_permisos)
        self._top_bar.update_badge(self._notif_panel.get_count())
        self.aplicar_filtros()

    def _abrir_export_dialog(self):
        from views.components.export_dialog import ExportDialog
        dialog = ExportDialog(
            permisos=self.permisos_filtrados,
            on_export=lambda template: self._ejecutar_export(template),
            usuario=self.usuario,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _ejecutar_export(self, template_key):
        self._cerrar_paneles()
        if hasattr(self, '_on_export'):
            self._on_export(self.permisos_filtrados, template_key)

    def _crear_backup(self):
        self._cerrar_paneles()
        if hasattr(self, '_on_backup'):
            self._on_backup()

    def _abrir_cambio_password(self):
        self._cerrar_paneles()
        if hasattr(self, '_on_change_password'):
            self._on_change_password()
