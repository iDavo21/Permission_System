import flet as ft
from views.login_view import LoginView
from controllers.main_controller import MainController

def main(page: ft.Page):
    page.title = "Sistema de Vacaciones"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Inicializar el controlador
    main_controller = MainController(page)

    # Inicializar la vista pasándole la función manejadora del controlador
    login_view = LoginView(on_login_click=main_controller.attempt_login)
    
    # Registrar la vista en el controlador (para poder mostrar errores)
    main_controller.set_login_view(login_view)

    # Agregar la vista de Login a la página
    page.add(login_view)

if __name__ == "__main__":
    ft.run(main)
