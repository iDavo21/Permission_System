import flet as ft


def create_shortcuts_help_dialog(dark_mode=True, on_close=None):
    tc = {
        "bg": "#252525" if dark_mode else "#FFFFFF",
        "title": "#FFFFFF" if dark_mode else "#000000",
        "text": "#E0E0E0" if dark_mode else "#333333",
        "secondary": "#9E9E9E" if dark_mode else "#666666",
        "border": "#424242" if dark_mode else "#E0E0E0",
    }

    def crear_fila(atajo, descripcion, color):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(
                        atajo,
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=color,
                    ),
                    width=80,
                ),
                ft.Text(descripcion, size=12, color=tc["text"]),
            ], spacing=10),
            padding=ft.padding.symmetric(vertical=4),
        )

    secciones = [
        ("Navegación", ft.Colors.GREEN_400, [
            ("Ctrl+1", "Ir a Personal"),
            ("Ctrl+2", "Ir a Permisos"),
            ("Ctrl+3", "Ir a Comisiones"),
        ]),
        ("Acciones Globales", ft.Colors.AMBER_400, [
            ("F1", "Cambiar tema (Dark/Light)"),
            ("Ctrl+B", "Crear backup"),
            ("Ctrl+H", "Ver atajos (este menú)"),
            ("Escape", "Cerrar diálogo"),
        ]),
        ("Acciones en Dashboards", ft.Colors.CYAN_400, [
            ("Ctrl+N", "Nuevo registro"),
            ("Ctrl+E", "Editar registro"),
            ("Ctrl+D", "Eliminar registro"),
            ("Ctrl+F", "Enfocar búsqueda"),
        ]),
        ("En Formularios", ft.Colors.PURPLE_400, [
            ("Ctrl+S", "Guardar registro"),
            ("Enter", "Confirmar acción"),
            ("Escape", "Cancelar/Volver"),
        ]),
    ]

    contenido = ft.Column(spacing=12)
    for seccion, color, atajos in secciones:
        contenido.controls.append(
            ft.Text(seccion, size=13, weight=ft.FontWeight.BOLD, color=tc["secondary"])
        )
        for atajo, desc in atajos:
            contenido.controls.append(crear_fila(atajo, desc, color))
        contenido.controls.append(ft.Divider(height=1, color=tc["border"]))

    return ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.KEYBOARD, color=ft.Colors.GREEN_400, size=22),
            ft.Text("Atajos de Teclado", color=tc["title"], weight=ft.FontWeight.BOLD),
        ], spacing=10),
        content=ft.Container(
            width=400,
            content=contenido,
        ),
        actions=[
            ft.TextButton(
                "Cerrar",
                on_click=on_close or (lambda e: None),
                style=ft.ButtonStyle(color=ft.Colors.GREEN_400),
            ),
        ],
        bgcolor=tc["bg"],
        shape=ft.RoundedRectangleBorder(radius=16),
    )


def show_shortcuts_help(page: ft.Page, dark_mode=True):
    def close(e):
        page.dialog.open = False
        page.update()

    page.dialog = create_shortcuts_help_dialog(dark_mode=dark_mode, on_close=close)
    page.dialog.open = True
    page.update()