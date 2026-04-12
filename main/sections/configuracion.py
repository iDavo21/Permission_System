import flet as ft
import os
from core.theme import theme_colors
from core.backup import crear_backup, obtener_lista_backups
from core.preferencias import set_preferencia


def build(app: 'MainApp'):
    tc = theme_colors(app.dark_mode)
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    
    def _get_db_sizes():
        db_files = ['personal.db', 'permisos.db', 'comisiones.db', 'usuarios.db']
        sizes = {}
        total = 0
        for db in db_files:
            path = os.path.join(data_dir, db)
            if os.path.exists(path):
                size = os.path.getsize(path)
                sizes[db.replace('.db', '')] = size
                total += size
            else:
                sizes[db.replace('.db', '')] = 0
        return sizes, total
    
    def format_size(size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    db_sizes, total_size = _get_db_sizes()
    backups = obtener_lista_backups()
    
    app.lbl_backup_fecha = ft.Text(
        f"Último backup: {backups[0]['fecha']}" if backups else "No hay backups",
        size=12, color=tc["text_secondary"]
    )
    
    app.chk_notificaciones = ft.Switch(
        label="Notificaciones de permisos por expirar",
        value=app.preferencias.get("notificaciones_activadas", True),
        active_color=ft.Colors.GREEN_400,
        on_change=app._guardar_preferencias_handler,
    )
    
    app.drp_dias_anticipacion = ft.Dropdown(
        label="Días de anticipación",
        width=150,
        options=[ft.dropdown.Option(str(i)) for i in [1, 2, 3, 5, 7]],
        value=str(app.preferencias.get("dias_anticipacion", 3)),
        border_radius=10,
        filled=True,
        bgcolor=tc["input_bg"],
        border_color=tc["input_border"],
        color=tc["input_text"],
        label_style=ft.TextStyle(color=tc["input_label"]),
    )
    
    usuario_info = app.usuario_actual or {}
    
    def _crear_backup_handler(e):
        from main.handlers.actions import crear_backup
        crear_backup(app)
    
    def _cambiar_password_handler(e):
        from main.handlers.forms import mostrar_dialogo_cambiar_password
        mostrar_dialogo_cambiar_password(app)
    
    def _limpiar_permisos_handler(e):
        from main.handlers.actions import mostrar_dialogo_limpiar_permisos
        mostrar_dialogo_limpiar_permisos(app)
    
    def _exportar_datos_handler(e):
        from main.handlers.actions import exportar_todos_datos
        exportar_todos_datos(app)
    
    def _crear_card(titulo, icono, contenido, color_icono=ft.Colors.GREEN_400):
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icono, color=color_icono, size=22),
                    ft.Text(titulo, size=14, weight=ft.FontWeight.BOLD, color=tc["text_primary"])], spacing=8),
                ft.Container(height=8),
                contenido,
            ], spacing=4),
            bgcolor=tc["bg_card"],
            border_radius=12,
            padding=16,
            border=ft.border.all(1, tc["border_primary"]),
            expand=True,
        )
    
    card_usuario = _crear_card(
        "Usuario", ft.Icons.PERSON,
        ft.Column([
            ft.Text(f"Usuario: {usuario_info.get('username', 'N/A')}", size=13, color=tc["text_secondary"]),
            ft.Text(f"Nombre: {usuario_info.get('nombre', 'N/A')}", size=13, color=tc["text_secondary"]),
            ft.Text(f"Rol: {usuario_info.get('rol', 'N/A')}", size=13, color=tc["text_secondary"]),
            ft.Container(height=8),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.LOCK, size=16, color=tc["text_secondary"]),
                    ft.Text("Cambiar password", size=12, color=ft.Colors.GREEN_400)], spacing=6),
                ink=True, on_click=_cambiar_password_handler,
            ),
        ], tight=True)
    )
    
    lista_backups = ft.Column([], spacing=4)
    if backups:
        for b in backups[:5]:
            lista_backups.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.FOLDER_ZIP, size=16, color=tc["text_secondary"]),
                        ft.Text(b['nombre'], size=11, color=tc["text_tertiary"], expand=True),
                        ft.Text(b['fecha'], size=10, color=tc["text_tertiary"]),
                    ], spacing=8), padding=4,
                )
            )
    else:
        lista_backups.controls.append(ft.Text("No hay backups", size=11, color=tc["text_tertiary"]))
    
    card_backup = _crear_card(
        "Respaldo", ft.Icons.BACKUP,
        ft.Column([
            app.lbl_backup_fecha, ft.Container(height=8),
            ft.Container(
                content=ft.ElevatedButton("Crear Backup", icon=ft.Icons.SAVE,
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700,
                        shape=ft.RoundedRectangleBorder(radius=8)), on_click=_crear_backup_handler),
            ),
            ft.Container(height=8),
            ft.Text("Backups recientes:", size=11, weight=ft.FontWeight.BOLD, color=tc["text_secondary"]),
            ft.Container(height=4),
            lista_backups,
        ], tight=True)
    )
    
    card_sistema = _crear_card(
        "Sistema", ft.Icons.INFO,
        ft.Column([
            ft.Text("Versión: 1.0.0", size=13, color=tc["text_secondary"]),
            ft.Text(f"Tamaño total BD: {format_size(total_size)}", size=13, color=tc["text_secondary"]),
            ft.Divider(height=16, color=tc["divider"]),
            ft.Text("Bases de datos:", size=11, weight=ft.FontWeight.BOLD, color=tc["text_secondary"]),
            ft.Text(f"Personal: {format_size(db_sizes.get('personal', 0))}", size=11, color=tc["text_tertiary"]),
            ft.Text(f"Permisos: {format_size(db_sizes.get('permisos', 0))}", size=11, color=tc["text_tertiary"]),
            ft.Text(f"Comisiones: {format_size(db_sizes.get('comisiones', 0))}", size=11, color=tc["text_tertiary"]),
            ft.Text(f"Usuarios: {format_size(db_sizes.get('usuarios', 0))}", size=11, color=tc["text_tertiary"]),
        ], tight=True)
    )
    
    card_datos = _crear_card(
        "Datos", ft.Icons.STORAGE,
        ft.Column([
            ft.Container(
                content=ft.ElevatedButton("Limpiar Permisos Expirados", icon=ft.Icons.DELETE_SWEEP,
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.ORANGE_700,
                        shape=ft.RoundedRectangleBorder(radius=8)), on_click=_limpiar_permisos_handler),
            ),
            ft.Container(height=8),
            ft.Container(
                content=ft.ElevatedButton("Exportar Todos los Datos", icon=ft.Icons.DOWNLOAD,
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.CYAN_700,
                        shape=ft.RoundedRectangleBorder(radius=8)), on_click=_exportar_datos_handler),
            ),
        ], tight=True)
    )
    
    card_preferencias = _crear_card(
        "Preferencias", ft.Icons.TUNE,
        ft.Column([
            app.chk_notificaciones, ft.Container(height=12), app.drp_dias_anticipacion,
            ft.Container(height=8),
            ft.Text("Recibe alertas cuando los permisos estén por expirar", size=11, color=tc["text_tertiary"]),
        ], tight=True)
    )
    
    return ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.GREEN_400, size=28),
                            bgcolor=tc["icon_bg"], border_radius=10, padding=10,
                        ),
                        ft.Column([
                            ft.Text("Configuración", size=20, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                            ft.Text("Administra la configuración del sistema", size=12, color=tc["text_secondary"]),
                        ], spacing=2),
                    ], spacing=14),
                ], alignment=ft.MainAxisAlignment.START),
                padding=ft.padding.symmetric(horizontal=24, vertical=16),
                bgcolor=tc["header_bg"],
                border=ft.border.all(1, tc["header_border"]),
                margin=ft.margin.only(left=24, right=24, top=16),
            ),
            ft.Container(height=24),
            ft.Container(
                content=ft.Row([card_usuario, card_backup], spacing=16),
                padding=ft.padding.symmetric(horizontal=24),
            ),
            ft.Container(height=16),
            ft.Container(
                content=ft.Row([card_sistema, card_datos], spacing=16),
                padding=ft.padding.symmetric(horizontal=24),
            ),
            ft.Container(height=16),
            ft.Container(
                content=card_preferencias,
                padding=ft.padding.symmetric(horizontal=24),
            ),
            ft.Container(expand=True),
        ], expand=True, scroll=ft.ScrollMode.AUTO),
        expand=True,
        padding=ft.padding.only(top=8),
    )