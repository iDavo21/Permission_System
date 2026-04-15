import flet as ft
from core.theme import theme_colors


class ErrorBanner(ft.Container):
    def __init__(self, message, on_close=None, banner_type="error", dark_mode=True, duration=5000):
        super().__init__()
        self.dark_mode = dark_mode
        self.on_close_callback = on_close
        self.duration = duration
        
        tc = theme_colors(dark_mode)
        
        colors = {
            "error": {"bg": "#7f1d1d", "icon": ft.Colors.RED_300},
            "warning": {"bg": "#78350f", "icon": ft.Colors.AMBER_300},
            "success": {"bg": "#14532d", "icon": ft.Colors.GREEN_300},
            "info": {"bg": "#1e3a5f", "icon": ft.Colors.BLUE_300},
        }
        
        color_scheme = colors.get(banner_type, colors["error"])
        
        self.bgcolor = color_scheme["bg"]
        self.border_radius = 8
        self.padding = ft.padding.symmetric(horizontal=16, vertical=12)
        self.margin = ft.margin.only(bottom=8)
        self.animate_opacity = ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT)
        
        self.content = ft.Row(
            controls=[
                ft.Icon(ft.Icons.ERROR_OUTLINE if banner_type == "error" else 
                       ft.Icons.WARNING_AMBER_ROUNDED if banner_type == "warning" else
                       ft.Icons.CHECK_CIRCLE_OUTLINE if banner_type == "success" else
                       ft.Icons.INFO_OUTLINE,
                       color=color_scheme["icon"], size=20),
                ft.Container(width=12),
                ft.Text(message, size=13, color=ft.Colors.WHITE, expand=True),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=ft.Colors.WHITE70,
                    icon_size=18,
                    on_click=lambda e: self._cerrar(),
                ),
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        if self.duration > 0:
            self._auto_dismiss()
    
    def _cerrar(self):
        self.opacity = 0
        try:
            self.update()
        except RuntimeError:
            pass
        if self.on_close_callback:
            self.on_close_callback()
    
    def _auto_dismiss(self):
        import asyncio
        async def wait_and_close():
            await asyncio.sleep(self.duration / 1000)
            try:
                self._cerrar()
            except RuntimeError:
                pass
        asyncio.create_task(wait_and_close())


class ErrorDialog(ft.AlertDialog):
    def __init__(self, title="Error", message="Ha ocurrido un error", 
                 on_retry=None, on_accept=None, dark_mode=True,
                 show_retry=True, show_accept=True):
        
        tc = theme_colors(dark_mode)
        
        actions = []
        if show_retry and on_retry:
            actions.append(ft.TextButton("Reintentar", on_click=on_retry))
        if show_accept and on_accept:
            actions.append(ft.ElevatedButton("Aceptar", on_click=on_accept))
        
        if not actions:
            actions.append(ft.ElevatedButton("Aceptar", on_click=lambda e: None))
        
        super().__init__(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED_400, size=24),
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            content=ft.Column([
                ft.Text(message, size=14, color=tc["text_secondary"]),
            ], spacing=8),
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END,
        )


