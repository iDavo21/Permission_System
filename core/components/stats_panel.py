import flet as ft
from core.theme import theme_colors


class StatsPanel(ft.Container):
    def __init__(self, cards_config=None, dark_mode=True, spacing=16, margin=None):
        super().__init__()
        self.dark_mode = dark_mode
        self.cards_config = cards_config or []
        
        tc = theme_colors(self.dark_mode)
        self.bgcolor = "transparent"
        self.margin = margin or ft.margin.only(left=24, right=24)
        
        self._cards = {}
        self._build_ui(tc, spacing)
    
    def _build_ui(self, tc, spacing):
        self.content = ft.Row(
            [self._create_card(config, tc) for config in self.cards_config],
            spacing=spacing
        )
    
    def _create_card(self, config, tc):
        icon = config.get("icon", ft.Icons.INFO)
        value = config.get("value", "0")
        label = config.get("label", "")
        accent = config.get("accent", ft.Colors.BLUE_400)
        
        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=20, color=accent),
                    ft.Container(expand=True),
                ]),
                ft.Text(value, size=26, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Text(label, size=11, color=tc["text_secondary"]),
            ], spacing=4),
            bgcolor=tc["stat_bg"],
            border_radius=14,
            padding=ft.padding.symmetric(vertical=20, horizontal=22),
            expand=True,
            border=ft.border.all(1, tc["stat_border"]),
        )
        
        key = config.get("key", label)
        self._cards[key] = card
        return card
    
    def actualizar(self, valores):
        tc = theme_colors(self.dark_mode)
        
        for key, value in valores.items():
            if key in self._cards:
                card = self._cards[key]
                card.content.controls[1].value = str(value)
                try:
                    card.content.update()
                except RuntimeError:
                    pass
        
        self._actualizar_visible()
    
    def _actualizar_visible(self):
        total_values = sum(
            int(card.content.controls[1].value) 
            for card in self._cards.values()
        )
        self.visible = total_values > 0
        try:
            self.update()
        except RuntimeError:
            pass
    
    def set_visible(self, visible):
        self.visible = visible
        try:
            self.update()
        except RuntimeError:
            pass
    
    def rebuild(self, dark_mode):
        self.dark_mode = dark_mode
        tc = theme_colors(dark_mode)
        
        for key, card in self._cards.items():
            card.bgcolor = tc["stat_bg"]
            card.border = ft.border.all(1, tc["stat_border"])
            card.content.controls[1].color = tc["text_primary"]
            card.content.controls[2].color = tc["text_secondary"]
        
        self.update()


class StatCard(ft.Container):
    def __init__(self, icon, value, label, accent, dark_mode=True):
        super().__init__()
        self.dark_mode = dark_mode
        
        tc = theme_colors(dark_mode)
        self.content = ft.Column([
            ft.Row([
                ft.Icon(icon, size=20, color=accent),
                ft.Container(expand=True),
            ]),
            ft.Text(value, size=26, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
            ft.Text(label, size=11, color=tc["text_secondary"]),
        ], spacing=4)
        self.bgcolor = tc["stat_bg"]
        self.border_radius = 14
        self.padding = ft.padding.symmetric(vertical=20, horizontal=22)
        self.expand = True
        self.border = ft.border.all(1, tc["stat_border"])
    
    def set_value(self, value):
        self.content.controls[1].value = str(value)
        try:
            self.content.update()
        except RuntimeError:
            pass
    
    def rebuild(self, dark_mode):
        self.dark_mode = dark_mode
        tc = theme_colors(dark_mode)
        self.bgcolor = tc["stat_bg"]
        self.border = ft.border.all(1, tc["stat_border"])
        self.content.controls[1].color = tc["text_primary"]
        self.content.controls[2].color = tc["text_secondary"]
        try:
            self.update()
        except RuntimeError:
            pass