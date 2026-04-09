import flet as ft


def theme_colors(dark=True):
    if dark:
        return {
            "bg_primary": "#121212",
            "bg_surface": "#1a1a1a",
            "bg_card": "#1e1e1e",
            "bg_input": "#161616",
            "bg_dialog": "#252525",
            "text_primary": ft.Colors.WHITE,
            "text_secondary": ft.Colors.GREY_400,
            "text_tertiary": ft.Colors.GREY_500,
            "text_hint": ft.Colors.GREY_500,
            "border_primary": ft.Colors.GREY_700,
            "border_secondary": ft.Colors.GREY_800,
            "border_input": "#2a2a2a",
            "divider": ft.Colors.GREY_700,
            "header_bg": "#1a1a1a",
            "header_border": ft.Colors.GREY_800,
            "table_header": ft.Colors.GREY_400,
            "table_row_text": ft.Colors.GREY_300,
            "table_name_text": ft.Colors.WHITE,
            "table_header_bg": ft.Colors.with_opacity(0.06, ft.Colors.GREEN),
            "table_row_hover": ft.Colors.with_opacity(0.05, ft.Colors.GREEN),
            "table_border": ft.Colors.GREY_700,
            "input_bg": "#161616",
            "input_border": "#2a2a2a",
            "input_label": ft.Colors.GREY_400,
            "input_text": ft.Colors.WHITE,
            "stat_bg": "#1e1e1e",
            "stat_border": ft.Colors.GREY_700,
            "badge_green": ft.Colors.with_opacity(0.1, ft.Colors.GREEN),
            "badge_amber": ft.Colors.with_opacity(0.1, ft.Colors.AMBER),
            "badge_red": ft.Colors.with_opacity(0.1, ft.Colors.RED),
            "badge_cyan": ft.Colors.with_opacity(0.1, ft.Colors.CYAN),
            "icon_bg": ft.Colors.with_opacity(0.1, ft.Colors.GREEN_400),
            "empty_icon_bg": ft.Colors.with_opacity(0.06, ft.Colors.GREEN),
            "empty_text": ft.Colors.GREY_300,
            "empty_subtext": ft.Colors.GREY_500,
            "empty_icon": ft.Colors.GREY_600,
            "sidebar_bg": "#141414",
            "sidebar_border": "#2a2a2a",
            "sidebar_text": ft.Colors.GREY_300,
            "sidebar_icon": ft.Colors.GREY_500,
            "sidebar_item_active_bg": ft.Colors.with_opacity(0.12, ft.Colors.GREEN),
            "sidebar_item_hover": ft.Colors.with_opacity(0.06, ft.Colors.GREY),
            "sidebar_divider": ft.Colors.GREY_700,
        }
    else:
        return {
            "bg_primary": ft.Colors.GREY_100,
            "bg_surface": ft.Colors.WHITE,
            "bg_card": ft.Colors.WHITE,
            "bg_input": ft.Colors.WHITE,
            "bg_dialog": ft.Colors.WHITE,
            "text_primary": ft.Colors.BLACK87,
            "text_secondary": ft.Colors.GREY_600,
            "text_tertiary": ft.Colors.GREY_500,
            "text_hint": ft.Colors.GREY_400,
            "border_primary": ft.Colors.GREY_300,
            "border_secondary": ft.Colors.GREY_200,
            "border_input": ft.Colors.GREY_300,
            "divider": ft.Colors.GREY_300,
            "header_bg": ft.Colors.WHITE,
            "header_border": ft.Colors.GREY_300,
            "table_header": ft.Colors.GREY_700,
            "table_row_text": ft.Colors.GREY_700,
            "table_name_text": ft.Colors.BLACK87,
            "table_header_bg": ft.Colors.with_opacity(0.08, ft.Colors.GREEN),
            "table_row_hover": ft.Colors.with_opacity(0.04, ft.Colors.GREEN),
            "table_border": ft.Colors.GREY_300,
            "input_bg": ft.Colors.WHITE,
            "input_border": ft.Colors.GREY_300,
            "input_label": ft.Colors.GREY_600,
            "input_text": ft.Colors.BLACK87,
            "stat_bg": ft.Colors.WHITE,
            "stat_border": ft.Colors.GREY_300,
            "badge_green": ft.Colors.with_opacity(0.1, ft.Colors.GREEN),
            "badge_amber": ft.Colors.with_opacity(0.1, ft.Colors.AMBER),
            "badge_red": ft.Colors.with_opacity(0.1, ft.Colors.RED),
            "badge_cyan": ft.Colors.with_opacity(0.1, ft.Colors.CYAN),
            "icon_bg": ft.Colors.with_opacity(0.1, ft.Colors.GREEN_700),
            "empty_icon_bg": ft.Colors.with_opacity(0.08, ft.Colors.GREEN),
            "empty_text": ft.Colors.GREY_700,
            "empty_subtext": ft.Colors.GREY_500,
            "empty_icon": ft.Colors.GREY_400,
            "sidebar_bg": ft.Colors.WHITE,
            "sidebar_border": ft.Colors.GREY_200,
            "sidebar_text": ft.Colors.GREY_700,
            "sidebar_icon": ft.Colors.GREY_600,
            "sidebar_item_active_bg": ft.Colors.with_opacity(0.1, ft.Colors.GREEN),
            "sidebar_item_hover": ft.Colors.with_opacity(0.06, ft.Colors.GREY),
            "sidebar_divider": ft.Colors.GREY_200,
        }