class ConfirmDialog(ft.AlertDialog):
    def __init__(self, title="Confirmar", message="¿Está seguro?", 
                 on_confirm=None, on_cancel=None, dark_mode=True,
                 confirm_text="Confirmar", cancel_text="Cancelar",
                 confirm_color=ft.Colors.GREEN_700):
        
        super().__init__(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.HELP_OUTLINE, color=ft.Colors.AMBER_400, size=24),
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            content=ft.Text(message, size=14),
            actions=[
                ft.TextButton(cancel_text, on_click=on_cancel),
                ft.ElevatedButton(
                    confirm_text, 
                    bgcolor=confirm_color,
                    color=ft.Colors.WHITE,
                    on_click=on_confirm
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )


class LoadingOverlay(ft.Container):
    def __init__(self, message="Cargando...", dark_mode=True, show_cancel=False, on_cancel=None):
        super().__init__()
        self.dark_mode = dark_mode
        
        tc = theme_colors(dark_mode)
        
        self.bgcolor = ft.Colors.with_opacity(0.7, ft.Colors.BLACK) if dark_mode else ft.Colors.with_opacity(0.5, ft.Colors.WHITE)
        self.expand = True
        
        content_controls = [
            ft.Column([
                ft.ProgressRing(width=40, height=40, stroke_width=3, color=ft.Colors.GREEN_400),
                ft.Container(height=16),
                ft.Text(message, size=14, color=ft.Colors.WHITE if dark_mode else ft.Colors.GREY_800),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)
        ]
        
        if show_cancel and on_cancel:
            content_controls.append(
                ft.Container(
                    content=ft.TextButton("Cancelar", on_click=on_cancel, style=ft.ButtonStyle(color=ft.Colors.WHITE70)),
                    margin=ft.margin.only(top=16)
                )
            )
        
        self.content = ft.Column(content_controls, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)
        self.alignment = ft.Alignment(0, 0)


def show_error_banner(page, message, duration=5000, banner_type="error"):
    """Función auxiliar para mostrar un banner de error en la página."""
    banner = ErrorBanner(message=message, banner_type=banner_type, duration=duration, dark_mode=True)
    
    if not hasattr(page, '_error_banners'):
        page._error_banners = []
    
    page._error_banners.append(banner)
    
    container = ft.Container(
        content=ft.Column([banner], spacing=0),
        expand=False,
        margin=ft.margin.only(left=24, right=24, top=8)
    )
    
    page.controls.insert(1, container)
    try:
        page.update()
    except RuntimeError:
        pass
    
    return banner


def show_toast(page, message, toast_type="success", duration=3000):
    """Función auxiliar para mostrar un toast en la página."""
    colors = {
        "success": {"bg": "#166534", "icon": ft.Icons.CHECK_CIRCLE},
        "error": {"bg": "#991b1b", "icon": ft.Icons.ERROR},
        "warning": {"bg": "#92400e", "icon": ft.Icons.WARNING},
        "info": {"bg": "#1e40af", "icon": ft.Icons.INFO},
    }
    
    color_scheme = colors.get(toast_type, colors["success"])
    
    toast = ft.Container(
        content=ft.Row([
            ft.Icon(color_scheme["icon"], color=ft.Colors.WHITE, size=20),
            ft.Container(width=8),
            ft.Text(message, color=ft.Colors.WHITE, size=13, expand=True),
        ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=color_scheme["bg"],
        border_radius=8,
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        margin=ft.margin.only(bottom=8),
        animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
    )
    
    snack = ft.SnackBar(
        content=toast,
        duration=duration,
        behavior=ft.SnackBarBehavior.FLOATING,
    )
    
    page.show_snack_bar(snack)


def show_error_dialog(page, title="Error", message="Ha ocurrido un error", on_accept=None):
    """Función auxiliar para mostrar un diálogo de error."""
    dlg = ErrorDialog(
        title=title,
        message=message,
        on_accept=lambda e: (page.pop_dialog() if on_accept is None else on_accept(e))
    )
    page.show_dialog(dlg)


def show_confirm_dialog(page, title="Confirmar", message="¿Está seguro?", 
                       on_confirm=None, on_cancel=None, confirm_text="Confirmar"):
    """Función auxiliar para mostrar un diálogo de confirmación."""
    def handle_confirm(e):
        page.pop_dialog()
        if on_confirm:
            on_confirm(e)
    
    def handle_cancel(e):
        page.pop_dialog()
        if on_cancel:
            on_cancel(e)
    
    dlg = ConfirmDialog(
        title=title,
        message=message,
        on_confirm=handle_confirm,
        on_cancel=handle_cancel,
        confirm_text=confirm_text
    )
    page.show_dialog(dlg)