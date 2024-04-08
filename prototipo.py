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

    def update_matrix_layout():
        matrix_container.controls.clear()
        for row in matrix_rows:
            matrix_container.controls.append(ft.Row([cell for cell in row], spacing=5))
        page.update()

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        theme_icon.icon = ft.icons.LIGHT_MODE_ROUNDED if page.theme_mode == ft.ThemeMode.DARK else ft.icons.DARK_MODE_ROUNDED
        page.update()

    theme_icon = ft.IconButton(icon=ft.icons.LIGHT_MODE_ROUNDED, tooltip="Toggle theme", on_click=toggle_theme)

    def create_text_field() -> ft.TextField:
        return ft.TextField(width=60, text_align=ft.TextAlign.CENTER)

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

    def clear_matrix():
        for row in matrix_rows:
            for cell in row:
                cell.value = ""
        page.update()

    def solve_matrix(event=None):
        try:
            matriz = obtener_matriz()
            if not matriz.shape[0] + 1 == matriz.shape[1]:
                raise ValueError("La matriz debe incluir una columna adicional para los términos constantes.")
            n_filas, n_cols = matriz.shape

            for fila_pivote in range(n_filas):
                # Busca el máximo en esta columna desde fila_pivote hasta el final
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

        matriz_texto = "\n".join(["\t".join([f"{num:.2f}" for num in fila]) for fila in matriz])
        solucion_texto = "\n".join([f"x{i + 1} = {matriz[i, -1]:.2f}" for i in range(matriz.shape[0])])

        right_top_section.controls.append(ft.Text(matriz_texto))
        right_bottom_section.controls.append(ft.Text(solucion_texto))
        page.update()

    def show_error(message):
        right_bottom_section.controls.clear()
        right_bottom_section.controls.append(ft.Text(value=message, color="red"))
        page.update()

    toolbar_buttons = [
        ft.IconButton(icon=ft.icons.PLAY_ARROW, tooltip="Solve matrix", on_click=solve_matrix),
        ft.IconButton(icon=ft.icons.CLEANING_SERVICES, tooltip="Clear matrix", on_click=clear_matrix),
    ]

    toolbar = ft.Row([*toolbar_buttons, theme_icon], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, expand=True)
    page.add(toolbar)

    left_section = ft.Container(content=matrix_container, padding=20, expand=True)
    content_section = ft.Row([left_section, ft.VerticalDivider(), right_top_section, right_bottom_section], expand=True,
                             spacing=10)
    page.add(content_section)

ft.app(target=main)