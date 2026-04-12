import flet as ft
from core.theme import theme_colors


class LoadingIndicator(ft.Container):
    def __init__(self, message="Cargando...", size=20, dark_mode=True):
        tc = theme_colors(dark_mode)
        super().__init__(
            content=ft.Column([
                ft.ProgressRing(
                    width=size,
                    height=size,
                    stroke_width=2,
                    color=ft.Colors.GREEN_400
                ),
                ft.Container(height=8),
                ft.Text(
                    message,
                    size=14,
                    color=tc["text_secondary"],
                    weight=ft.FontWeight.W_500
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0
            ),
            padding=ft.padding.all(24),
            bgcolor=tc["bg_dialog"],
            border_radius=12,
            border=ft.border.all(1, tc["border_primary"])
        )


class SkeletonLoader(ft.Container):
    """Placeholder skeleton para listas y tarjetas"""
    def __init__(self, width, height, dark_mode=True, radius=8):
        tc = theme_colors(dark_mode)
        super().__init__(
            width=width,
            height=height,
            bgcolor=tc["input_bg"],
            border_radius=radius,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
        )
        
    def start_loading(self):
        self.opacity = 0.7
        self.update()
        
    def stop_loading(self):
        self.opacity = 1.0
        self.update()