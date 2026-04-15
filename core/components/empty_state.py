import flet as ft
from core.theme import theme_colors


class EmptyState(ft.Container):
    def __init__(self, icon=ft.Icons.INBOX, title="No hay datos", 
                 subtitle="Los datos aparecerán aquí", action=None, 
                 dark_mode=True, width=None, height=None):
        super().__init__()
        self.dark_mode = dark_mode
        
        tc = theme_colors(dark_mode)
        
        self.bgcolor = "transparent"
        self.width = width
        self.height = height
        
        icon_colors = {
            ft.Icons.INBOX: tc["empty_icon"],
            ft.Icons.SEARCH_OFF: tc["empty_icon"],
            ft.Icons.PEOPLE_OUTLINE: tc["empty_icon"],
            ft.Icons.EVENT_NOTE: tc["empty_icon"],
            ft.Icons.BUSINESS_CENTER: tc["empty_icon"],
            ft.Icons.WARNING: tc["empty_icon"],
        }
        
        icon_color = icon_colors.get(icon, tc["empty_icon"])
        
        controls = [
            ft.Container(
                content=ft.Icon(icon, size=64, color=icon_color),
                bgcolor=tc["empty_icon_bg"],
                border_radius=20,
                padding=24,
                alignment=ft.Alignment(0, 0),
            ),
            ft.Container(height=16),
            ft.Text(title, size=20, color=tc["empty_text"], weight=ft.FontWeight.BOLD),
            ft.Container(height=4),
            ft.Text(subtitle, size=14, color=tc["empty_subtext"]),
        ]
        
        if action:
            controls.append(ft.Container(height=16))
            controls.append(action)
        
        self.content = ft.Column(
            controls=controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            expand=True,
        )
        self.alignment = ft.Alignment(0, 0)


class EmptyTableState(EmptyState):
    """Estado vacío específico para tablas."""
    def __init__(self, dark_mode=True, on_refresh=None):
        action = None
        if on_refresh:
            action = ft.Container(
                content=ft.ElevatedButton(
                    "Actualizar",
                    icon=ft.Icons.REFRESH,
                    on_click=on_refresh,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.GREEN_700,
                        color=ft.Colors.WHITE,
                    )
                )
            )
        
        super().__init__(
            icon=ft.Icons.INBOX,
            title="No hay registros",
            subtitle="No se encontraron datos para mostrar",
            action=action,
            dark_mode=dark_mode
        )


class EmptySearchState(EmptyState):
    """Estado vacío para búsquedas sin resultados."""
    def __init__(self, search_term="", dark_mode=True, on_clear=None):
        action = None
        if on_clear:
            action = ft.Container(
                content=ft.TextButton(
                    "Limpiar búsqueda",
                    icon=ft.Icons.CLEAR,
                    on_click=on_clear
                )
            )
        
        super().__init__(
            icon=ft.Icons.SEARCH_OFF,
            title="Sin resultados",
            subtitle=f"No se encontró nada para '{search_term}'" if search_term else "Intenta con otros términos",
            action=action,
            dark_mode=dark_mode
        )


class EmptyListState(EmptyState):
    """Estado vacío genérico para listas."""
    def __init__(self, list_type="elementos", dark_mode=True, on_add=None):
        icon_map = {
            "personal": ft.Icons.PEOPLE_OUTLINE,
            "permisos": ft.Icons.EVENT_NOTE,
            "comisiones": ft.Icons.BUSINESS_CENTER,
            "situaciones": ft.Icons.WARNING,
            "elementos": ft.Icons.INBOX,
        }
        
        title_map = {
            "personal": "No hay personal registrado",
            "permisos": "No hay permisos registrados",
            "comisiones": "No hay comisiones registradas",
            "situaciones": "No hay situaciones registradas",
            "elementos": "No hay elementos",
        }
        
        subtitle_map = {
            "personal": "Registra nuevo personal para comenzar",
            "permisos": "Los permisos aparecerán aquí",
            "comisiones": "Las comisiones aparecerán aquí",
            "situaciones": "Las situaciones aparecerán aquí",
            "elementos": "Los elementos aparecerán aquí",
        }
        
        action = None
        if on_add:
            button_text = {
                "personal": "Agregar Personal",
                "permisos": "Agregar Permiso",
                "comisiones": "Agregar Comisión",
                "situaciones": "Agregar Situación",
                "elementos": "Agregar",
            }
            action = ft.Container(
                content=ft.ElevatedButton(
                    button_text.get(list_type, "Agregar"),
                    icon=ft.Icons.ADD,
                    on_click=on_add,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.GREEN_700,
                        color=ft.Colors.WHITE,
                    )
                )
            )
        
        super().__init__(
            icon=icon_map.get(list_type, ft.Icons.INBOX),
            title=title_map.get(list_type, "No hay elementos"),
            subtitle=subtitle_map.get(list_type, "Los elementos aparecerán aquí"),
            action=action,
            dark_mode=dark_mode
        )


class LoadingState(ft.Container):
    def __init__(self, message="Cargando...", dark_mode=True):
        super().__init__()
        self.dark_mode = dark_mode
        
        tc = theme_colors(dark_mode)
        
        self.content = ft.Column([
            ft.ProgressRing(width=40, height=40, stroke_width=3, color=ft.Colors.GREEN_400),
            ft.Container(height=16),
            ft.Text(message, size=14, color=tc["text_secondary"]),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)
        
        self.alignment = ft.Alignment(0, 0)
        self.expand = True


def get_empty_state(state_type, dark_mode=True, **kwargs):
    """Factory function para obtener el estado vacío apropiado."""
    states = {
        "table": EmptyTableState,
        "search": EmptySearchState,
        "list": EmptyListState,
        "loading": LoadingState,
    }
    
    state_class = states.get(state_type, EmptyState)
    
    if state_type == "search":
        return state_class(search_term=kwargs.get("search_term", ""), dark_mode=dark_mode, on_clear=kwargs.get("on_clear"))
    elif state_type == "list":
        return state_class(list_type=kwargs.get("list_type", "elementos"), dark_mode=dark_mode, on_add=kwargs.get("on_add"))
    elif state_type == "table":
        return state_class(dark_mode=dark_mode, on_refresh=kwargs.get("on_refresh"))
    elif state_type == "loading":
        return state_class(message=kwargs.get("message", "Cargando..."), dark_mode=dark_mode)
    else:
        return state_class(dark_mode=dark_mode)