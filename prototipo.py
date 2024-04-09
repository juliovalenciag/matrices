import flet as ft
import numpy as np

def main(page: ft.Page):
    page.title = "Prototipo de programa para resolver matrices con gauss-jordan"
    page.window_width = 1200
    page.window_height = 800
    page.window_center()

    matrix_rows = []

    right_top_section = ft.Column([], expand=True)
    right_bottom_section = ft.Column([], expand=True)

    matrix_container = ft.Column([], spacing=10)

    divider = ft.Divider(thickness=2)
    v_divider = ft.VerticalDivider(thickness=3)

    def update_matrix_layout():
        matrix_container.controls.clear()
        for row_index, row in enumerate(matrix_rows):
            row_controls = [cell for cell_index, cell in enumerate(row)]
            matrix_container.controls.append(ft.Row(row_controls, spacing=5))
        page.update()

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        theme_icon.icon = ft.icons.LIGHT_MODE_ROUNDED if page.theme_mode == ft.ThemeMode.DARK else ft.icons.DARK_MODE_ROUNDED

        for row in matrix_rows:
            for cell in row:
                cell.bgcolor = ft.colors.WHITE if page.theme_mode == ft.ThemeMode.LIGHT else ft.colors.GREY_800

        update_matrix_layout()
        if right_top_section.controls:
            mostrar_resultados(obtener_matriz())
        page.update()

    theme_icon = ft.IconButton(icon=ft.icons.LIGHT_MODE_ROUNDED, tooltip="Cambiar tema", on_click=toggle_theme)

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.update()

    def create_text_field() -> ft.TextField:
        return ft.TextField(width=60, text_align=ft.TextAlign.CENTER, bgcolor=ft.colors.WHITE if page.theme_mode == ft.ThemeMode.LIGHT else ft.colors.GREY_800)

    def create_result_field(value: str) -> ft.TextField:
        bgcolor = ft.colors.GREY_300 if page.theme_mode == ft.ThemeMode.LIGHT else ft.colors.GREY_700
        text_color = ft.colors.BLACK if page.theme_mode == ft.ThemeMode.LIGHT else ft.colors.WHITE
        return ft.TextField(value=value, width=60, text_align=ft.TextAlign.CENTER, read_only=True, bgcolor=bgcolor,
                            color=text_color)

    def adjust_matrix_size(new_rows, new_columns):
        while len(matrix_rows) < new_rows:
            matrix_rows.append([create_text_field() for _ in range(new_columns)])
        while len(matrix_rows) > new_rows:
            matrix_rows.pop()
        for row in matrix_rows:
            while len(row) < new_columns:
                row.append(create_text_field())
            while len(row) > new_columns:
                row.pop()
        update_matrix_layout()

    adjust_matrix_size(3, 4)

    def obtener_matriz():
        return np.array([[float(cell.value) for cell in row] for row in matrix_rows])

    def cambiar_filas(matriz, fila1, fila2):
        matriz[[fila1, fila2]] = matriz[[fila2, fila1]]

    def hacer_ceros_abajo(matriz, fila_pivote):
        n_filas, n_cols = matriz.shape
        for i in range(fila_pivote + 1, n_filas):
            factor = matriz[i, fila_pivote] / matriz[fila_pivote, fila_pivote]
            matriz[i] = matriz[i] - factor * matriz[fila_pivote]

    def hacer_ceros_arriba(matriz, fila_pivote):
        for i in range(fila_pivote - 1, -1, -1):
            factor = matriz[i, fila_pivote] / matriz[fila_pivote, fila_pivote]
            matriz[i] = matriz[i] - factor * matriz[fila_pivote]

    def clear_matrix(event=None):
        for row in matrix_rows:
            for cell in row:
                cell.value = ""
        right_top_section.controls.clear()
        right_bottom_section.controls.clear()
        page.update()

    def solve_matrix(event=None):
        try:
            matriz = obtener_matriz()
            if not matriz.shape[0] + 1 == matriz.shape[1]:
                raise ValueError("La matriz debe incluir una columna adicional para los términos constantes.")
            n_filas, n_cols = matriz.shape

            for fila_pivote in range(n_filas):
                fila_max = np.argmax(abs(matriz[fila_pivote:, fila_pivote])) + fila_pivote
                cambiar_filas(matriz, fila_pivote, fila_max)

                if matriz[fila_pivote, fila_pivote] == 0:
                    right_bottom_section.controls.append(
                        ft.Text("La matriz es singular o el sistema no tiene solución única.", color="red"))
                    page.update()
                    return

                hacer_ceros_abajo(matriz, fila_pivote)

            for fila_pivote in range(n_filas - 1, -1, -1):
                hacer_ceros_arriba(matriz, fila_pivote)

            for i in range(n_filas):
                matriz[i] = matriz[i] / matriz[i, i]

            mostrar_resultados(matriz)

        except ValueError as e:
            show_error(str(e))

    def mostrar_resultados(matriz):
        right_top_section.controls.clear()
        right_bottom_section.controls.clear()
        for fila in matriz:
            result_row = [create_result_field(f"{int(num) if num.is_integer() else num:.2f}".replace('-0.00', '0.00'))
                          for num in fila]
            right_top_section.controls.append(ft.Row(result_row, spacing=5))

        solucion_texto = "\n".join([f"x{i + 1} = {matriz[i, -1]:.2f}" for i in range(matriz.shape[0])])
        right_bottom_section.controls.append(ft.Text(solucion_texto))

        page.update()

    def show_error(message):
        right_bottom_section.controls.clear()
        right_bottom_section.controls.append(ft.Text(value=message, color="red"))
        page.update()

    toolbar_buttons = [
        ft.IconButton(icon=ft.icons.FILE_DOWNLOAD_ROUNDED, tooltip="Exportar Matriz"),
        ft.IconButton(icon=ft.icons.UPLOAD_FILE, tooltip="Importar Matriz",
                      on_click=lambda _: file_picker.pick_files(allow_multiple=True)),
        ft.IconButton(icon=ft.icons.PLAY_ARROW, tooltip="Solve matrix", on_click=solve_matrix),
        ft.IconButton(icon=ft.icons.CLEANING_SERVICES, tooltip="Clear matrix", on_click=clear_matrix),
    ]

    toolbar = ft.Row(
        toolbar_buttons + [v_divider, ft.Container(width=20),v_divider, theme_icon],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        expand=True
    )

    toolbar_container = ft.Container(content=toolbar, padding=5)

    left_section = ft.Container(content=matrix_container, padding=20, expand=True)

    right_section = ft.Column(controls=[right_top_section, divider, right_bottom_section])

    content_section = ft.Row([
        ft.Container(content=left_section, width=600, expand=True),
        v_divider,
        ft.Container(content=right_section, width=600, expand=True),
    ], expand=True)

    page.add(toolbar_container, divider, content_section)

ft.app(target=main)