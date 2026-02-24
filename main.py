import flet as ft

def main(page: ft.Page):
    page.title = "Prueba de Vida"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.add(
        ft.Icon(name=ft.icons.CHECK_CIRCLE, color="green", size=50),
        ft.Text("¡LOGRADO, PABLO!", size=30, weight="bold"),
        ft.Text("Si ves esto, la configuración es correcta.", size=16),
        ft.ElevatedButton("Continuar", on_click=lambda _: print("Click"))
    )

ft.app(target=main)
