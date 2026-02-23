import flet as ft
import time
import threading
import requests
from datetime import datetime

def main(page: ft.Page):
    # --- CONFIGURACIÓN DE LA VENTANA ---
    page.title = "Reducción de Estrés - Método Gottman"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "start"
    page.scroll = "auto" 
    page.theme_mode = "light"
    page.window_width = 400 
    page.window_height = 800

    # --- CONFIGURACIÓN DE FIREBASE ---
    # Nota: Agregamos "/sesiones.json" al final de tu URL para que Firebase sepa dónde guardar los datos
    FIREBASE_URL = "https://conversacion-conecta-default-rtdb.firebaseio.com/sesiones.json"

    # --- VARIABLES DE ESTADO ---
    tiempo_total_ejercicio = 900 # 15 minutos en segundos
    estado = {"turno": 1, "hablante": "", "oyente": "", "tiempo_restante": tiempo_total_ejercicio, "corriendo": False}

    # --- COMPONENTES VISUALES ---
    titulo = ft.Text("Conversación que Conecta", size=22, weight="bold", text_align="center")
    
    input_p1 = ft.TextField(label="Nombre Pareja 1", width=300, prefix_icon="person")
    input_p2 = ft.TextField(label="Nombre Pareja 2", width=300, prefix_icon="person_outline")
    
    texto_instruccion_hablante = ft.Text(size=14, color="blue", weight="w500")
    texto_instruccion_oyente = ft.Text(size=14, color="green", weight="w500")
    
    texto_reloj = ft.Text("15:00", size=32, weight="bold", color="black")
    anillo_progreso = ft.ProgressRing(
        width=130, 
        height=130, 
        stroke_width=8, 
        value=1.0, 
        color="blue",
        bgcolor="#e3f2fd" 
    )
    
    reloj_visual = ft.Stack(
        controls=[
            anillo_progreso,
            ft.Container(
                content=texto_reloj,
                alignment=ft.alignment.center,
                width=130,
                height=130
            )
        ],
        width=130,
        height=130
    )
    
    tarjetas_apoyo = ft.Card(
        elevation=4,
        content=ft.Container(
            content=ft.Column([
                ft.Text("💡 Guía para el Oyente:", weight="bold"),
                ft.Text("• Realiza contacto visual", color="blue_grey_700"),
                ft.Text("• Muestra interés", color="blue_grey_700"),
                ft.Text("• '¿Y cómo te hizo sentir eso?'"),
                ft.Text("• 'Tiene todo el sentido que estés frustrado/a.'"),
                ft.Text("• 'Estamos juntos en esto.'"),
                ft.Text("• Valida a tu pareja", color="blue_grey_700"),
                ft.Text("• '¿Puedo ayudarte con algo?'", color="blue_grey_700")
            ]),
            padding=15
        )
    )

    logo_nuevo = ft.Stack(
        controls=[
            ft.Icon("forum", size=70, color="blue"),
            ft.Container(
                content=ft.Icon("favorite", size=25, color="red"),
                alignment=ft.alignment.center,
                padding=ft.padding.only(left=22, top=12) 
            )
        ],
        width=80,
        height=80
    )

    mensaje_objetivo = ft.Text(
        "Objetivo: Crear un espacio seguro para compartir el estrés diario ajeno a la relación. El oyente practica la empatía y la validación, mientras el hablante se desahoga sin ser juzgado.",
        text_align="center",
        color="blue_grey_700",
        italic=True,
        size=14
    )

    # --- FUNCIONES DE LÓGICA Y NAVEGACIÓN ---
    def actualizar_reloj():
        while estado["tiempo_restante"] > 0 and estado["corriendo"]:
            mins, secs = divmod(estado["tiempo_restante"], 60)
            texto_reloj.value = f"{mins:02d}:{secs:02d}"
            anillo_progreso.value = estado["tiempo_restante"] / tiempo_total_ejercicio
            
            page.update()
            time.sleep(1)
            estado["tiempo_restante"] -= 1
        
        if estado["tiempo_restante"] <= 0 and estado["corriendo"]:
            estado["corriendo"] = False
            texto_reloj.value = "00:00"
            anillo_progreso.value = 0
            page.update()
            mostrar_alerta_tiempo()

    def mostrar_alerta_tiempo():
        dlg_tiempo = ft.AlertDialog(
            title=ft.Text("⏰ ¡Tiempo cumplido!"),
            content=ft.Text("Es momento de cambiar de turno o finalizar el ejercicio."),
            actions=[ft.TextButton("Entendido", on_click=lambda e: page.close(dlg_tiempo))]
        )
        page.open(dlg_tiempo)

    def iniciar_sesion(e):
        if input_p1.value and input_p2.value:
            estado["hablante"] = input_p1.value
            estado["oyente"] = input_p2.value
            estado["tiempo_restante"] = tiempo_total_ejercicio
            estado["corriendo"] = True
            
            texto_reloj.value = "15:00"
            anillo_progreso.value = 1.0
            
            actualizar_pantalla_activa()
            threading.Thread(target=actualizar_reloj, daemon=True).start()
        else:
            page.open(ft.SnackBar(ft.Text("Por favor, ingresen ambos nombres para el encuadre.")))

    def boton_tiempo_fuera(e):
        estado["corriendo"] = False
        dlg = ft.AlertDialog(
            title=ft.Text("🚨 Tiempo Fuera"),
            content=ft.Text("Parece que necesitan pausar o el tema se está desviando hacia la relación.\n\nRecuerden: Este espacio es para el estrés externo.\n\nRespiren profundo y volvamos al tema original."),
            actions=[ft.TextButton("Entendido, reanudar tiempo", on_click=lambda e: reanudar_tiempo(dlg))]
        )
        page.open(dlg)

    def reanudar_tiempo(dlg):
        page.close(dlg)
        estado["corriendo"] = True
        threading.Thread(target=actualizar_reloj, daemon=True).start()
        page.update()

    def cambiar_turno(e):
        estado["corriendo"] = False
        time.sleep(1.1) 
        
        if estado["turno"] == 1:
            estado["turno"] = 2
            estado["hablante"], estado["oyente"] = estado["oyente"], estado["hablante"]
            estado["tiempo_restante"] = tiempo_total_ejercicio
            estado["corriendo"] = True
            
            texto_reloj.value = "15:00"
            anillo_progreso.value = 1.0
            
            actualizar_pantalla_activa()
            threading.Thread(target=actualizar_reloj, daemon=True).start()
        else:
            finalizar_sesion()

    def enviar_datos_firebase():
        """Envía el registro a Firebase en segundo plano"""
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datos_sesion = {
            "fecha": fecha_actual,
            "pareja_1": input_p1.value,
            "pareja_2": input_p2.value,
            "ejercicio_completado": True
        }
        try:
            # El timeout evita que la app se quede colgada si no hay buen internet
            requests.post(FIREBASE_URL, json=datos_sesion, timeout=5)
            print("Datos enviados correctamente a Firebase")
        except Exception as e:
            print(f"Error al enviar datos: {e}")

    def finalizar_sesion():
        estado["corriendo"] = False
        
        # Disparamos el envío a Firebase en un hilo separado
        threading.Thread(target=enviar_datos_firebase, daemon=True).start()

        page.clean()
        page.add(
            ft.Divider(height=100, color="transparent"),
            ft.Column([
                ft.Icon("favorite", color="red", size=80),
                ft.Text("¡Ejercicio Completado!", size=28, weight="bold"),
                ft.Text("Excelente trabajo escuchándose y apoyándose mutuamente.", size=16, text_align="center"),
                ft.Divider(height=30, color="transparent"),
                ft.Container(
                    content=ft.Text("Cierre sugerido:\nDense un abrazo de 20 segundos.", text_align="center", size=16, weight="bold"),
                    bgcolor="#ffebee",
                    padding=20,
                    border_radius=10
                )
            ], alignment="center", horizontal_alignment="center")
        )
        page.update()

    def actualizar_pantalla_activa():
        page.clean()
        texto_instruccion_hablante.value = f"🗣️ ROL DE {estado['hablante'].upper()} (Hablante):\nHabla de cualquier cosa, EXCEPTO de la relación."
        texto_instruccion_oyente.value = f"👂 ROL DE {estado['oyente'].upper()} (Oyente):\nEscucha sin juzgar.\nNO des consejos."
        
        texto_boton_derecho = "Cambio" if estado["turno"] == 1 else "Finalizar"
        icono_boton_derecho = "skip_next" if estado["turno"] == 1 else "check_circle"
        
        page.add(
            ft.Divider(height=10, color="transparent"),
            titulo,
            ft.Text(f"Turno {estado['turno']} de 2", color="grey"),
            ft.Divider(height=5, color="transparent"),
            
            ft.Row([reloj_visual], alignment="center"),
            ft.Divider(height=5, color="transparent"),
            
            ft.Row([
                ft.Container(content=texto_instruccion_hablante, padding=15, bgcolor="#e3f2fd", border_radius=10, width=350)
            ], alignment="center"),
            
            ft.Divider(height=10, color="transparent"),
            
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.IconButton(icon="pan_tool", icon_color="red", icon_size=30, on_click=boton_tiempo_fuera),
                        ft.Text("Pausa", size=11, color="red", weight="bold")
                    ], horizontal_alignment="center", spacing=0),
                    on_click=boton_tiempo_fuera
                ),
                
                ft.Container(content=texto_instruccion_oyente, padding=15, bgcolor="#e8f5e9", border_radius=10, width=220),
                
                ft.Container(
                    content=ft.Column([
                        ft.IconButton(icon=icono_boton_derecho, icon_color="blue", icon_size=30, on_click=cambiar_turno),
                        ft.Text(texto_boton_derecho, size=11, color="blue", weight="bold")
                    ], horizontal_alignment="center", spacing=0),
                    on_click=cambiar_turno
                )
            ], alignment="center", spacing=5),
            
            ft.Divider(height=15, color="transparent"),
            
            ft.Row([tarjetas_apoyo], alignment="center"),
            ft.Divider(height=20, color="transparent")
        )
        page.update()

    # --- VISTA INICIAL (ONBOARDING) ---
    page.add(
        ft.Divider(height=30, color="transparent"),
        ft.Row([logo_nuevo], alignment="center"),
        titulo,
        ft.Divider(height=10, color="transparent"),
        ft.Container(
            content=mensaje_objetivo,
            padding=ft.padding.symmetric(horizontal=20),
        ),
        ft.Divider(height=10, color="transparent"),
        ft.Text("Introduzcan sus nombres para establecer los roles iniciales:", text_align="center", color="grey"),
        input_p1,
        input_p2,
        ft.Divider(height=20, color="transparent"),
        ft.ElevatedButton("Comenzar Ejercicio", on_click=iniciar_sesion, width=250, height=50, bgcolor="blue", color="white")
    )

ft.app(target=main)
