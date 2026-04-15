import flet as ft
from core.theme import theme_colors


class ChartContainer(ft.Container):
    def __init__(self, title="", dark_mode=True, width=None, height=None):
        super().__init__()
        self.dark_mode = dark_mode
        
        tc = theme_colors(dark_mode)
        
        self.bgcolor = tc["bg_card"]
        self.border_radius = 14
        self.border = ft.border.all(1, tc["table_border"])
        self.padding = ft.padding.all(16)
        self.width = width
        self.height = height
        
        self.title = title
        self._build_header(tc)
    
    def _build_header(self, tc):
        if self.title:
            self.header = ft.Row([
                ft.Text(self.title, size=16, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Container(expand=True),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        else:
            self.header = None
    
    def set_content(self, content):
        if self.header:
            self.content = ft.Column([self.header, ft.Container(height=12), content], spacing=0)
        else:
            self.content = content


class BarChart(ChartContainer):
    def __init__(self, title="", data=None, dark_mode=True, width=None, height=250):
        super().__init__(title=title, dark_mode=dark_mode, width=width, height=height)
        
        self.data = data or []
        self._build_chart()
    
    def _build_chart(self):
        tc = theme_colors(self.dark_mode)
        
        bars = []
        max_value = max([d.get("value", 0) for d in self.data], default=1)
        
        for item in self.data:
            label = item.get("label", "")
            value = item.get("value", 0)
            color = item.get("color", ft.Colors.GREEN_400)
            
            bar_height = max(20, int((value / max_value * 100)) ) if max_value > 0 else 20
            
            bar_column = ft.Column([
                ft.Container(
                    width=45,
                    height=bar_height,
                    bgcolor=color,
                    border_radius=ft.border_radius.vertical(top=6),
                ),
                ft.Container(height=4),
                ft.Text(label, size=10, color=tc["text_secondary"], text_align=ft.TextAlign.CENTER, width=50),
                ft.Text(str(value), size=11, color=tc["text_primary"], weight=ft.FontWeight.BOLD),
            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            bars.append(bar_column)
        
        chart = ft.Row(bars, spacing=16, alignment=ft.MainAxisAlignment.CENTER, expand=True)
        
        self.set_content(chart)


class DonutChart(ChartContainer):
    def __init__(self, title="", data=None, center_text="", dark_mode=True, width=None, height=250):
        super().__init__(title=title, dark_mode=dark_mode, width=width, height=height)
        
        self.data = data or []
        self.center_text = center_text
        self._build_chart()
    
    def _build_chart(self):
        tc = theme_colors(self.dark_mode)
        
        total = sum([d.get("value", 0) for d in self.data])
        
        progress_bars = []
        
        for item in self.data:
            label = item.get("label", "")
            value = item.get("value", 0)
            color = item.get("color", ft.Colors.GREEN_400)
            
            percentage = (value / total * 100) if total > 0 else 0
            
            progress_bars.append(
                ft.Column([
                    ft.Row([
                        ft.Container(width=10, height=10, bgcolor=color, border_radius=2),
                        ft.Text(label, size=12, color=tc["text_primary"], expand=True),
                        ft.Text(f"{value} ({percentage:.0f}%)", size=11, color=tc["text_secondary"]),
                    ], spacing=8),
                    ft.Container(height=6),
                    ft.Container(
                        content=ft.Container(
                            width=percentage * 2,
                            bgcolor=color,
                            border_radius=3,
                        ),
                        height=8,
                        bgcolor=tc["input_bg"],
                        border_radius=4,
                    ),
                    ft.Container(height=12),
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.START)
            )
        
        center_display = ft.Container(
            content=ft.Column([
                ft.Text(str(total), size=32, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Text("Total", size=12, color=tc["text_secondary"]),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            alignment=ft.Alignment(0, 0),
            padding=20,
            bgcolor=tc["input_bg"],
            border_radius=50,
            width=100,
            height=100,
        )
        
        content = ft.Column([
            ft.Row([
                center_display,
                ft.Container(width=20),
                ft.Column(progress_bars, expand=True),
            ], alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=0)
        
        self.set_content(content)


class PieChart(DonutChart):
    """PieChart usa la misma implementación que DonutChart"""
    pass


class ProgressChart(ChartContainer):
    def __init__(self, title="", data=None, dark_mode=True, width=None, height=250):
        super().__init__(title=title, dark_mode=dark_mode, width=width, height=height)
        
        self.data = data or []
        self._build_chart()
    
    def _build_chart(self):
        tc = theme_colors(self.dark_mode)
        
        progress_rows = []
        
        for item in self.data:
            label = item.get("label", "")
            value = item.get("value", 0)
            color = item.get("color", ft.Colors.GREEN_400)
            
            progress_rows.append(
                ft.Column([
                    ft.Row([
                        ft.Text(label, size=13, color=tc["text_primary"], expand=True),
                        ft.Text(str(value), size=13, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                    ], spacing=8),
                    ft.Container(height=6),
                    ft.Container(
                        content=ft.Container(
                            width=value * 3,
                            bgcolor=color,
                            border_radius=3,
                        ),
                        height=10,
                        bgcolor=tc["input_bg"],
                        border_radius=5,
                    ),
                    ft.Container(height=12),
                ], spacing=2)
            )
        
        self.set_content(ft.Column(progress_rows, spacing=0))


class StatsCard(ft.Container):
    def __init__(self, title="", value="", icon=ft.Icons.INFO, color=ft.Colors.GREEN_400, 
                 subtitle="", dark_mode=True, on_click=None):
        super().__init__()
        self.dark_mode = dark_mode
        
        tc = theme_colors(dark_mode)
        
        self.bgcolor = tc["bg_card"]
        self.border_radius = 14
        self.border = ft.border.all(1, tc["stat_border"])
        self.padding = ft.padding.symmetric(vertical=16, horizontal=20)
        
        self.content = ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(icon, color=color, size=22),
                    bgcolor=tc["icon_bg"],
                    border_radius=10,
                    padding=10,
                ),
                ft.Container(expand=True),
            ]),
            ft.Container(height=12),
            ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
            ft.Text(title, size=12, color=tc["text_secondary"]),
            ft.Container(height=4),
            ft.Text(subtitle, size=11, color=tc["text_tertiary"]) if subtitle else ft.Container(),
        ], spacing=0)
        
        if on_click:
            self.on_click = on_click
            self.ink = True


class MiniStatsRow(ft.Container):
    def __init__(self, items=None, dark_mode=True, spacing=16):
        super().__init__()
        self.dark_mode = dark_mode
        
        tc = theme_colors(dark_mode)
        
        cards = []
        for item in (items or []):
            label = item.get("label", "")
            value = item.get("value", "0")
            icon = item.get("icon", ft.Icons.INFO)
            color = item.get("color", ft.Colors.GREEN_400)
            
            card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, color=color, size=18),
                        ft.Container(expand=True),
                    ]),
                    ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                    ft.Text(label, size=11, color=tc["text_secondary"]),
                ], spacing=2),
                bgcolor=tc["bg_card"],
                border_radius=12,
                border=ft.border.all(1, tc["stat_border"]),
                padding=ft.padding.symmetric(vertical=14, horizontal=16),
                expand=True,
            )
            cards.append(card)
        
        self.content = ft.Row(cards, spacing=spacing)


def create_bar_chart_from_dict(data_dict, title="", dark_mode=True):
    """Crea un gráfico de barras desde un diccionario {label: value}"""
    data = [
        {"label": label, "value": value, "color": ft.Colors.GREEN_400}
        for label, value in data_dict.items()
    ]
    return BarChart(title=title, data=data, dark_mode=dark_mode)


def create_donut_chart_from_dict(data_dict, title="", dark_mode=True):
    """Crea un gráfico donut desde un diccionario {label: value}"""
    colors = [ft.Colors.GREEN_400, ft.Colors.BLUE_400, ft.Colors.ORANGE_400, 
              ft.Colors.RED_400, ft.Colors.PURPLE_400, ft.Colors.CYAN_400]
    
    data = [
        {"label": label, "value": value, "color": colors[i % len(colors)]}
        for i, (label, value) in enumerate(data_dict.items())
    ]
    total = sum(data_dict.values())
    return DonutChart(title=title, data=data, center_text=str(total), dark_mode=dark_mode)


def create_progress_chart_from_dict(data_dict, title="", dark_mode=True):
    """Crea un gráfico de progreso desde un diccionario {label: value}"""
    colors = [ft.Colors.GREEN_400, ft.Colors.BLUE_400, ft.Colors.ORANGE_400, 
              ft.Colors.RED_400, ft.Colors.PURPLE_400, ft.Colors.CYAN_400]
    
    data = [
        {"label": label, "value": value, "color": colors[i % len(colors)]}
        for i, (label, value) in enumerate(data_dict.items())
    ]
    return ProgressChart(title=title, data=data, dark_mode=dark_mode)


def create_stats_cards_from_dict(stats_dict, dark_mode=True):
    """Crea una fila de tarjetas de estadísticas desde un diccionario {label: value}"""
    icons = [ft.Icons.PEOPLE, ft.Icons.EVENT_NOTE, ft.Icons.BUSINESS_CENTER, 
             ft.Icons.WARNING, ft.Icons.CHECK_CIRCLE, ft.Icons.SCHEDULE]
    colors = [ft.Colors.GREEN_400, ft.Colors.CYAN_400, ft.Colors.ORANGE_400,
              ft.Colors.RED_400, ft.Colors.BLUE_400, ft.Colors.AMBER_400]
    
    items = []
    for i, (label, value) in enumerate(stats_dict.items()):
        items.append({
            "label": label,
            "value": str(value),
            "icon": icons[i % len(icons)],
            "color": colors[i % len(colors)],
        })
    
    return MiniStatsRow(items=items, dark_mode=dark_mode)