import flet as ft
from main.app import MainApp


def main(page: ft.Page):
    MainApp(page)


if __name__ == "__main__":
    ft.app(target=main)