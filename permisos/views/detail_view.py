import flet as ft
import asyncio
from datetime import datetime
from core.estado_utils import obtener_estado, calcular_dias_permiso
from core.theme import theme_colors
from core.constants import FECHA_FORMAT


class DetailView(ft.Container):
    def __init__(self, datos, on_back=None, on_edit=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.alignment = ft.Alignment.CENTER
        self.on_back = on_back
        self.on_edit = on_edit
        self.datos = datos
        self.permiso_id = datos.get("id")
        self.dark_mode = dark_mode
        tc = theme_colors(self.dark_mode)

        W_FULL = 440
        W_HALF = 205

        estado_texto, estado_color = self._obtener_estado()

        badge_estado = ft.Container(
            content=ft.Text(estado_texto, size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            bgcolor=estado_color,
            border_radius=6,
            padding=ft.padding.symmetric(horizontal=12, vertical=4),
        )

        def campo_ro(label, valor, icono=None, expand=False, width=None):
            kw = {
                "label": label,
                "value": valor or "\u2014",
                "read_only": True,
                "icon": icono,
                "text_size": 13,
                "filled": True,
                "bgcolor": tc["input_bg"],
                "border_color": tc["input_border"],
                "color": tc["input_text"],
                "label_style": ft.TextStyle(color=tc["input_label"]),
            }
            if expand:
                kw["expand"] = True
            if width:
                kw["width"] = width
            return ft.TextField(**kw)

        def seccion_titulo(texto, icono):
            return ft.Container(
                content=ft.Row([
                    ft.Icon(icono, color=ft.Colors.GREEN_400, size=18),
                    ft.Text(texto, size=13, weight=ft.FontWeight.BOLD, color=tc["text_secondary"])
                ], spacing=8),
                padding=ft.padding.only(top=12, bottom=2),
            )

        nombres = datos.get("nombres", "").split(" ", 1)
        apellidos = datos.get("apellidos", "").split(" ", 1)
        fecha_desde_str = datos.get("fecha_desde", "")
        fecha_hasta_str = datos.get("fecha_hasta", "")

        lbl_dias = ft.Text("", weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400, size=14)
        try:
            fd = datetime.strptime(fecha_desde_str, FECHA_FORMAT)
            fh = datetime.strptime(fecha_hasta_str, FECHA_FORMAT)
            diff = (fh - fd).days
            if diff >= 0:
                lbl_dias.value = "Duración: %d día(s)" % (diff + 1)
            else:
                lbl_dias.value = "Fechas inválidas"
                lbl_dias.color = ft.Colors.RED_700
        except (ValueError, TypeError):
            lbl_dias.value = ""

        btn_editar = ft.ElevatedButton(
            "Editar Permiso",
            icon=ft.Icons.EDIT_OUTLINED,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_700,
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=15,
            ),
            width=W_FULL,
            on_click=lambda e: self.on_edit(self.permiso_id) if self.on_edit else None,
        )
        btn_volver = ft.TextButton(
            "Volver al Panel",
            icon=ft.Icons.ARROW_BACK,
            icon_color=tc["text_secondary"],
            on_click=lambda e: self.on_back() if self.on_back else None,
        )

        formulario = ft.Column(
            controls=[
                ft.Icon(ft.Icons.ASSIGNMENT_OUTLINED, size=48, color=ft.Colors.GREEN_400),
                ft.Text("Detalle del Permiso", size=24, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                badge_estado,
                ft.Divider(color=tc["divider"]),

                seccion_titulo("Datos Personales", ft.Icons.PERSON),
                ft.Row([campo_ro("1er Nombre", nombres[0] if nombres else "", ft.Icons.PERSON, expand=True),
                        campo_ro("2do Nombre", nombres[1] if len(nombres) > 1 else "", expand=True)],
                       spacing=15, width=W_FULL),
                ft.Row([campo_ro("1er Apellido", apellidos[0] if apellidos else "", ft.Icons.PERSON_OUTLINE, expand=True),
                        campo_ro("2do Apellido", apellidos[1] if len(apellidos) > 1 else "", expand=True)],
                       spacing=15, width=W_FULL),
                ft.Row([campo_ro("Cédula", datos.get("cedula"), ft.Icons.BADGE, expand=True),
                        campo_ro("Teléfono", datos.get("telefono"), ft.Icons.PHONE, expand=True)],
                       spacing=15, width=W_FULL),

                seccion_titulo("Información Laboral", ft.Icons.WORK),
                campo_ro("Grado de Jerarquía", datos.get("grado_jerarquia"), ft.Icons.MILITARY_TECH, width=W_FULL),
                campo_ro("Cargo", datos.get("cargo"), ft.Icons.WORK_OUTLINED, width=W_FULL),
                campo_ro("Tipo de Permiso", datos.get("tipo_permiso"), ft.Icons.ASSIGNMENT, width=W_FULL),

                seccion_titulo("Período del Permiso", ft.Icons.DATE_RANGE),
                campo_ro("Fecha de Elaboración", datos.get("fecha_elaboracion"), ft.Icons.EDIT_DOCUMENT, width=W_FULL),
                ft.Row([campo_ro("Desde", fecha_desde_str, ft.Icons.EVENT_AVAILABLE, expand=True),
                        campo_ro("Hasta", fecha_hasta_str, ft.Icons.EVENT_BUSY, expand=True)],
                       spacing=15, width=W_FULL),
                ft.Container(
                    content=lbl_dias,
                    bgcolor=tc["badge_green"],
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=14, vertical=6),
                    width=W_FULL,
                    visible=bool(lbl_dias.value),
                ),

                seccion_titulo("Datos de Contacto", ft.Icons.LOCATION_ON_OUTLINED),
                campo_ro("Dirección Domiciliaria", datos.get("dir_domiciliaria"), ft.Icons.HOME_OUTLINED, width=W_FULL),
                campo_ro("Dirección de Emergencia", datos.get("dir_emergencia"), ft.Icons.LOCAL_HOSPITAL_OUTLINED, width=W_FULL),

                seccion_titulo("Observaciones", ft.Icons.NOTES),
                campo_ro("Observaciones", datos.get("observaciones"), ft.Icons.NOTES, width=W_FULL),

                ft.Divider(color=tc["divider"]),
                btn_editar,
                btn_volver,
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
            ),
        )

        self._card_wrapper = ft.Container(
            content=card,
            opacity=0,
            offset=ft.Offset(0, 0.15),
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN),
            animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
        )
        self.content = self._card_wrapper

    def _obtener_estado(self):
        return obtener_estado(self.datos.get("fecha_hasta", ""))

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
