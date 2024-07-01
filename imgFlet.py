import flet as ft
from tkinter import filedialog, Tk
from pathlib import Path
from rembg import remove
from PIL import Image
import os


def mostrar_dialogo(titulo, mensaje, page: ft.Page):
    dialog = ft.AlertDialog(title=ft.Text(mensaje))
    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def optimizar_imagenes(file_path, calidad, destino, lista_procesos, page):
    Path(destino).mkdir(parents=True, exist_ok=True)
    img = Image.open(file_path)
    nombre_archivo = os.path.basename(file_path)
    ruta_salida = Path(destino) / nombre_archivo
    img.save(ruta_salida, quality=calidad, optimize=True)
    mensage = f"Optimizando {file_path} y guardando en {ruta_salida}"
    lista_procesos.controls.append(ft.Text(mensage))
    print(f"Optimizando {file_path} y guardando en {ruta_salida}")
    page.update()


def remover_fondo(file_path, destino, lista_procesos, page):
    Path(destino).mkdir(parents=True, exist_ok=True)
    nombre_archivo = os.path.basename(file_path)
    ruta_salida = Path(destino) / nombre_archivo

    with open(file_path, "rb") as i:
        img = i.read()
        salida = remove(img)

    with open(ruta_salida, "wb") as o:
        o.write(salida)
    mensage = f"Removiendo fondo de {file_path} y guardando en {ruta_salida}"
    lista_procesos.controls.append(ft.Text(mensage))
    print(f"Removiendo fondo de {file_path} y guardando en {ruta_salida}")
    page.update()


def main(page: ft.Page):
    archivo_seleccionado = False
    is_file = False
    is_path_destino = ""
    lista_archivos = []
    optimizar = True
    lista_procesos = ft.Column()

    def seleccionar_archivo(e):
        file_picker.pick_files(
            file_type=ft.FilePickerFileType.IMAGE,
            allow_multiple=True,
            allowed_extensions=["jpg", "jpeg", "png"],
        )

    def archivo_seleccionado_handler(e):
        nonlocal archivo_seleccionado, is_file
        if file_picker.result is not None:
            lista_archivos.clear()
            files = file_picker.result.files
            archivo_seleccionado = True
            for file in files:
                lista_archivos.append(file.path)
                print("file: ", file.path)
            is_file = True
            actualizar_estado_botones()

    def seleccionar_carpeta_salida(e):
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        root.update()
        folder_salida = filedialog.askdirectory(title="Selecciona la carpeta de salida")
        root.destroy()  # Cierra la ventana de Tkinter
        nonlocal is_path_destino
        if folder_salida:
            is_path_destino = folder_salida

    def actualizar_estado_botones():
        boton_carpeta_salida.disabled = not archivo_seleccionado
        numero_input.visible = optimizar
        page.update()

    def opcion_seleccionada(calidad):
        nonlocal is_file, is_path_destino, optimizar
        if optimizar:
            lista_procesos.controls.append(ft.Text("En proceso..."))
            for file in lista_archivos:
                optimizar_imagenes(file, calidad, is_path_destino, lista_procesos, page)
        else:
            lista_procesos.controls.append(ft.Text("En proceso..."))
            for file in lista_archivos:
                remover_fondo(file, is_path_destino, lista_procesos, page)
        is_file = False
        lista_procesos.controls.append(ft.Text("Proceso terminado"))
        page.update()
        is_path_destino = ""
        lista_archivos.clear()

        mostrar_dialogo("Proceso terminado", "Proceso terminado", page)

    def enviar_numero(e):
        if not optimizar:
            opcion_seleccionada(50)
            return
        try:
            numero = int(numero_input.value)
            if 1 <= numero <= 100:
                opcion_seleccionada(numero)
            else:
                mostrar_dialogo(
                    "Número inválido", "Ingresa un número entre 1 y 100.", page
                )
        except ValueError:
            mostrar_dialogo("Número inválido", "Ingresa un número válido.", page)

    def seleccionar_optimizar(e):
        nonlocal optimizar
        optimizar = True
        boton_optimizar_imagenes.disabled = True
        boton_remover_fondo.disabled = False
        actualizar_estado_botones()

    def seleccionar_remover_fondo(e):
        nonlocal optimizar
        optimizar = False
        boton_optimizar_imagenes.disabled = False
        boton_remover_fondo.disabled = True
        actualizar_estado_botones()

    file_picker = ft.FilePicker(on_result=archivo_seleccionado_handler)

    numero_input = ft.TextField(
        label="Ingresa la calidad (1-100)",
        width=200,
        visible=True,
        bgcolor=ft.colors.LIGHT_BLUE_50,
        border_color=ft.colors.BLUE,
    )

    boton_carpeta_salida = ft.ElevatedButton(
        "Seleccionar carpeta de salida",
        on_click=seleccionar_carpeta_salida,
        disabled=True,
        bgcolor=ft.colors.GREEN_600,
        color=ft.colors.WHITE,
    )

    boton_seleccionar_archivo = ft.ElevatedButton(
        "Seleccionar archivos",
        on_click=seleccionar_archivo,
        bgcolor=ft.colors.BLUE_600,
        color=ft.colors.WHITE,
    )

    boton_optimizar_imagenes = ft.ElevatedButton(
        "Optimizar Imágenes",
        on_click=seleccionar_optimizar,
        disabled=False,
        bgcolor=ft.colors.ORANGE_600,
        color=ft.colors.WHITE,
    )

    boton_remover_fondo = ft.ElevatedButton(
        "Remover Fondo",
        on_click=seleccionar_remover_fondo,
        disabled=False,
        bgcolor=ft.colors.RED_600,
        color=ft.colors.WHITE,
    )

    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        boton_optimizar_imagenes,
                        boton_remover_fondo,
                    ],
                    alignment="center",
                    spacing=10,
                ),
                ft.Row(
                    [
                        boton_seleccionar_archivo,
                        boton_carpeta_salida,
                        numero_input,
                        ft.ElevatedButton(
                            "Procesar",
                            on_click=enviar_numero,
                            bgcolor=ft.colors.PURPLE_600,
                            color=ft.colors.WHITE,
                        ),
                    ],
                    alignment="center",
                    spacing=10,
                ),
                lista_procesos,
            ],
            horizontal_alignment="center",
            alignment="center",
            spacing=20,
        ),
        file_picker,
    )


ft.app(target=main)
