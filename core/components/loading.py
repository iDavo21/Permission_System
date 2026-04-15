import flet as ft
import asyncio
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


class LoadingOverlay(ft.Container):
    def __init__(self, message="Cargando...", dark_mode=True, show_cancel=False, on_cancel=None):
        super().__init__()
        self.dark_mode = dark_mode
        self.on_cancel_callback = on_cancel
        self.visible = False
        self.opacity = 0
        
        tc = theme_colors(dark_mode)
        
        self.bgcolor = ft.Colors.with_opacity(0.7, ft.Colors.BLACK) if dark_mode else ft.Colors.with_opacity(0.5, ft.Colors.WHITE)
        self.expand = True
        
        controls = [
            ft.Column([
                ft.ProgressRing(width=40, height=40, stroke_width=3, color=ft.Colors.GREEN_400),
                ft.Container(height=16),
                ft.Text(message, size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)
        ]
        
        if show_cancel and on_cancel:
            controls.append(
                ft.Container(
                    content=ft.TextButton(
                        "Cancelar", 
                        on_click=lambda e: self._handle_cancel(),
                        style=ft.ButtonStyle(color=ft.Colors.WHITE70)
                    ),
                    margin=ft.margin.only(top=16)
                )
            )
        
        self.content = ft.Column(controls, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)
        self.alignment = ft.Alignment(0, 0)
        self.animate_opacity = ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT)
    
    def _handle_cancel(self):
        if self.on_cancel_callback:
            self.on_cancel_callback()
        self.hide()
    
    def show(self, message=None):
        if message:
            self.content.controls[0].controls[2].value = message
        self.visible = True
        self.opacity = 1
        try:
            self.update()
        except RuntimeError:
            pass
    
    def hide(self):
        self.visible = False
        self.opacity = 0
        try:
            self.update()
        except RuntimeError:
            pass


class SkeletonLoader(ft.Container):
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
        try:
            self.update()
        except RuntimeError:
            pass
        
    def stop_loading(self):
        self.opacity = 1.0
        try:
            self.update()
        except RuntimeError:
            pass


class SkeletonList(ft.Container):
    def __init__(self, item_height=52, item_count=5, dark_mode=True, spacing=8):
        super().__init__()
        self.dark_mode = dark_mode
        
        tc = theme_colors(dark_mode)
        
        items = []
        for _ in range(item_count):
            items.append(
                ft.Container(
                    width=float("inf"),
                    height=item_height,
                    bgcolor=tc["input_bg"],
                    border_radius=8,
                    margin=ft.margin.only(bottom=spacing if spacing else 0),
                )
            )
        
        self.content = ft.Column(items, spacing=spacing)
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO


class SkeletonCard(ft.Container):
    def __init__(self, width=200, height=120, dark_mode=True):
        super().__init__()
        self.dark_mode = dark_mode
        
        tc = theme_colors(dark_mode)
        
        self.content = ft.Column([
            ft.Container(
                width=float("inf"),
                height=60,
                bgcolor=tc["input_bg"],
                border_radius=8,
            ),
            ft.Container(height=8),
            ft.Container(
                width=100,
                height=14,
                bgcolor=tc["input_bg"],
                border_radius=4,
            ),
            ft.Container(height=4),
            ft.Container(
                width=60,
                height=12,
                bgcolor=tc["input_bg"],
                border_radius=4,
            ),
        ], spacing=0)
        
        self.width = width
        self.height = height


def create_loading_overlay(page, message="Cargando...", show_cancel=False, on_cancel=None):
    """Factory function para crear un overlay de carga en la página."""
    overlay = LoadingOverlay(message=message, dark_mode=True, show_cancel=show_cancel, on_cancel=on_cancel)
    overlay.visible = False
    overlay.opacity = 0
    
    container = ft.Container(
        content=overlay,
        expand=True,
        alignment=ft.Alignment(0, 0),
    )
    
    page.controls.insert(0, container)
    
    def show(message_override=None):
        overlay.show(message_override)
    
    def hide():
        overlay.hide()
    
    return {
        "container": container,
        "show": show,
        "hide": hide,
    }
        
    def stop_loading(self):
        self.opacity = 1.0
        try:
            self.update()
        except RuntimeError:
            pass