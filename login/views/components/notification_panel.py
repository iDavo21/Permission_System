import flet as ft
from utils.estado_utils import clasificar_notificaciones


class NotificationPanel(ft.Container):
    def __init__(self, permisos=None, on_view_detail=None, on_mark_read=None, on_filter_by_notif=None, on_close=None):
        super().__init__()
        self.bgcolor = ft.Colors.GREEN_800
        self.border = ft.border.all(1, ft.Colors.GREEN_600)
        self.border_radius = 10
        self.padding = 12
        self.width = 320
        self.shadow = ft.BoxShadow(blur_radius=15, spread_radius=2, color=ft.Colors.BLACK54)

        self.permisos = permisos or []
        self.on_view_detail = on_view_detail
        self.on_mark_read = on_mark_read
        self.on_filter_by_notif = on_filter_by_notif
        self.on_close = on_close
        self._notificaciones = self._obtener_notificaciones()

        badge_notif = ft.Container(
            content=ft.Text(str(len(self._notificaciones)), size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            bgcolor=ft.Colors.RED_600 if self._notificaciones else ft.Colors.TRANSPARENT,
            border_radius=10,
            width=20, height=20,
            alignment=ft.Alignment(0, 0),
            visible=bool(self._notificaciones),
        )
        self._badge_notif = badge_notif

        self.content = self._crear_contenido()

    def _obtener_notificaciones(self):
        vence_hoy, vence_manana, vence_proximos = clasificar_notificaciones(self.permisos)
        resultado = vence_hoy + vence_manana + vence_proximos
        resultado.sort(key=lambda x: x["_dias_restantes"])
        return resultado

    def _crear_contenido(self):
        btn_cerrar = ft.IconButton(
            icon=ft.Icons.CLOSE, icon_color=ft.Colors.WHITE70, icon_size=16,
            tooltip="Cerrar", on_click=lambda e: self.on_close() if self.on_close else None,
        )

        if not self._notificaciones:
            return ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.NOTIFICATIONS, color=ft.Colors.AMBER_300, size=18),
                    ft.Text("Notificaciones", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300),
                    btn_cerrar,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINED, size=40, color=ft.Colors.GREEN_300),
                        ft.Text("No hay notificaciones", size=13, color=ft.Colors.WHITE70),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20, alignment=ft.Alignment(0, 0),
                ),
            ], spacing=4)

        vence_hoy, vence_manana, vence_proximos = clasificar_notificaciones(self.permisos)
        total = len(self._notificaciones)

        bloques = []
        if vence_hoy:
            bloques.append(ft.GestureDetector(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE, size=16),
                        ft.Text(f"{len(vence_hoy)} vence{'n' if len(vence_hoy)>1 else ''} hoy",
                                size=12, color=ft.Colors.ORANGE, weight=ft.FontWeight.BOLD),
                        ft.Icon(ft.Icons.ARROW_FORWARD_IOS, color=ft.Colors.ORANGE, size=12),
                    ], spacing=6),
                    bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.ORANGE),
                    border_radius=6, padding=ft.padding.symmetric(horizontal=10, vertical=6),
                ),
                on_tap=lambda e: self.on_filter_by_notif("hoy") if self.on_filter_by_notif else None,
                mouse_cursor=ft.MouseCursor.CLICK,
            ))
        if vence_manana:
            bloques.append(ft.GestureDetector(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED, size=16),
                        ft.Text(f"{len(vence_manana)} vence{'n' if len(vence_manana)>1 else ''} ma\u00f1ana",
                                size=12, color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
                        ft.Icon(ft.Icons.ARROW_FORWARD_IOS, color=ft.Colors.RED, size=12),
                    ], spacing=6),
                    bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.RED),
                    border_radius=6, padding=ft.padding.symmetric(horizontal=10, vertical=6),
                ),
                on_tap=lambda e: self.on_filter_by_notif("manana") if self.on_filter_by_notif else None,
                mouse_cursor=ft.MouseCursor.CLICK,
            ))
        if vence_proximos:
            bloques.append(ft.GestureDetector(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SCHEDULE, color=ft.Colors.AMBER, size=16),
                        ft.Text(f"{len(vence_proximos)} vence{'n' if len(vence_proximos)>1 else ''} en los pr\u00f3ximos 3 d\u00edas",
                                size=12, color=ft.Colors.AMBER, weight=ft.FontWeight.BOLD),
                        ft.Icon(ft.Icons.ARROW_FORWARD_IOS, color=ft.Colors.AMBER, size=12),
                    ], spacing=6),
                    bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.AMBER),
                    border_radius=6, padding=ft.padding.symmetric(horizontal=10, vertical=6),
                ),
                on_tap=lambda e: self.on_filter_by_notif("proximos") if self.on_filter_by_notif else None,
                mouse_cursor=ft.MouseCursor.CLICK,
            ))

        btn_marcar_leida = ft.ElevatedButton(
            "Marcar como le\u00edda",
            icon=ft.Icons.DONE_ALL,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600,
                shape=ft.RoundedRectangleBorder(radius=6), padding=10,
            ),
            on_click=lambda e: self.on_mark_read() if self.on_mark_read else None,
        )

        return ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.NOTIFICATIONS, color=ft.Colors.AMBER_300, size=18),
                ft.Text(f"Notificaciones ({total})", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300),
                btn_cerrar,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(
                content=ft.Text(
                    f"Hay {total} permiso{'s' if total > 1 else ''} por vencer",
                    size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500,
                ),
                padding=ft.padding.only(top=4, bottom=4),
            ),
            *bloques,
            ft.Divider(color=ft.Colors.WHITE24, height=1),
            ft.Row([btn_marcar_leida], alignment=ft.MainAxisAlignment.END),
        ], spacing=6)

    def get_count(self):
        return len(self._notificaciones)

    def get_badge(self):
        return self._badge_notif

    def marcar_leida(self):
        self._notificaciones = []
        self._badge_notif.visible = False
        self._badge_notif.bgcolor = ft.Colors.TRANSPARENT
        self.content = self._crear_contenido()

    def actualizar_permisos(self, permisos):
        self.permisos = permisos
        self._notificaciones = self._obtener_notificaciones()
        self._badge_notif.visible = bool(self._notificaciones)
        self._badge_notif.bgcolor = ft.Colors.RED_600 if self._notificaciones else ft.Colors.TRANSPARENT
        self._badge_notif.content.value = str(len(self._notificaciones))
        self.content = self._crear_contenido()