def create_input(dark=True, **kwargs):
    tc = theme_colors(dark)
    defaults = {
        "border_radius": 10,
        "filled": True,
        "bgcolor": tc["input_bg"],
        "border_color": tc["input_border"],
        "focused_border_color": ft.Colors.GREEN_400,
        "color": tc["input_text"],
        "label_style": ft.TextStyle(color=tc["input_label"]),
        "content_padding": ft.padding.symmetric(horizontal=14, vertical=12),
    }
    for key in ["label", "value", "hint_text", "prefix_icon", "suffix_text"]:
        if key in kwargs:
            defaults[key] = kwargs.pop(key)
    if "expand" in kwargs:
        defaults["expand"] = kwargs.pop("expand")
    if "width" in kwargs:
        defaults["width"] = kwargs.pop("width")
    if "max_length" in kwargs:
        defaults["max_length"] = kwargs.pop("max_length")
    if "input_filter" in kwargs:
        filter_type = kwargs.pop("input_filter")
        if filter_type == "number":
            defaults["input_filter"] = ft.NumbersOnlyInputFilter()
        else:
            defaults["input_filter"] = filter_type
    if "multiline" in kwargs:
        defaults["multiline"] = kwargs.pop("multiline")
    if "min_lines" in kwargs:
        defaults["min_lines"] = kwargs.pop("min_lines")
    if "max_lines" in kwargs:
        defaults["max_lines"] = kwargs.pop("max_lines")
    defaults.update(kwargs)
    return ft.TextField(**defaults)


def create_primary_button(text, icon=None, on_click=None, dark=True):
    content = []
    if icon:
        content.append(ft.Icon(icon, color=ft.Colors.WHITE, size=20))
    content.append(ft.Text(text, color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.BOLD))
    return ft.Container(
        content=ft.Row(content, spacing=8),
        gradient=ft.LinearGradient(
            begin=ft.Alignment.CENTER_LEFT,
            end=ft.Alignment.CENTER_RIGHT,
            colors=["#1b5e20", "#2e7d32"],
        ),
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=28, vertical=14),
        ink=True,
        on_click=on_click,
    )


def create_secondary_button(text, icon=None, on_click=None, dark=True):
    tc = theme_colors(dark)
    content = []
    if icon:
        content.append(ft.Icon(ft.Icons.ARROW_BACK, color=tc["text_secondary"], size=20))
    content.append(ft.Text(text, color=tc["text_secondary"], size=14, weight=ft.FontWeight.BOLD))
    return ft.Container(
        content=ft.Row(content, spacing=8),
        border=ft.border.all(1, tc["border_primary"]),
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=28, vertical=14),
        ink=True,
        on_click=on_click,
    )


def create_success_button(text, on_click=None):
    return ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.CHECK, color=ft.Colors.WHITE, size=20),
            ft.Text(text, color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.BOLD),
        ], spacing=8),
        bgcolor=ft.Colors.GREEN_700,
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=28, vertical=14),
        ink=True,
        on_click=on_click,
    )


def create_danger_button(text, on_click=None):
    return ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.DELETE, color=ft.Colors.WHITE, size=20),
            ft.Text(text, color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.BOLD),
        ], spacing=8),
        bgcolor=ft.Colors.RED_700,
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=28, vertical=14),
        ink=True,
        on_click=on_click,
    )


def create_stat_card(dark=True, icon=None, value="0", label="", accent=ft.Colors.GREEN_400):
    tc = theme_colors(dark)
    return ft.Container(
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
        padding=ft.padding.symmetric(vertical=16, horizontal=18),
        expand=True,
        border=ft.border.all(1, tc["stat_border"]),
    )


def create_header(dark=True, title="", subtitle="", icon=ft.Icons.HOME):
    tc = theme_colors(dark)
    return ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Icon(icon, color=ft.Colors.GREEN_400, size=26),
                    bgcolor=tc["icon_bg"],
                    border_radius=10,
                    padding=10,
                ),
                ft.Column([
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                    ft.Text(subtitle, size=12, color=tc["text_secondary"]),
                ], spacing=2),
            ], spacing=14),
        ]),
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        bgcolor=tc["header_bg"],
        border=ft.border.all(1, tc["header_border"]),
        border_radius=14,
    )


def apply_page_theme(page, is_dark=True):
    page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN_400 if is_dark else ft.Colors.GREEN_600)
    page.bgcolor = theme_colors(is_dark)["bg_primary"]
    page.update()


def create_empty_state(
    icon=ft.Icons.INBOX_OUTLINED,
    title="No hay datos",
    subtitle="No hay registros para mostrar",
    dark=True
):
    tc = theme_colors(dark)
    return ft.Column(
        [
            ft.Container(
                content=ft.Icon(icon, size=64, color=tc["empty_icon"]),
                bgcolor=tc["empty_icon_bg"],
                border_radius=50,
                width=120,
                height=120,
                alignment=ft.alignment.center,
            ),
            ft.Text(title, size=18, color=tc["empty_text"], weight=ft.FontWeight.W_500),
            ft.Text(subtitle, size=13, color=tc["empty_subtext"]),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16,
    )


def create_loading_indicator(dark=True, text="Cargando..."):
    tc = theme_colors(dark)
    return ft.Column(
        [
            ft.ProgressRing(width=40, height=40, color=ft.Colors.GREEN_400),
            ft.Text(text, size=14, color=tc["text_secondary"]),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )
