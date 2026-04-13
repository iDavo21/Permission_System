import flet as ft
from core.theme import theme_colors


class Sidebar(ft.Container):
    def __init__(self, active_section="inicio", on_navigate=None, on_logout=None, on_toggle_theme=None, dark_mode=True):
        super().__init__()
        self.active_section = active_section
        self.on_navigate = on_navigate or (lambda x: None)
        self.on_logout = on_logout or (lambda: None)
        self.on_toggle_theme = on_toggle_theme or (lambda: None)
        self.dark_mode = dark_mode
        self._item_buttons = {}
        self._build_ui()

    def _build_ui(self):
        tc = theme_colors(self.dark_mode)
        
        self._build_item_button("inicio", ft.Icons.HOME, "Inicio", tc)
        self._build_item_button("personal", ft.Icons.PEOPLE, "Personal", tc)
        self._build_item_button("permisos", ft.Icons.EVENT_NOTE, "Permisos", tc)
        self._build_item_button("comisiones", ft.Icons.BUSINESS_CENTER, "Comisiones", tc)
        self._build_item_button("situaciones", ft.Icons.WARNING_AMBER_ROUNDED, "Situaciones", tc)

        self.theme_toggle = ft.Container(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.DARK_MODE if self.dark_mode else ft.Icons.LIGHT_MODE,
                    color=tc["sidebar_icon"],
                    size=20,
                ),
                ft.Text(
                    "Tema",
                    color=tc["sidebar_text"],
                    size=13,
                ),
            ], spacing=10),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border_radius=10,
            ink=True,
            on_click=lambda e: self.on_toggle_theme(),
        )

        self.logout_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.RED_300, size=20),
                ft.Text("Cerrar Sesión", color=ft.Colors.RED_300, size=13),
            ], spacing=10),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border_radius=10,
            ink=True,
            on_click=lambda e: self.on_logout(),
        )

        self.config_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SETTINGS, color=tc["sidebar_icon"], size=20),
                ft.Text("Configuración", color=tc["sidebar_text"], size=13),
            ], spacing=10),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border_radius=10,
            ink=True,
            on_click=lambda e: self._on_config_click(),
        )


        self.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.Icons.MILITARY_TECH, color=ft.Colors.GREEN_400, size=32),
                            bgcolor=tc["icon_bg"],
                            border_radius=12,
                            padding=12,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=8),
                        ft.Text("Control de", size=12, color=tc["sidebar_text"], weight=ft.FontWeight.W_400),
                        ft.Text("Personal", size=18, color=tc["sidebar_text"], weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(vertical=20),
                ),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Column([
                        self._item_buttons["inicio"],
                        self._item_buttons["personal"],
                        self._item_buttons["permisos"],
                        self._item_buttons["comisiones"],
                        self._item_buttons["situaciones"],
                    ], spacing=4),
                    padding=ft.padding.symmetric(horizontal=12),
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Column([
                        ft.Divider(color=tc["sidebar_divider"], height=1),
                        ft.Container(height=8),
                        ft.Text("SISTEMA", size=11, weight=ft.FontWeight.W_500, color=tc["text_tertiary"]),
                        ft.Container(height=4),
                        self.config_btn,
                        self.theme_toggle,
                        ft.Container(height=4),
                        self.logout_btn,
                        ft.Container(height=16),
                    ], spacing=2),
                    padding=ft.padding.symmetric(horizontal=12),
                ),
            ],
            expand=True,
        )

        self.width = 220
        self.bgcolor = tc["sidebar_bg"]
        self.border = ft.border.only(right=ft.border.BorderSide(1, tc["sidebar_border"]))

    def _build_item_button(self, section, icon, label, tc):
        is_active = self.active_section == section
        
        btn = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(
                        icon,
                        color=ft.Colors.WHITE if is_active else tc["sidebar_icon"],
                        size=18,
                    ),
                    bgcolor=ft.Colors.GREEN_700 if is_active else "transparent",
                    border_radius=8,
                    padding=ft.padding.all(6),
                    width=32,
                    height=32,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Text(
                    label,
                    color=ft.Colors.WHITE if is_active else tc["sidebar_text"],
                    size=14,
                    weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.W_500,
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.KEYBOARD_ARROW_RIGHT,
                        color=ft.Colors.GREEN_400,
                        size=16,
                    ),
                    visible=is_active,
                ),
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            border_radius=10,
            bgcolor=tc["sidebar_item_active_bg"] if is_active else "transparent",
            border=ft.border.only(
                left=ft.border.BorderSide(3, ft.Colors.GREEN_400) if is_active else ft.border.BorderSide(0, "transparent")
            ),
            ink=True,
            on_click=lambda e, s=section: self._on_item_click(s),
        )
        
        if not is_active:
            btn.on_hover = lambda e, b=btn: self._on_item_hover(e, b, tc)
        
        self._item_buttons[section] = btn
        return btn

    def _on_item_hover(self, e, btn, tc):
        if e.data == "true":
            btn.bgcolor = tc["sidebar_item_hover"]
        else:
            btn.bgcolor = "transparent"
        btn.update()

    def _on_item_click(self, section):
        if section != self.active_section:
            self.active_section = section
            self.on_navigate(section)

    def _on_config_click(self):
        self.on_navigate("configuracion")


    def update_active(self, section, dark_mode=None):
        if dark_mode is not None:
            self.dark_mode = dark_mode
        self.active_section = section
        self._rebuild_items()

    def _rebuild_items(self):
        tc = theme_colors(self.dark_mode)
        for key, btn in self._item_buttons.items():
            is_active = self.active_section == key
            
            icon_container = btn.content.controls[0]
            icon_container.content.color = ft.Colors.WHITE if is_active else tc["sidebar_icon"]
            icon_container.bgcolor = ft.Colors.GREEN_700 if is_active else "transparent"
            
            text = btn.content.controls[1]
            text.color = ft.Colors.WHITE if is_active else tc["sidebar_text"]
            text.weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.W_500
            
            indicator = btn.content.controls[3]
            indicator.visible = is_active
            
            btn.bgcolor = tc["sidebar_item_active_bg"] if is_active else "transparent"
            btn.border = ft.border.only(
                left=ft.border.BorderSide(3, ft.Colors.GREEN_400) if is_active else ft.border.BorderSide(0, "transparent")
            )
            
            if not is_active:
                btn.on_hover = lambda e, b=btn: self._on_item_hover(e, b, tc)
            else:
                btn.on_hover = None
        try:
            if self.page:
                self.update()
        except RuntimeError:
            pass

    def rebuild(self, dark_mode=None):
        if dark_mode is not None:
            self.dark_mode = dark_mode
        self._build_ui()