import flet as ft
from core.theme import theme_colors


def build_personal_summary_labels(personal_list, dark_mode=True):
    tc = {
        "text_primary": ft.Colors.WHITE if dark_mode else ft.Colors.BLACK87,
        "text_secondary": ft.Colors.GREY_400 if dark_mode else ft.Colors.GREY_600,
        "text_tertiary": ft.Colors.GREY_500 if dark_mode else ft.Colors.GREY_500,
    }
    
    labels = {
        "lbl_persona_resumen": ft.Text("Sin persona seleccionada", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400),
        "lbl_persona_detalle": ft.Text("Haga click en 'Seleccionar Personal'", size=13, color=tc["text_secondary"]),
        "lbl_persona_extras": ft.Text("", size=13, color=tc["text_tertiary"], visible=False),
    }
    
    def actualizar():
        cantidad = len(personal_list)
        if cantidad == 0:
            labels["lbl_persona_resumen"].value = "Sin persona seleccionada"
            labels["lbl_persona_detalle"].value = "Haga click en 'Seleccionar Personal'"
            labels["lbl_persona_extras"].visible = False
        elif cantidad == 1:
            p = personal_list[0]
            labels["lbl_persona_resumen"].value = f"{p.get('nombres', '')} {p.get('apellidos', '')}".strip()
            labels["lbl_persona_detalle"].value = f"C.I.: {p.get('cedula', '')}"
            labels["lbl_persona_extras"].value = f"{p.get('grado_jerarquia', '')} | {p.get('cargo', '')}"
            labels["lbl_persona_extras"].visible = True
        else:
            labels["lbl_persona_resumen"].value = f"{cantidad} personas seleccionadas"
            nombres = [f"{p.get('nombres', '').split(' ')[0]} {p.get('apellidos', '').split(' ')[0]}" for p in personal_list]
            resumen_nombres = ", ".join(nombres)
            labels["lbl_persona_detalle"].value = resumen_nombres if len(resumen_nombres) <= 40 else resumen_nombres[:40] + "..."
            labels["lbl_persona_extras"].visible = False

        try:
            labels["lbl_persona_resumen"].update()
            labels["lbl_persona_detalle"].update()
            labels["lbl_persona_extras"].update()
        except Exception:
            pass
    
    labels["actualizar"] = actualizar
    return labels


def build_error_label(dark_mode=True):
    return ft.Text("", color=ft.Colors.RED_400, size=13, weight=ft.FontWeight.W_500)


class DialogService:
    @staticmethod
    def show_confirm_dialog(page, title, message, on_confirm, on_cancel=None, dark_mode=True):
        tc = theme_colors(dark_mode)
        
        def handle_confirm(e):
            page.pop_dialog()
            on_confirm(e)
        
        def handle_cancel(e):
            page.pop_dialog()
            if on_cancel:
                on_cancel(e)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER_400, size=22),
                ft.Text(title, color=tc["text_primary"], weight=ft.FontWeight.BOLD, size=16),
            ], spacing=10),
            content=ft.Text(message, color=tc["text_secondary"], size=14),
            actions=[
                ft.TextButton("Cancelar", on_click=handle_cancel),
                ft.ElevatedButton(
                    "Confirmar",
                    on_click=handle_confirm,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED_700,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=tc["bg_dialog"],
        )
        page.show_dialog(dialog)

    @staticmethod
    def show_delete_confirmation(page, item_name, on_confirm, dark_mode=True):
        tc = theme_colors(dark_mode)
        DialogService.show_confirm_dialog(
            page,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar \"{item_name}\"? Esta acción no se puede deshacer.",
            on_confirm,
            dark_mode=dark_mode
        )


class NotificationService:
    @staticmethod
    def show_success(page, message, duration=3000):
        if page:
            page.snack_bar = ft.SnackBar(
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                    ft.Text(message, color=ft.Colors.WHITE),
                ], spacing=10),
                bgcolor=ft.Colors.GREEN_700,
                duration=duration,
                open=True,
            )
            page.update()

    @staticmethod
    def show_error(page, message, duration=4000):
        if page:
            page.snack_bar = ft.SnackBar(
                ft.Row([
                    ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE, size=20),
                    ft.Text(message, color=ft.Colors.WHITE),
                ], spacing=10),
                bgcolor=ft.Colors.RED_700,
                duration=duration,
                open=True,
            )
            page.update()

    @staticmethod
    def show_warning(page, message, duration=3500):
        if page:
            page.snack_bar = ft.SnackBar(
                ft.Row([
                    ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.WHITE, size=20),
                    ft.Text(message, color=ft.Colors.WHITE),
                ], spacing=10),
                bgcolor=ft.Colors.AMBER_700,
                duration=duration,
                open=True,
            )
            page.update()

    @staticmethod
    def show_info(page, message, duration=3000):
        if page:
            page.snack_bar = ft.SnackBar(
                ft.Row([
                    ft.Icon(ft.Icons.INFO, color=ft.Colors.WHITE, size=20),
                    ft.Text(message, color=ft.Colors.WHITE),
                ], spacing=10),
                bgcolor=ft.Colors.BLUE_700,
                duration=duration,
                open=True,
            )
            page.update()


class ValidationService:
    @staticmethod
    def validate_cedula(cedula):
        if not cedula:
            return False, "La cédula es requerida"
        if not cedula.isdigit():
            return False, "La cédula debe contener solo números"
        if len(cedula) < 6 or len(cedula) > 10:
            return False, "La cédula debe tener entre 6 y 10 dígitos"
        return True, None

    @staticmethod
    def validate_telefono(telefono):
        if not telefono:
            return True, None
        if not telefono.isdigit():
            return False, "El teléfono debe contener solo números"
        if len(telefono) < 10 or len(telefono) > 15:
            return False, "El teléfono debe tener entre 10 y 15 dígitos"
        return True, None

    @staticmethod
    def validate_required(value, field_name):
        if not value or not value.strip():
            return False, f"{field_name} es requerido"
        return True, None

    @staticmethod
    def validate_date_range(fecha_desde, fecha_hasta):
        if not fecha_desde or not fecha_hasta:
            return True, None
        try:
            from datetime import datetime
            from core.constants import FECHA_FORMAT
            fd = datetime.strptime(fecha_desde, FECHA_FORMAT)
            fh = datetime.strptime(fecha_hasta, FECHA_FORMAT)
            if fd > fh:
                return False, "La fecha de inicio no puede ser mayor que la fecha de fin"
            return True, None
        except ValueError:
            return False, "Formato de fecha inválido"