import flet as ft
import requests
import json

# URL de tu Firebase (Asegúrate de que termine en .json)
FIREBASE_URL = "https://proyecto-gottman-default-rtdb.firebaseio.com/sesiones.json"

def main(page: ft.Page):
    # Configuración básica de la página
    page.title = "App Terapia de Pareja"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = "adaptive"
    page.padding = 20

    # Título y Logo (Globos de diálogo con corazón)
    header = ft.Column(
        controls=[
            ft.Icon(name=ft.icons.SMSO_OUTLINED, color=ft.colors.PINK, size=50),
            ft.Text("❤️", size=20),
            ft.Text("Dinámica de Conexión", size=28, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Este ejercicio busca fortalecer el vínculo y la comunicación en la pareja.",
                italic=True,
                text_align=ft.TextAlign.CENTER,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Campos para nombres
    nombre_1 = ft.TextField(label="Nombre de la primera persona", width=300)
    nombre_2 = ft.TextField(label="Nombre de la segunda persona", width=300)
    
    status_text = ft.Text("", color=ft.colors.BLUE)

    def guardar_datos(e):
        if not nombre_1.value or not nombre_2.value:
            status_text.value = "Por favor, escribe ambos nombres."
            status_text.color = ft.colors.RED
            page.update()
            return

        # Datos a enviar
        datos = {
            "pareja": f"{nombre_1.value} y {nombre_2.value}",
            "fecha": "2026-02-23"  # Fecha actual
        }

        status_text.value = "Guardando en la nube..."
        status_text.color = ft.colors.BLUE
        page.update()

        try:
            # Intentamos la conexión
            respuesta = requests.post(FIREBASE_URL, json=datos, timeout=10)
            
            if respuesta.status_code == 200:
                status_text.value = "¡Datos guardados con éxito! Pueden comenzar."
                status_text.color = ft.colors.GREEN
                # Aquí podrías navegar a la siguiente pantalla del ejercicio
            else:
                status_text.value = f"Error del servidor: {respuesta.status_code}"
                status_text.color = ft.colors.ORANGE
        except Exception as ex:
            # Si falla el internet o Firebase, esto evita la pantalla blanca
            status_text.value = f"Error de conexión: Verifica tu internet o URL."
            status_text.color = ft.colors.RED
            print(f"Detalle del error: {ex}")
        
        page.update()

    # Botón de inicio
    btn_continuar = ft.ElevatedButton(
        text="Comenzar Ejercicio",
        icon=ft.icons.PLAY_ARROW,
        on_click=guardar_datos,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
    )

    # Construcción de la interfaz
    page.add(
        header,
        ft.Divider(height=20, color=ft.colors.TRANSPARENT),
        nombre_1,
        nombre_2,
        ft.Divider(height=10, color=ft.colors.TRANSPARENT),
        btn_continuar,
        status_text
    )

# Ejecución de la App
if __name__ == "__main__":
    ft.app(target=main)
