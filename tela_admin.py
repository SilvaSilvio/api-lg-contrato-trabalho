import flet as ft
from database import Database
from typing import List, Dict
import sqlite3

class TelaAdmin:
    def __init__(self):
        self.db = Database()
    
    def main(self, page: ft.Page):
        page.title = "Administração do Sistema"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        page.window.width = 1200
        page.window.height = 800
        page.bgcolor = ft.colors.BLUE_GREY_50
        
        # Definir tema personalizado
        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.colors.BLUE,
                secondary=ft.colors.BLUE_ACCENT,
                surface=ft.colors.WHITE,
                background=ft.colors.BLUE_GREY_50,
                error=ft.colors.RED_400,
            ),
            visual_density=ft.VisualDensity.COMFORTABLE,
        )
        
        # Componentes da tela
        titulo = ft.Text(
            "Administração do Sistema",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLUE
        )
        
        # Tabs para diferentes seções
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Usuários",
                    icon=ft.icons.PEOPLE,
                    content=self.criar_tab_usuarios(page)
                ),
                ft.Tab(
                    text="Empresas",
                    icon=ft.icons.BUSINESS,
                    content=self.criar_tab_empresas(page)
                )
            ]
        )
        
        # Layout principal
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        titulo,
                        ft.Container(height=20),
                        tabs
                    ],
                    spacing=0
                ),
                padding=20,
                bgcolor=ft.colors.WHITE,
                border_radius=8,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color=ft.colors.BLUE_GREY_100,
                    offset=ft.Offset(0, 3)
                )
            )
        )
    
    def criar_tab_usuarios(self, page: ft.Page):
        # Campos do formulário
        username = ft.TextField(
            label="Nome de usuário",
            width=300,
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        senha = ft.TextField(
            label="Senha",
            width=300,
            password=True,
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        nome = ft.TextField(
            label="Nome completo",
            width=300,
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        # Lista de empresas para seleção
        empresas = ft.Column(
            [],
            scroll=ft.ScrollMode.AUTO,
            height=200
        )
        
        def atualizar_lista_empresas():
            empresas.controls.clear()
            for emp in self.db.get_todas_empresas():
                empresas.controls.append(
                    ft.Checkbox(
                        label=f"{emp['codigo']} - {emp['nome']}",
                        value=False
                    )
                )
            page.update()
        
        def adicionar_usuario(e):
            # Coletar empresas selecionadas
            empresas_selecionadas = [
                cb.label.split(" - ")[0]
                for cb in empresas.controls
                if cb.value
            ]
            
            if self.db.adicionar_usuario(
                username.value,
                senha.value,
                nome.value,
                empresas_selecionadas
            ):
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Usuário adicionado com sucesso!"),
                        bgcolor=ft.colors.GREEN
                    )
                )
                # Limpar campos
                username.value = ""
                senha.value = ""
                nome.value = ""
                for cb in empresas.controls:
                    cb.value = False
            else:
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Erro ao adicionar usuário. Verifique se o nome de usuário já existe."),
                        bgcolor=ft.colors.RED_400
                    )
                )
            page.update()
        
        # Botão de adicionar
        btn_adicionar = ft.ElevatedButton(
            "Adicionar Usuário",
            icon=ft.icons.ADD,
            on_click=adicionar_usuario,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
            ),
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )
        
        # Atualizar lista de empresas
        atualizar_lista_empresas()
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Adicionar Novo Usuário",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    username,
                                    ft.Container(height=10),
                                    senha,
                                    ft.Container(height=10),
                                    nome
                                ],
                                spacing=0
                            ),
                            ft.Container(width=20),
                            ft.Column(
                                [
                                    ft.Text(
                                        "Empresas Permitidas",
                                        size=16,
                                        weight=ft.FontWeight.W_500
                                    ),
                                    ft.Container(height=10),
                                    empresas
                                ],
                                spacing=0
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Container(height=20),
                    btn_adicionar
                ],
                spacing=0
            ),
            padding=20
        )
    
    def criar_tab_empresas(self, page: ft.Page):
        # Campos do formulário
        codigo = ft.TextField(
            label="Código",
            width=200,
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        nome = ft.TextField(
            label="Nome",
            width=400,
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        def adicionar_empresa(e):
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute('''
                        INSERT INTO empresas (codigo, nome)
                        VALUES (?, ?)
                    ''', (codigo.value, nome.value))
                    conn.commit()
                    
                    page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text("Empresa adicionada com sucesso!"),
                            bgcolor=ft.colors.GREEN
                        )
                    )
                    # Limpar campos
                    codigo.value = ""
                    nome.value = ""
                    # Atualizar lista
                    atualizar_lista_empresas()
                except sqlite3.IntegrityError:
                    page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text("Erro ao adicionar empresa. Verifique se o código já existe."),
                            bgcolor=ft.colors.RED_400
                        )
                    )
            page.update()
        
        # Lista de empresas
        lista_empresas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nome", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ações", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.BLUE_GREY_200),
            border_radius=8,
            vertical_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_200),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_200),
            heading_row_color=ft.colors.BLUE_50,
            heading_row_height=50,
            data_row_color=ft.colors.WHITE,
            data_row_min_height=40,
            data_row_max_height=40,
            column_spacing=20,
            expand=True
        )
        
        def atualizar_lista_empresas():
            lista_empresas.rows.clear()
            for emp in self.db.get_todas_empresas():
                lista_empresas.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(emp["codigo"])),
                            ft.DataCell(ft.Text(emp["nome"])),
                            ft.DataCell(
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.icons.EDIT,
                                            icon_color=ft.colors.BLUE,
                                            tooltip="Editar",
                                            on_click=lambda e, c=emp["codigo"]: editar_empresa(c)
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE,
                                            icon_color=ft.colors.RED_400,
                                            tooltip="Excluir",
                                            on_click=lambda e, c=emp["codigo"]: excluir_empresa(c)
                                        )
                                    ]
                                )
                            )
                        ]
                    )
                )
            page.update()
        
        def editar_empresa(codigo: str):
            # Implementar edição de empresa
            pass
        
        def excluir_empresa(codigo: str):
            # Implementar exclusão de empresa
            pass
        
        # Botão de adicionar
        btn_adicionar = ft.ElevatedButton(
            "Adicionar Empresa",
            icon=ft.icons.ADD,
            on_click=adicionar_empresa,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
            ),
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )
        
        # Atualizar lista de empresas
        atualizar_lista_empresas()
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Gerenciar Empresas",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        [
                            codigo,
                            ft.Container(width=20),
                            nome,
                            ft.Container(expand=True),
                            btn_adicionar
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Container(height=20),
                    lista_empresas
                ],
                spacing=0
            ),
            padding=20
        )

if __name__ == "__main__":
    def main(page: ft.Page):
        tela_admin = TelaAdmin()
        tela_admin.main(page)
    
    ft.app(target=main) 