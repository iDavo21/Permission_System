import flet as ft
from datetime import datetime
from core.theme import theme_colors


class FilterPanelBase(ft.Container):
    def __init__(self, on_apply=None, on_close=None, dark_mode=True, show_search=True, page_ref=None):
        super().__init__()
        self.dark_mode = dark_mode
        self.on_apply_callback = on_apply
        self.on_close_callback = on_close
        self.show_search = show_search
        self._page_ref = page_ref
        
        tc = theme_colors(self.dark_mode)
        self.bgcolor = tc["bg_dialog"]
        self.border = ft.border.all(1, tc["border_primary"])
        self.border_radius = 12
        self.padding = 16
        self.width = 420
        self.shadow = ft.BoxShadow(blur_radius=20, spread_radius=2, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
        self.animate_opacity = ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT)
        
        self._build_ui(tc)
    
    def _build_ui(self, tc):
        self.filtro_texto = ft.TextField(
            hint_text="Buscar...",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            border_radius=10,
            filled=True,
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            color=tc["input_text"],
            label_style=ft.TextStyle(color=tc["input_label"]),
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            text_size=13,
        )
        
        self.btn_aplicar = ft.Container(
            content=ft.Text("Aplicar", color=ft.Colors.WHITE, size=13, weight=ft.FontWeight.BOLD),
            bgcolor=ft.Colors.GREEN_700,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ink=True,
            on_click=lambda e: self._aplicar(),
        )
        
        self.btn_limpiar = ft.Container(
            content=ft.Text("Limpiar", color=tc["text_secondary"], size=13),
            border=ft.border.all(1, tc["border_primary"]),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ink=True,
            on_click=lambda e: self._limpiar(),
        )
        
        self._dropdowns = {}
        self._date_fields = {}
        
        contenido = [self._build_header(tc)]
        
        if self.show_search:
            contenido.append(ft.Container(height=12))
            contenido.append(self.filtro_texto)
        
        contenido.append(ft.Container(height=12))
        contenido.append(self._build_dropdowns_section())
        contenido.append(ft.Container(height=8))
        contenido.append(ft.Container(height=0))  # Placeholder for date fields
        contenido.append(ft.Container(height=12))
        contenido.append(ft.Row([self.btn_aplicar, ft.Container(width=8), self.btn_limpiar], spacing=8))
        
        self.content = ft.Column(contenido, spacing=0)
    
    def _build_header(self, tc):
        return ft.Row([
            ft.Icon(ft.Icons.FILTER_LIST, color=ft.Colors.GREEN_400, size=18),
            ft.Text("Filtros", size=16, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
            ft.Container(expand=True),
            ft.IconButton(
                icon=ft.Icons.CLOSE,
                icon_color=tc["text_secondary"],
                icon_size=18,
                on_click=lambda e: self._cerrar() if self.on_close_callback else None,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    def _build_dropdowns_section(self):
        return ft.Column([
            self._build_dropdown_row(i) 
            for i in range(len(self._dropdowns))
        ], spacing=8) if self._dropdowns else ft.Container()
    
    def _build_dropdown_row(self, row_index):
        row_dropdowns = [d for i, d in enumerate(self._dropdowns.values()) if i % 2 == row_index]
        return ft.Row(row_dropdowns, spacing=12)
    
    def add_date_range(self, key, label_from="Desde", label_to="Hasta"):
        tc = theme_colors(self.dark_mode)
        
        self._date_ranges = getattr(self, '_date_ranges', {})
        
        date_from = ft.TextField(
            label=label_from,
            hint_text="DD/MM/AAAA",
            width=130,
            border_radius=10,
            filled=True,
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            color=tc["input_text"],
            label_style=ft.TextStyle(color=tc["input_label"]),
            text_size=12,
        )
        
        date_to = ft.TextField(
            label=label_to,
            hint_text="DD/MM/AAAA",
            width=130,
            border_radius=10,
            filled=True,
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            color=tc["input_text"],
            label_style=ft.TextStyle(color=tc["input_label"]),
            text_size=12,
        )
        
        self._date_ranges[key] = {"from": date_from, "to": date_to}
        self._rebuild_date_ranges()
        return date_from, date_to
    
    def _rebuild_date_ranges(self):
        for idx, (key, fields) in enumerate(self._date_ranges.items()):
            section_idx = 3 + (len(self._dropdowns) > 0)
            while len(self.content.controls) <= section_idx:
                self.content.controls.append(ft.Container())
            
            date_controls = []
            for field_key, field in fields.items():
                date_controls.append(field)
            
            self.content.controls[section_idx] = ft.Column(date_controls, spacing=8)
    
    def add_dropdown(self, key, label, options, default="Todos"):
        tc = theme_colors(self.dark_mode)
        dropdown = ft.Dropdown(
            label=label,
            width=180,
            options=[ft.dropdown.Option("Todos")] + [ft.dropdown.Option(o) for o in options],
            value=default,
            border_radius=10,
            filled=True,
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            color=tc["input_text"],
            label_style=ft.TextStyle(color=tc["input_label"]),
        )
        self._dropdowns[key] = dropdown
        self._rebuild_dropdowns_content()
        return dropdown
    
    def add_date_field(self, key, label="Fecha", page=None):
        tc = theme_colors(self.dark_mode)
        
        from datetime import datetime
        
        page_to_use = page if page is not None else self._page_ref
        
        date_field = ft.TextField(
            label=label,
            hint_text="DD/MM/AAAA",
            width=110,
            border_radius=10,
            filled=True,
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            color=tc["input_text"],
            label_style=ft.TextStyle(color=tc["input_label"]),
            text_size=12,
            read_only=True,
        )
        
        date_picker = ft.DatePicker(
            first_date=datetime(2000, 1, 1),
            last_date=datetime(2050, 12, 31),
            on_change=lambda e, k=key: self._on_date_picked(e, k),
        )
        
        def open_picker(e):
            container = e.control
            while container and not hasattr(container, 'page'):
                container = container.parent if hasattr(container, 'parent') else None
            
            target_page = None
            if container and hasattr(container, 'page'):
                target_page = container.page
            
            if not target_page and page_to_use:
                target_page = page_to_use
            
            if target_page:
                if date_picker not in target_page.overlay:
                    target_page.overlay.append(date_picker)
                date_picker.open = True
                target_page.update()
        
        btn_calendar = ft.Container(
            content=ft.Icon(ft.Icons.CALENDAR_TODAY, size=18, color=tc["text_secondary"]),
            ink=True,
            on_click=open_picker,
            padding=8,
        )
        
        row = ft.Row([date_field, btn_calendar], spacing=2, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        
        self._date_fields = getattr(self, '_date_fields', {})
        self._date_fields[key] = {"field": date_field, "picker": date_picker, "row": row, "page": page_to_use}
        self._rebuild_date_fields()
        return row
    
    def _on_date_picked(self, e, key):
        picker = e.control
        selected_date = picker.value
        if selected_date and key in self._date_fields:
            date_str = selected_date.strftime("%d/%m/%Y")
            self._date_fields[key]["field"].value = date_str
            self._date_fields[key]["field"].update()
            filtros = self.get_filtros()
            if self.on_apply_callback:
                self.on_apply_callback(filtros)
    
    def _rebuild_dropdowns_content(self):
        self.content.controls[3] = self._build_dropdowns_section()
    
    def _rebuild_date_fields(self):
        date_fields_col = ft.Column([], spacing=8)
        for key, data in getattr(self, '_date_fields', {}).items():
            date_fields_col.controls.append(data["row"])
        
        if len(self.content.controls) > 5:
            self.content.controls[5] = date_fields_col
        else:
            self.content.controls.append(date_fields_col)
    
    def get_filtros(self):
        filtros = {"texto": (self.filtro_texto.value or "").strip().lower()}
        
        for key, dropdown in self._dropdowns.items():
            filtros[key] = dropdown.value if dropdown.value else "Todos"
        
        for key, data in getattr(self, '_date_fields', {}).items():
            filtros[key] = data["field"].value or ""
        
        return filtros
    
    def set_filtro(self, key, value):
        if key in self._dropdowns:
            self._dropdowns[key].value = value
    
    def _aplicar(self):
        if self.on_apply_callback:
            self.on_apply_callback(self.get_filtros())
    
    def _limpiar(self):
        self.filtro_texto.value = ""
        for dropdown in self._dropdowns.values():
            dropdown.value = "Todos"
        for data in getattr(self, '_date_fields', {}).values():
            data["field"].value = ""
        self._actualizar_dropdowns()
        if self.on_apply_callback:
            self.on_apply_callback(self.get_filtros())
    
    def _cerrar(self):
        if self.on_close_callback:
            self.on_close_callback()
    
    def _actualizar_dropdowns(self):
        for dropdown in self._dropdowns.values():
            dropdown.update()
    
    def rebuild_dropdowns(self):
        tc = theme_colors(self.dark_mode)
        for key, dropdown in self._dropdowns.items():
            dropdown.bgcolor = tc["input_bg"]
            dropdown.border_color = tc["input_border"]
            dropdown.color = tc["input_text"]
            dropdown.label_style = ft.TextStyle(color=tc["input_label"])
        self.update()


class FilterPanelContainer(ft.Container):
    def __init__(self, filter_panel=None, dark_mode=True):
        super().__init__()
        self.dark_mode = dark_mode
        self.filter_panel = filter_panel
        self.opacity = 0
        self.visible = False
        self.top = 145
        self.right = 0
        self.left = 0
        self.animate_opacity = ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT)
        
        self.content = ft.Row(
            [self.filter_panel] if self.filter_panel else [],
            alignment=ft.MainAxisAlignment.END
        )
        self.padding = ft.padding.only(right=24)
    
    def set_page(self, page):
        if self.filter_panel:
            self.filter_panel._page_ref = page
            for key, data in getattr(self.filter_panel, '_date_fields', {}).items():
                data["page"] = page
    
    def show(self):
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
    
    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def set_filter_panel(self, fp):
        self.filter_panel = fp
        self.content = ft.Row([fp], alignment=ft.MainAxisAlignment.END)
        try:
            self.update()
        except RuntimeError:
            pass