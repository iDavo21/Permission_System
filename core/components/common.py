import flet as ft


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