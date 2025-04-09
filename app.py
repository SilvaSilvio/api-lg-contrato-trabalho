import flet as ft
import asyncio
from datetime import datetime

from controllers.empresa_controller import EmpresaController
from controllers.usuario_controller import UsuarioController
from controllers.operador_controller import OperadorController
from controllers.contrato_controller import ContratoController

class TelaContratos:
    def __init__(self):
        # Inicializar controladores
        self.empresa_controller = EmpresaController()
        self.usuario_controller = UsuarioController()
        self.operador_controller = OperadorController()
        self.contrato_controller = ContratoController()
        
        # Referências para a interface
        self.page = None
        self.tabela_empresas = None
        self.tabela_usuarios = None
        self.tabela_operadores = None
        self.lista_empresas_usuarios = None
        
    def main(self, page: ft.Page):
        self.page = page
        page.title = "Sistema de Contratos de Trabalho"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.window.width = 1200
        page.window.height = 800
        page.bgcolor = ft.colors.BLUE_GREY_50
        page.scroll = ft.ScrollMode.AUTO
        
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
        
        # Componentes da tela de login
        usuario = ft.TextField(
            label="Usuário",
            width=300,
            autofocus=True,
            border_radius=8,
            prefix_icon=ft.icons.PERSON_OUTLINE,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        senha = ft.TextField(
            label="Senha",
            width=300,
            password=True,
            border_radius=8,
            prefix_icon=ft.icons.LOCK_OUTLINE,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        erro_login = ft.Text(
            color=ft.colors.RED,
            visible=False,
            text_align=ft.TextAlign.CENTER
        )
        
        # Componentes da tela principal
        info_usuario = ft.Text(
            size=16,
            color=ft.colors.BLUE
        )
        
        # Tabs para diferentes seções
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            visible=False,
            tabs=[
                ft.Tab(
                    text="Contratos",
                    icon=ft.icons.DESCRIPTION,
                    content=self.criar_tab_contratos(page)
                ),
                ft.Tab(
                    text="Usuários",
                    icon=ft.icons.PEOPLE,
                    content=self.criar_tab_usuarios(page)
                ),
                ft.Tab(
                    text="Empresas",
                    icon=ft.icons.BUSINESS,
                    content=self.criar_tab_empresas(page)
                ),
                ft.Tab(
                    text="Operadores",
                    icon=ft.icons.SUPPORT_AGENT,
                    content=self.criar_tab_operadores(page)
                )
            ]
        )
        
        # Campos de busca
        mes = ft.Dropdown(
            options=[
                ft.dropdown.Option(str(i), f"{i:02d}") for i in range(1, 13)
            ],
            width=120,
            value=str(datetime.now().month),
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        ano = ft.TextField(
            value=str(datetime.now().year),
            width=120,
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        # Dropdown de empresas
        empresa_dropdown = ft.Dropdown(
            width=300,
            options=[],
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        # Dropdown de operadores
        operador_dropdown = ft.Dropdown(
            width=300,
            options=[],
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.WHITE,
            label="Operador"
        )
        
        # Tabela de dados
        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Matrícula", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nome", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("CPF", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Data Admissão", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cargo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Departamento", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Situação", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Empresa", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.BLUE_GREY_200),
            vertical_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_200),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_200),
            heading_row_color=ft.colors.BLUE_50,
            heading_row_height=50,
            data_row_color=ft.colors.WHITE,
            data_row_min_height=40,
            data_row_max_height=40,
            column_spacing=20,
            width=1100,
            horizontal_margin=10
        )
        
        # Container para a tabela com scroll
        table_container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "Resultados da Busca",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.BLUE
                            ),
                            ft.Container(expand=True),
                            ft.Text(
                                "Total de registros: 0",
                                size=14,
                                color=ft.colors.BLUE_GREY_700
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Column(
                            [data_table],
                            scroll=ft.ScrollMode.AUTO,
                            spacing=0,
                            height=400,
                        ),
                        border=ft.border.all(1, ft.colors.BLUE_GREY_200),
                        border_radius=8,
                        padding=10
                    )
                ]
            ),
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=8,
            expand=True,
            margin=ft.margin.symmetric(horizontal=20, vertical=10)
        )
        
        # Indicador de carregamento
        self.progress = ft.ProgressBar(
            visible=False,
            color=ft.colors.BLUE,
            bgcolor=ft.colors.BLUE_GREY_100
        )
        
        # Container principal que vai alternar entre login e conteúdo
        self.main_container = ft.Container(expand=True)
        
        def atualizar_empresas():
            """Atualiza o dropdown de empresas com base nas permissões do usuário."""
            empresas = self.empresa_controller.get_todas_empresas()
            empresa_dropdown.options = [
                ft.dropdown.Option("", "Todas as Empresas")
            ] + [
                ft.dropdown.Option(emp["codigo"], f"{emp['codigo']} - {emp['nome']}")
                for emp in empresas
            ]
            empresa_dropdown.value = ""
            page.update()
        
        def atualizar_operadores():
            """Atualiza o dropdown de operadores."""
            operadores = self.operador_controller.get_todos_operadores()
            operador_dropdown.options = [
                ft.dropdown.Option("", "Usar credenciais padrão")
            ] + [
                ft.dropdown.Option(operador["email"], f"{operador['email']} ({'Ativo' if operador['ativo'] else 'Inativo'})")
                for operador in operadores
            ]
            operador_dropdown.value = ""
            page.update()
        
        def fazer_login(e):
            """Realiza o login do usuário."""
            if self.usuario_controller.verificar_login(usuario.value, senha.value):
                # Login bem sucedido
                erro_login.visible = False
                info_usuario.value = f"Usuário: {usuario.value}"
                
                # Verificar se é admin
                usuario_data = self.usuario_controller.get_usuario(usuario.value)
                is_admin = usuario_data and usuario_data["is_admin"]
                
                # Mostrar tela principal
                self.main_container.content = ft.Column(
                    [
                        header,
                        tabs,
                        filtros_card,
                        self.progress,
                        table_container
                    ],
                    expand=True,
                    spacing=0
                )
                
                # Atualizar visibilidade das tabs
                tabs.visible = is_admin
                if is_admin:
                    tabs.selected_index = 0
                
                # Atualizar área administrativa
                self.atualizar_area_administrativa()
            else:
                # Login falhou
                erro_login.value = "Usuário ou senha inválidos"
                erro_login.visible = True
            
            self.page.update()
        
        def fazer_logout(e):
            """Realiza o logout do usuário."""
            usuario.value = ""
            senha.value = ""
            empresa_dropdown.options = []
            tabs.visible = False
            
            # Voltar para tela de login
            self.main_container.content = ft.Column(
                [login_card],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
            self.page.update()
        
        def buscar_contratos(self, e):
            """Busca contratos com base nos filtros selecionados."""
            try:
                # Validar mês e ano
                if not mes.value or not ano.value:
                    self.page.show_snack_bar(
                        ft.SnackBar(content=ft.Text("Por favor, preencha mês e ano"))
                    )
                    return

                # Mostrar progresso
                self.progress.visible = True
                self.page.update()

                # Limpar tabela atual
                data_table.rows.clear()

                # Buscar contratos
                contratos, mensagem = self.contrato_controller.buscar_contratos(
                    mes.value,
                    ano.value,
                    empresa_dropdown.value,
                    operador_dropdown.value
                )
                
                # Preencher tabela
                for contrato in contratos:
                    data_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(contrato['matricula'])),
                                ft.DataCell(ft.Text(contrato['nome'])),
                                ft.DataCell(ft.Text(contrato['cpf'])),
                                ft.DataCell(ft.Text(contrato['data_admissao'])),
                                ft.DataCell(ft.Text(contrato['cargo'])),
                                ft.DataCell(ft.Text(contrato['departamento'])),
                                ft.DataCell(
                                    ft.Container(
                                        content=ft.Text(
                                            contrato['situacao'],
                                            color=ft.colors.WHITE,
                                            text_align=ft.TextAlign.CENTER
                                        ),
                                        bgcolor=ft.colors.GREEN if contrato['situacao'] == 'Ativo' else ft.colors.RED_400,
                                        border_radius=15,
                                        padding=ft.padding.symmetric(horizontal=10, vertical=5)
                                    )
                                ),
                                ft.DataCell(ft.Text(str(contrato.get('empresa', {}).get('Codigo', '')))),
                            ]
                        )
                    )
                
                # Atualizar contador de registros
                total_registros = len(contratos)
                table_container.content.controls[0].controls[1].value = f"Total de registros: {total_registros}"
                
                # Esconder progresso
                self.progress.visible = False
                self.page.update()
            except Exception as e:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Erro ao buscar contratos: {e}"),
                        bgcolor=ft.colors.RED_400,
                        action="OK"
                    )
                )
        
        # Botões
        btn_login = ft.ElevatedButton(
            "Entrar",
            icon=ft.icons.LOGIN,
            on_click=fazer_login,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=30, vertical=15),
            ),
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )
        
        btn_logout = ft.IconButton(
            icon=ft.icons.LOGOUT,
            icon_color=ft.colors.RED_400,
            tooltip="Sair",
            on_click=fazer_logout
        )
        
        btn_buscar = ft.ElevatedButton(
            "Buscar Contratos",
            icon=ft.icons.SEARCH,
            on_click=buscar_contratos,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
            ),
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )
        
        # Tela de login
        login_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(
                                name=ft.icons.PERSON,
                                size=60,
                                color=ft.colors.BLUE
                            ),
                            alignment=ft.alignment.center,
                            padding=20
                        ),
                        ft.Text(
                            "Login do Sistema",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.BLUE,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Container(height=20),
                        usuario,
                        ft.Container(height=10),
                        senha,
                        ft.Container(height=10),
                        erro_login,
                        ft.Container(height=20),
                        btn_login
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0
                ),
                padding=30,
                width=400
            ),
            elevation=5,
            margin=ft.margin.only(top=100)
        )
        
        # Componentes da tela principal
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        name=ft.icons.DESCRIPTION,
                        size=40,
                        color=ft.colors.BLUE
                    ),
                    ft.Text(
                        "Consulta de Contratos de Trabalho",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE
                    ),
                    ft.Container(expand=True),
                    info_usuario,
                    btn_logout
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=ft.colors.WHITE,
            border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.BLUE_GREY_100,
                offset=ft.Offset(0, 3)
            )
        )
        
        # Painel de filtros
        filtros_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Filtros de Busca",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.BLUE
                        ),
                        ft.Container(height=15),
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text("Mês", size=14, weight=ft.FontWeight.W_500),
                                            mes
                                        ],
                                        spacing=5
                                    ),
                                    padding=10,
                                    bgcolor=ft.colors.BLUE_GREY_50,
                                    border_radius=8
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text("Ano", size=14, weight=ft.FontWeight.W_500),
                                            ano
                                        ],
                                        spacing=5
                                    ),
                                    padding=10,
                                    bgcolor=ft.colors.BLUE_GREY_50,
                                    border_radius=8
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text("Empresa", size=14, weight=ft.FontWeight.W_500),
                                            empresa_dropdown
                                        ],
                                        spacing=5
                                    ),
                                    padding=10,
                                    bgcolor=ft.colors.BLUE_GREY_50,
                                    border_radius=8
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text("Operador", size=14, weight=ft.FontWeight.W_500),
                                            operador_dropdown
                                        ],
                                        spacing=5
                                    ),
                                    padding=10,
                                    bgcolor=ft.colors.BLUE_GREY_50,
                                    border_radius=8
                                ),
                                ft.Container(expand=True),
                                btn_buscar
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        )
                    ],
                    spacing=10
                ),
                padding=20
            ),
            elevation=2,
            margin=ft.margin.symmetric(horizontal=20, vertical=10)
        )
        
        # Inicialmente mostrar tela de login
        self.main_container.content = ft.Column(
            [login_card],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        # Adicionar container principal à página
        page.add(self.main_container)
    
    def criar_tab_usuarios(self, page):
        # Campos para cadastro/edição de usuários
        username = ft.TextField(
            label="Nome de Usuário",
            width=300,
            border_radius=8,
            prefix_icon=ft.icons.PERSON_OUTLINE,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        nome = ft.TextField(
            label="Nome Completo",
            width=300,
            border_radius=8,
            prefix_icon=ft.icons.BADGE,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        senha = ft.TextField(
            label="Senha",
            width=300,
            password=True,
            border_radius=8,
            prefix_icon=ft.icons.LOCK_OUTLINE,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        is_admin = ft.Checkbox(
            label="Administrador",
            value=False
        )
        
        # Lista de empresas para seleção
        empresas_checkboxes = ft.Column(
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
            height=200
        )
        
        # Botões
        btn_adicionar = ft.ElevatedButton(
            "Adicionar Usuário",
            icon=ft.icons.PERSON_ADD,
            on_click=self.adicionar_usuario,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
            ),
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )
        
        btn_salvar = ft.ElevatedButton(
            "Salvar Alterações",
            icon=ft.icons.SAVE,
            on_click=self.salvar_usuario,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
            ),
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE,
            visible=False
        )
        
        btn_cancelar = ft.OutlinedButton(
            "Cancelar",
            icon=ft.icons.CANCEL,
            on_click=self.cancelar_edicao_usuario,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
            ),
            visible=False
        )
        
        # Tabela de usuários
        self.tabela_usuarios = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Usuário", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nome", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Empresas", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ações", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.BLUE_GREY_200),
            vertical_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_200),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_200),
            heading_row_color=ft.colors.BLUE_50,
            heading_row_height=50,
            data_row_color=ft.colors.WHITE,
            data_row_min_height=40,
            data_row_max_height=40,
            column_spacing=20,
            width=1100,
            horizontal_margin=10
        )
        
        # Container para a tabela com scroll
        table_container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "Usuários Cadastrados",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.BLUE
                            ),
                            ft.Container(expand=True),
                            ft.Text(
                                "Total de usuários: 0",
                                size=14,
                                color=ft.colors.BLUE_GREY_700
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Column(
                            [self.tabela_usuarios],
                            scroll=ft.ScrollMode.AUTO,
                            spacing=0,
                            height=400,
                        ),
                        border=ft.border.all(1, ft.colors.BLUE_GREY_200),
                        border_radius=8,
                        padding=10
                    )
                ]
            ),
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=8,
            expand=True,
            margin=ft.margin.symmetric(horizontal=20, vertical=10)
        )
        
        # Formulário de cadastro/edição
        form_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Cadastro de Usuário",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE
                    ),
                    ft.Container(height=15),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    username,
                                    ft.Container(height=10),
                                    nome,
                                    ft.Container(height=10),
                                    senha,
                                    ft.Container(height=10),
                                    is_admin,
                                ],
                                spacing=5
                            ),
                            ft.Container(width=20),
                            ft.Column(
                                [
                                    ft.Text(
                                        "Empresas",
                                        size=14,
                                        weight=ft.FontWeight.W_500
                                    ),
                                    ft.Container(height=5),
                                    ft.Container(
                                        content=empresas_checkboxes,
                                        border=ft.border.all(1, ft.colors.BLUE_GREY_200),
                                        border_radius=8,
                                        padding=10,
                                        bgcolor=ft.colors.WHITE,
                                        width=300,
                                        height=200
                                    )
                                ],
                                spacing=5
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        [
                            btn_adicionar,
                            ft.Container(width=10),
                            btn_salvar,
                            ft.Container(width=10),
                            btn_cancelar
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    )
                ],
                spacing=10
            ),
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=8,
            margin=ft.margin.symmetric(horizontal=20, vertical=10)
        )
        
        # Armazenar referências para uso posterior
        self.username_field = username
        self.nome_field = nome
        self.senha_field = senha
        self.is_admin_checkbox = is_admin
        self.empresas_checkboxes = empresas_checkboxes
        self.btn_adicionar_usuario = btn_adicionar
        self.btn_salvar_usuario = btn_salvar
        self.btn_cancelar_usuario = btn_cancelar
        self.usuario_editando = None
        
        # Função para atualizar a lista de empresas no formulário
        def atualizar_empresas_formulario():
            empresas = self.empresa_controller.get_todas_empresas()
            self.empresas_checkboxes.controls.clear()
            
            for emp in empresas:
                self.empresas_checkboxes.controls.append(
                    ft.Checkbox(
                        label=f"{emp['codigo']} - {emp['nome']}",
                        value=False,
                        data=emp['codigo']
                    )
                )
            
            page.update()
        
        # Retornar o container com o formulário e a tabela
        return ft.Column(
            [
                form_container,
                table_container
            ],
            spacing=0,
            expand=True
        )
    
    def criar_tab_empresas(self, page):
        # Campos para cadastro/edição de empresas
        codigo = ft.TextField(
            label="Código",
            width=300,
            border_radius=8,
            prefix_icon=ft.icons.NUMBERS,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        nome = ft.TextField(
            label="Nome",
            width=300,
            border_radius=8,
            prefix_icon=ft.icons.BUSINESS,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        tenet_id = ft.TextField(
            label="Tenet ID",
            width=300,
            border_radius=8,
            prefix_icon=ft.icons.FINGERPRINT,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        ambiente = ft.TextField(
            label="Ambiente",
            width=300,
            border_radius=8,
            prefix_icon=ft.icons.SETTINGS,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        # Botões
        btn_adicionar = ft.ElevatedButton(
            "Adicionar Empresa",
            icon=ft.icons.BUSINESS_CENTER,
            on_click=self.adicionar_empresa,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
            ),
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )
        
        btn_salvar = ft.ElevatedButton(
            "Salvar Alterações",
            icon=ft.icons.SAVE,
            on_click=self.salvar_empresa,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
            ),
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE,
            visible=False
        )
        
        btn_cancelar = ft.OutlinedButton(
            "Cancelar",
            icon=ft.icons.CANCEL,
            on_click=self.cancelar_edicao_empresa,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
            ),
            visible=False
        )
        
        # Tabela de empresas
        self.tabela_empresas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nome", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tenet ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ambiente", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ações", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.BLUE_GREY_200),
            vertical_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_200),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_200),
            heading_row_color=ft.colors.BLUE_50,
            heading_row_height=50,
            data_row_color=ft.colors.WHITE,
            data_row_min_height=40,
            data_row_max_height=40,
            column_spacing=20,
            width=1100,
            horizontal_margin=10
        )
        
        # Container para a tabela com scroll
        table_container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "Empresas Cadastradas",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.BLUE
                            ),
                            ft.Container(expand=True),
                            ft.Text(
                                "Total de empresas: 0",
                                size=14,
                                color=ft.colors.BLUE_GREY_700
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Column(
                            [self.tabela_empresas],
                            scroll=ft.ScrollMode.AUTO,
                            spacing=0,
                            height=400,
                        ),
                        border=ft.border.all(1, ft.colors.BLUE_GREY_200),
                        border_radius=8,
                        padding=10
                    )
                ]
            ),
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=8,
            expand=True,
            margin=ft.margin.symmetric(horizontal=20, vertical=10)
        )
        
        # Formulário de cadastro/edição
        form_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Cadastro de Empresa",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE
                    ),
                    ft.Container(height=15),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    codigo,
                                    ft.Container(height=10),
                                    nome,
                                    ft.Container(height=10),
                                    tenet_id,
                                    ft.Container(height=10),
                                    ambiente,
                                ],
                                spacing=5
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        [
                            btn_adicionar,
                            ft.Container(width=10),
                            btn_salvar,
                            ft.Container(width=10),
                            btn_cancelar
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    )
                ],
                spacing=10
            ),
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=8,
            margin=ft.margin.symmetric(horizontal=20, vertical=10)
        )
        
        # Armazenar referências para uso posterior
        self.codigo_field = codigo
        self.nome_empresa_field = nome
        self.tenet_id_field = tenet_id
        self.ambiente_field = ambiente
        self.btn_adicionar_empresa = btn_adicionar
        self.btn_salvar_empresa = btn_salvar
        self.btn_cancelar_empresa = btn_cancelar
        self.empresa_editando = None
        
        # Retornar o container com o formulário e a tabela
        return ft.Column(
            [
                form_container,
                table_container
            ],
            spacing=0,
            expand=True
        )
    
    def criar_tab_operadores(self, page):
        # Campos para cadastro/edição de operadores
        email = ft.TextField(
            label="Email",
            width=300,
            border_radius=8,
            prefix_icon=ft.icons.EMAIL,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        senha = ft.TextField(
            label="Senha",
            width=300,
            border_radius=8,
            prefix_icon=ft.icons.LOCK,
            filled=True,
            bgcolor=ft.colors.WHITE,
            password=True,
            can_reveal_password=True
        )
        
        ativo = ft.Checkbox(
            label="Ativo",
            value=True,
            fill_color=ft.colors.BLUE
        )
        
        # Botões
        btn_adicionar = ft.ElevatedButton(
            "Adicionar Operador",
            icon=ft.icons.PERSON_ADD,
            on_click=self.adicionar_operador,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
            ),
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )
        
        btn_salvar = ft.ElevatedButton(
            "Salvar Alterações",
            icon=ft.icons.SAVE,
            on_click=self.salvar_operador,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
            ),
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE,
            visible=False
        )
        
        btn_cancelar = ft.OutlinedButton(
            "Cancelar",
            icon=ft.icons.CANCEL,
            on_click=self.cancelar_edicao_operador,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
            ),
            visible=False
        )
        
        # Tabela de operadores
        self.tabela_operadores = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Email", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ações", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.BLUE_GREY_200),
            vertical_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_200),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_200),
            heading_row_color=ft.colors.BLUE_50,
            heading_row_height=50,
            data_row_color=ft.colors.WHITE,
            data_row_min_height=40,
            data_row_max_height=40,
            column_spacing=20,
            width=1100,
            horizontal_margin=10
        )
        
        # Container para a tabela com scroll
        table_container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "Operadores Cadastrados",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.BLUE
                            ),
                            ft.Container(expand=True),
                            ft.Text(
                                "Total de operadores: 0",
                                size=14,
                                color=ft.colors.BLUE_GREY_700
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Column(
                            [self.tabela_operadores],
                            scroll=ft.ScrollMode.AUTO,
                            spacing=0,
                            height=400,
                        ),
                        border=ft.border.all(1, ft.colors.BLUE_GREY_200),
                        border_radius=8,
                        padding=10
                    )
                ]
            ),
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=8,
            expand=True,
            margin=ft.margin.symmetric(horizontal=20, vertical=10)
        )
        
        # Formulário de cadastro/edição
        form_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Cadastro de Operador",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE
                    ),
                    ft.Container(height=15),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    email,
                                    ft.Container(height=10),
                                    senha,
                                    ft.Container(height=10),
                                    ativo,
                                ],
                                spacing=5
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        [
                            btn_adicionar,
                            ft.Container(width=10),
                            btn_salvar,
                            ft.Container(width=10),
                            btn_cancelar
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    )
                ],
                spacing=10
            ),
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=8,
            margin=ft.margin.symmetric(horizontal=20, vertical=10)
        )
        
        # Armazenar referências para uso posterior
        self.email_operador_field = email
        self.senha_operador_field = senha
        self.ativo_operador_checkbox = ativo
        self.btn_adicionar_operador = btn_adicionar
        self.btn_salvar_operador = btn_salvar
        self.btn_cancelar_operador = btn_cancelar
        self.operador_editando = None
        
        # Retornar o container com o formulário e a tabela
        return ft.Column(
            [
                form_container,
                table_container
            ],
            spacing=0,
            expand=True
        )
    
    def criar_tab_contratos(self, page):
        # Implementação da tab de contratos
        # Esta função será implementada posteriormente
        return ft.Container(content=ft.Text("Tab de Contratos"))
    
    def atualizar_area_administrativa(self):
        """Atualiza todas as listas da área administrativa."""
        try:
            # Atualizar listas uma por uma, capturando erros individuais
            try:
                self.atualizar_lista_empresas()
            except Exception as e:
                print(f"Erro ao atualizar lista de empresas: {str(e)}")
                
            try:
                self.atualizar_lista_usuarios()
            except Exception as e:
                print(f"Erro ao atualizar lista de usuários: {str(e)}")
                
            try:
                self.atualizar_lista_operadores()
            except Exception as e:
                print(f"Erro ao atualizar lista de operadores: {str(e)}")
            
            # Atualizar a lista de empresas no formulário de usuários
            if hasattr(self, 'empresas_checkboxes') and self.empresas_checkboxes:
                try:
                    empresas = self.empresa_controller.get_todas_empresas()
                    self.empresas_checkboxes.controls.clear()
                    
                    for emp in empresas:
                        self.empresas_checkboxes.controls.append(
                            ft.Checkbox(
                                label=f"{emp['codigo']} - {emp['nome']}",
                                value=False,
                                data=emp['codigo']
                            )
                        )
                except Exception as e:
                    print(f"Erro ao atualizar checkboxes de empresas: {str(e)}")
            
            # Verificar se o main_container existe antes de atualizar a página
            if hasattr(self, 'main_container') and self.main_container:
                try:
                    # Forçar uma reconstrução do conteúdo
                    if self.main_container.content:
                        current_content = self.main_container.content
                        self.main_container.content = None
                        self.page.update()
                        self.main_container.content = current_content
                        
                    # Forçar uma reconstrução completa da interface
                    self.page.clean()
                    self.page.add(self.main_container)
                except Exception as e:
                    print(f"Erro ao reconstruir main_container: {str(e)}")
            
            # Atualização final
            self.page.update()
        except Exception as e:
            print(f"Erro ao atualizar área administrativa: {str(e)}")
            # Mostra um snackbar de erro em último caso
            try:
                error_snack = ft.SnackBar(
                    content=ft.Text(f"Erro ao atualizar interface: {str(e)}"),
                    bgcolor=ft.colors.RED_400,
                    action="OK"
                )
                self.page.overlay.append(error_snack)
                error_snack.open = True
                self.page.update()
            except:
                # Se nem o snackbar puder ser mostrado, pelo menos registramos o erro
                print("Erro crítico ao atualizar interface")
    
    def atualizar_lista_empresas(self):
        """Atualiza a lista de empresas na tabela."""
        if hasattr(self, 'tabela_empresas') and self.tabela_empresas:
            # Limpar a tabela
            self.tabela_empresas.rows.clear()
            
            # Obter todas as empresas
            empresas = self.empresa_controller.get_todas_empresas()
            
            # Adicionar cada empresa à tabela
            for emp in empresas:
                self.tabela_empresas.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(emp["codigo"])),
                            ft.DataCell(ft.Text(emp["nome"])),
                            ft.DataCell(ft.Text(emp["tenetID"])),
                            ft.DataCell(ft.Text(emp["ambiente"])),
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        icon_color=ft.colors.BLUE,
                                        tooltip="Editar",
                                        data=emp["codigo"],
                                        on_click=self.editar_empresa
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        icon_color=ft.colors.RED_400,
                                        tooltip="Excluir",
                                        data=emp["codigo"],
                                        on_click=self.excluir_empresa
                                    )
                                ])
                            )
                        ]
                    )
                )
            
            # Atualizar a página para garantir que as alterações sejam exibidas
            self.page.update()
    
    def atualizar_lista_usuarios(self):
        """Atualiza a lista de usuários na tabela."""
        if hasattr(self, 'tabela_usuarios') and self.tabela_usuarios:
            self.tabela_usuarios.rows.clear()
            for user in self.usuario_controller.get_todos_usuarios():
                # Obter empresas do usuário
                empresas_usuario = self.usuario_controller.get_empresas_usuario(user["username"])
                empresas_str = ", ".join([f"{emp['codigo']} - {emp['nome']}" for emp in empresas_usuario])
                
                # Criar botões de ação
                btn_editar = ft.IconButton(
                    icon=ft.icons.EDIT,
                    icon_color=ft.colors.BLUE,
                    tooltip="Editar",
                    data=user["username"],
                    on_click=self.editar_usuario
                )
                
                btn_excluir = ft.IconButton(
                    icon=ft.icons.DELETE,
                    icon_color=ft.colors.RED_400,
                    tooltip="Excluir",
                    data=user["username"],
                    on_click=self.excluir_usuario
                )
                
                self.tabela_usuarios.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(user["username"])),
                            ft.DataCell(ft.Text(user["nome"])),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(
                                        "Administrador" if user["is_admin"] else "Usuário",
                                        color=ft.colors.WHITE,
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                    bgcolor=ft.colors.BLUE if user["is_admin"] else ft.colors.GREEN,
                                    border_radius=15,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5)
                                )
                            ),
                            ft.DataCell(ft.Text(empresas_str)),
                            ft.DataCell(
                                ft.Row([btn_editar, btn_excluir])
                            )
                        ]
                    )
                )
            self.page.update()
    
    def atualizar_lista_operadores(self):
        """Atualiza a lista de operadores na interface."""
        if hasattr(self, 'tabela_operadores') and self.tabela_operadores:
            try:
                # Limpar a tabela atual
                self.tabela_operadores.rows.clear()
                
                # Obter todos os operadores
                operadores = self.operador_controller.get_todos_operadores()
                
                # Adicionar cada operador à tabela
                for operador in operadores:
                    # Criar botões de ação
                    btn_editar = ft.IconButton(
                        icon=ft.icons.EDIT,
                        icon_color=ft.colors.BLUE,
                        tooltip="Editar",
                        data=operador['email'],
                        on_click=self.editar_operador
                    )
                    
                    btn_excluir = ft.IconButton(
                        icon=ft.icons.DELETE,
                        icon_color=ft.colors.RED_400,
                        tooltip="Excluir",
                        data=operador['email'],
                        on_click=self.excluir_operador
                    )
                    
                    # Adicionar linha na tabela
                    self.tabela_operadores.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(operador['email'])),
                                ft.DataCell(ft.Text("Ativo" if operador['ativo'] else "Inativo")),
                                ft.DataCell(
                                    ft.Row(
                                        [btn_editar, btn_excluir],
                                        spacing=0
                                    )
                                )
                            ]
                        )
                    )
                
                # Atualizar a página para garantir que as alterações sejam exibidas
                self.page.update()
            except Exception as e:
                print(f"Erro ao atualizar lista de operadores: {str(e)}")
                # Cria um snackbar de erro
                error_snack = ft.SnackBar(
                    content=ft.Text(f"Erro ao atualizar lista de operadores: {str(e)}"),
                    bgcolor=ft.colors.RED_400,
                    action="OK"
                )
                self.page.overlay.append(error_snack)
                error_snack.open = True
                self.page.update()
    
    def editar_empresa(self, e):
        """Preenche o formulário com os dados da empresa para edição."""
        # Obter dados da empresa
        empresa = self.empresa_controller.get_empresa(e.control.data)
        if not empresa:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Empresa não encontrada"),
                    bgcolor=ft.colors.RED_400
                )
            )
            return
        
        # Preencher campos
        self.codigo_field.value = empresa["codigo"]
        self.nome_empresa_field.value = empresa["nome"]
        self.tenet_id_field.value = empresa["tenetID"]
        self.ambiente_field.value = empresa["ambiente"]
        
        # Armazenar referência da empresa sendo editada
        self.empresa_editando = e.control.data
        
        # Alterar visibilidade dos botões
        self.btn_adicionar_empresa.visible = False
        self.btn_salvar_empresa.visible = True
        self.btn_cancelar_empresa.visible = True
        
        self.page.update()
    
    def excluir_empresa(self, e):
        """Exclui uma empresa do sistema."""
        try:
            codigo = e.control.data
            if not codigo:
                error_snack = ft.SnackBar(
                    content=ft.Text("Não foi possível identificar o código da empresa"),
                    bgcolor=ft.colors.RED_400
                )
                self.page.overlay.append(error_snack)
                error_snack.open = True
                self.page.update()
                return
                
            # Confirmar exclusão
            dlg = ft.AlertDialog(
                modal=True,  # Garantir que o diálogo seja modal
                title=ft.Text("Confirmar Exclusão"),
                content=ft.Text(f"Tem certeza que deseja excluir a empresa {codigo}?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: self.fechar_dialogo(e, dlg)),
                    ft.TextButton(
                        "Excluir", 
                        on_click=lambda e: self.confirmar_exclusao_empresa(e, dlg, codigo),
                        style=ft.ButtonStyle(color=ft.colors.RED_400)
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            # Adicionar o diálogo ao overlay e abri-lo
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()
        except Exception as e:
            print(f"Erro ao exibir diálogo de exclusão: {str(e)}")
            error_snack = ft.SnackBar(
                content=ft.Text(f"Erro ao preparar exclusão: {str(e)}"),
                bgcolor=ft.colors.RED_400
            )
            self.page.overlay.append(error_snack)
            error_snack.open = True
            self.page.update()
    
    def fechar_dialogo(self, e, dlg):
        """Fecha um diálogo de forma segura."""
        try:
            # Verificar se o diálogo existe e está no overlay
            if dlg and dlg in self.page.overlay:
                dlg.open = False
                self.page.overlay.remove(dlg)
                self.page.update()
            elif dlg:
                # Se o diálogo existe mas não está no overlay, apenas feche-o
                dlg.open = False
                self.page.update()
        except Exception as e:
            print(f"Erro ao fechar diálogo: {str(e)}")
            # Tentar atualizar a página mesmo assim
            self.page.update()
    
    def confirmar_exclusao_empresa(self, e, dlg, codigo):
        """Confirma a exclusão de uma empresa."""
        try:
            # Fechar diálogo
            dlg.open = False
            self.page.overlay.remove(dlg)
            
            # Excluir empresa
            sucesso, mensagem = self.empresa_controller.excluir_empresa(codigo)
            
            # Criar snackbar com a mensagem apropriada
            snack = ft.SnackBar(
                content=ft.Text(mensagem),
                bgcolor=ft.colors.RED_400 if not sucesso else None,
                action_color=ft.colors.WHITE if not sucesso else None
            )
            
            # Atualizar a interface completamente
            if sucesso:
                self.forcar_atualizacao_interface()
            
            # Adicionar e mostrar o snackbar
            self.page.overlay.append(snack)
            snack.open = True
            
            # Fazer uma única atualização da página após todas as mudanças
            self.page.update()
        except Exception as e:
            # Em caso de erro, exibir uma mensagem e registrar o erro
            error_snack = ft.SnackBar(
                content=ft.Text(f"Erro ao excluir empresa: {str(e)}"),
                bgcolor=ft.colors.RED_400,
                action="OK"
            )
            self.page.overlay.append(error_snack)
            error_snack.open = True
            self.page.update()
            print(f"Erro ao excluir empresa: {str(e)}")  # Log no console
    
    def adicionar_empresa(self, e):
        """Adiciona uma nova empresa ao sistema."""
        # Validar campos obrigatórios
        if not self.codigo_field.value or not self.nome_empresa_field.value or not self.tenet_id_field.value or not self.ambiente_field.value:
            snack = ft.SnackBar(content=ft.Text("Por favor, preencha todos os campos obrigatórios"))
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
            return
        
        # Criar empresa
        sucesso, mensagem = self.empresa_controller.criar_empresa(
            self.codigo_field.value,
            self.nome_empresa_field.value,
            self.tenet_id_field.value,
            self.ambiente_field.value
        )
        
        if sucesso:
            # Limpar campos
            self.codigo_field.value = ""
            self.nome_empresa_field.value = ""
            self.tenet_id_field.value = ""
            self.ambiente_field.value = ""
            
            # Atualizar lista de empresas
            self.atualizar_lista_empresas()
            
            # Mostrar mensagem de sucesso
            snack = ft.SnackBar(content=ft.Text(mensagem))
            self.page.overlay.append(snack)
            snack.open = True
        else:
            # Mostrar mensagem de erro
            snack = ft.SnackBar(
                content=ft.Text(mensagem),
                bgcolor=ft.colors.RED_400
            )
            self.page.overlay.append(snack)
            snack.open = True
        
        self.page.update()
    
    def salvar_empresa(self, e):
        """Salva as alterações de uma empresa."""
        # Validar campos obrigatórios
        if not self.codigo_field.value or not self.nome_empresa_field.value or not self.tenet_id_field.value or not self.ambiente_field.value:
            snack = ft.SnackBar(content=ft.Text("Por favor, preencha todos os campos obrigatórios"))
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
            return
        
        # Atualizar empresa
        sucesso, mensagem = self.empresa_controller.atualizar_empresa(
            self.empresa_editando,  # Código original
            self.codigo_field.value,
            self.nome_empresa_field.value,
            self.tenet_id_field.value,
            self.ambiente_field.value
        )
        
        if sucesso:
            # Limpar campos
            self.codigo_field.value = ""
            self.nome_empresa_field.value = ""
            self.tenet_id_field.value = ""
            self.ambiente_field.value = ""
            
            # Resetar estado de edição
            self.empresa_editando = None
            self.btn_adicionar_empresa.visible = True
            self.btn_salvar_empresa.visible = False
            self.btn_cancelar_empresa.visible = False
            
            # Atualizar lista de empresas
            self.atualizar_lista_empresas()
            
            # Mostrar mensagem de sucesso
            snack = ft.SnackBar(content=ft.Text(mensagem))
            self.page.overlay.append(snack)
            snack.open = True
        else:
            # Mostrar mensagem de erro
            snack = ft.SnackBar(
                content=ft.Text(mensagem),
                bgcolor=ft.colors.RED_400
            )
            self.page.overlay.append(snack)
            snack.open = True
        
        self.page.update()
    
    def cancelar_edicao_empresa(self, e):
        """Cancela a edição de uma empresa."""
        # Limpar campos
        self.codigo_field.value = ""
        self.nome_empresa_field.value = ""
        
        # Resetar estado de edição
        self.empresa_editando = None
        self.btn_adicionar_empresa.visible = True
        self.btn_salvar_empresa.visible = False
        self.btn_cancelar_empresa.visible = False
        
        self.page.update()
    
    def editar_operador(self, e):
        """Prepara a interface para edição de um operador."""
        try:
            # Obter o email do operador a ser editado
            email_original = e.control.data
            
            # Busca os dados do operador
            operador = self.operador_controller.get_operador(email_original)
            if not operador:
                self.page.overlay.append(
                    ft.SnackBar(
                        content=ft.Text("Operador não encontrado"),
                        action="OK"
                    )
                )
                self.page.update()
                return
            
            # Preenche os campos com os dados do operador
            self.email_operador_field.value = operador['email']
            self.senha_operador_field.value = operador['senha']
            self.ativo_operador_checkbox.value = operador['ativo']
            
            # Armazena o email original para uso na atualização
            self.operador_editando = email_original
            
            # Atualiza a interface
            self.btn_adicionar_operador.visible = False
            self.btn_salvar_operador.visible = True
            self.btn_cancelar_operador.visible = True
            self.page.update()
            
        except Exception as e:
            print(f"Erro ao preparar edição do operador: {e}")
            self.page.overlay.append(
                ft.SnackBar(
                    content=ft.Text(f"Erro ao preparar edição do operador: {str(e)}"),
                    action="OK"
                )
            )
            self.page.update()
    
    def excluir_operador(self, e):
        """Exclui um operador."""
        try:
            email = e.control.data
            if not email:
                error_snack = ft.SnackBar(
                    content=ft.Text("Não foi possível identificar o email do operador"),
                    bgcolor=ft.colors.RED_400
                )
                self.page.overlay.append(error_snack)
                error_snack.open = True
                self.page.update()
                return
                
            # Confirmar exclusão
            dlg = ft.AlertDialog(
                modal=True,  # Garantir que o diálogo seja modal
                title=ft.Text("Confirmar Exclusão"),
                content=ft.Text(f"Tem certeza que deseja excluir o operador {email}?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: self.fechar_dialogo(e, dlg)),
                    ft.TextButton(
                        "Excluir", 
                        on_click=lambda e: self.confirmar_exclusao_operador(e, dlg, email),
                        style=ft.ButtonStyle(color=ft.colors.RED_400)
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            # Adicionar o diálogo ao overlay e abri-lo
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()
        except Exception as e:
            print(f"Erro ao exibir diálogo de exclusão: {str(e)}")
            error_snack = ft.SnackBar(
                content=ft.Text(f"Erro ao preparar exclusão: {str(e)}"),
                bgcolor=ft.colors.RED_400
            )
            self.page.overlay.append(error_snack)
            error_snack.open = True
            self.page.update()
    
    def salvar_operador(self, e):
        """Salva um operador novo ou atualiza um existente."""
        try:
            # Validação dos campos
            if not self.email_operador_field.value or not self.senha_operador_field.value:
                self.page.overlay.append(
                    ft.SnackBar(
                        content=ft.Text("Preencha todos os campos obrigatórios"),
                        action="OK"
                    )
                )
                self.page.update()
                return

            # Se estiver editando
            if self.operador_editando:
                try:
                    # Atualiza o operador
                    self.operador_controller.atualizar_operador(
                        self.operador_editando,
                        self.email_operador_field.value,
                        self.senha_operador_field.value,
                        True
                    )
                    
                    # Limpa os campos
                    self.email_operador_field.value = ""
                    self.senha_operador_field.value = ""
                    self.operador_editando = None
                    
                    # Atualiza a interface
                    self.atualizar_lista_operadores()
                    self.atualizar_area_administrativa()
                    
                    # Mostra mensagem de sucesso
                    self.page.overlay.append(
                        ft.SnackBar(
                            content=ft.Text("Operador atualizado com sucesso!"),
                            action="OK"
                        )
                    )
                    self.page.update()
                    
                except ValueError as ve:
                    # Mostra mensagem de erro
                    self.page.overlay.append(
                        ft.SnackBar(
                            content=ft.Text(str(ve)),
                            action="OK"
                        )
                    )
                    self.page.update()
                    
            else:
                try:
                    # Cria novo operador
                    self.operador_controller.adicionar_operador(
                        self.email_operador_field.value,
                        self.senha_operador_field.value,
                        self.ativo_operador_checkbox.value
                    )
                    
                    # Limpa os campos
                    self.email_operador_field.value = ""
                    self.senha_operador_field.value = ""
                    self.ativo_operador_checkbox.value = True
                    
                    # Atualiza a interface
                    self.atualizar_lista_operadores()
                    self.atualizar_area_administrativa()
                    
                    # Mostra mensagem de sucesso
                    self.page.overlay.append(
                        ft.SnackBar(
                            content=ft.Text("Operador criado com sucesso!"),
                            action="OK"
                        )
                    )
                    self.page.update()
                    
                except ValueError as ve:
                    # Mostra mensagem de erro
                    self.page.overlay.append(
                        ft.SnackBar(
                            content=ft.Text(str(ve)),
                            action="OK"
                        )
                    )
                    self.page.update()
                    
        except Exception as e:
            # Mostra mensagem de erro genérica
            self.page.overlay.append(
                ft.SnackBar(
                    content=ft.Text(f"Erro ao salvar operador: {str(e)}"),
                    action="OK"
                )
            )
            self.page.update()
    
    def cancelar_edicao_operador(self, e):
        """Cancela a edição de um operador."""
        # Limpar campos
        self.email_operador_field.value = ""
        self.senha_operador_field.value = ""
        self.ativo_operador_checkbox.value = True
        
        # Resetar estado de edição
        self.operador_editando = None
        self.btn_adicionar_operador.visible = True
        self.btn_salvar_operador.visible = False
        self.btn_cancelar_operador.visible = False
        
        self.page.update()
    
    def confirmar_exclusao_operador(self, e, dlg, email):
        """Confirma a exclusão de um operador."""
        try:
            # Fechar diálogo
            dlg.open = False
            self.page.overlay.remove(dlg)
            
            # Excluir operador
            sucesso, mensagem = self.operador_controller.excluir_operador(email)
            
            # Criar snackbar com a mensagem apropriada
            snack = ft.SnackBar(
                content=ft.Text(mensagem),
                bgcolor=ft.colors.RED_400 if not sucesso else None,
                action_color=ft.colors.WHITE if not sucesso else None
            )
            
            # Atualizar a interface completamente
            if sucesso:
                # Primeiro atualiza todas as listas
                self.atualizar_area_administrativa()
                # Força a atualização da interface
                self.forcar_atualizacao_interface()
            
            # Adicionar e mostrar o snackbar
            self.page.overlay.append(snack)
            snack.open = True
            
            # Fazer uma única atualização da página após todas as mudanças
            self.page.update()
        except Exception as e:
            # Em caso de erro, exibir uma mensagem e registrar o erro
            error_snack = ft.SnackBar(
                content=ft.Text(f"Erro ao excluir operador: {str(e)}"),
                bgcolor=ft.colors.RED_400,
                action="OK"
            )
            self.page.overlay.append(error_snack)
            error_snack.open = True
            self.page.update()
            print(f"Erro ao excluir operador: {str(e)}")  # Log no console
    
    def adicionar_operador(self, e):
        """Adiciona um novo operador ao sistema."""
        # Validar campos obrigatórios
        if not self.email_operador_field.value or not self.senha_operador_field.value:
            snack = ft.SnackBar(content=ft.Text("Por favor, preencha todos os campos obrigatórios"))
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
            return
        
        # Criar operador
        sucesso, mensagem = self.operador_controller.adicionar_operador(
            self.email_operador_field.value,
            self.senha_operador_field.value,
            self.ativo_operador_checkbox.value
        )
        
        if sucesso:
            # Limpar campos
            self.email_operador_field.value = ""
            self.senha_operador_field.value = ""
            self.ativo_operador_checkbox.value = True
            
            # Atualizar lista de operadores
            self.atualizar_lista_operadores()
            
            # Forçar atualização da interface
            self.forcar_atualizacao_interface()
            
            # Mostrar mensagem de sucesso
            snack = ft.SnackBar(content=ft.Text(mensagem))
            self.page.overlay.append(snack)
            snack.open = True
        else:
            # Mostrar mensagem de erro
            snack = ft.SnackBar(
                content=ft.Text(mensagem),
                bgcolor=ft.colors.RED_400
            )
            self.page.overlay.append(snack)
            snack.open = True
        
        self.page.update()

    def adicionar_usuario(self, e):
        """Adiciona um novo usuário ao sistema."""
        # Validar campos obrigatórios
        if not self.username_field.value or not self.nome_field.value or not self.senha_field.value:
            snack = ft.SnackBar(content=ft.Text("Por favor, preencha todos os campos obrigatórios"))
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
            return
        
        # Obter empresas selecionadas
        empresas_selecionadas = []
        for checkbox in self.empresas_checkboxes.controls:
            if checkbox.value:
                empresas_selecionadas.append(checkbox.data)
        
        # Verificar se pelo menos uma empresa foi selecionada
        if not empresas_selecionadas:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Selecione pelo menos uma empresa"))
            )
            return
        
        # Criar usuário
        sucesso, mensagem = self.usuario_controller.criar_usuario(
            self.username_field.value,
            self.nome_field.value,
            self.senha_field.value,
            self.is_admin_checkbox.value,
            empresas_selecionadas
        )
        
        if sucesso:
            # Limpar campos
            self.username_field.value = ""
            self.nome_field.value = ""
            self.senha_field.value = ""
            self.is_admin_checkbox.value = False
            for checkbox in self.empresas_checkboxes.controls:
                checkbox.value = False
            
            # Atualizar lista de usuários
            self.atualizar_lista_usuarios()
            
            # Mostrar mensagem de sucesso
            snack = ft.SnackBar(content=ft.Text(mensagem))
            self.page.overlay.append(snack)
            snack.open = True
        else:
            # Mostrar mensagem de erro
            snack = ft.SnackBar(
                content=ft.Text(mensagem),
                bgcolor=ft.colors.RED_400
            )
            self.page.overlay.append(snack)
            snack.open = True
        
        self.page.update()

    def salvar_usuario(self, e):
        """Salva as alterações de um usuário."""
        # Validar campos obrigatórios
        if not self.username_field.value or not self.nome_field.value:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Por favor, preencha todos os campos obrigatórios"))
            )
            return
        
        # Obter empresas selecionadas
        empresas_selecionadas = []
        for checkbox in self.empresas_checkboxes.controls:
            if checkbox.value:
                empresas_selecionadas.append(checkbox.data)
        
        # Verificar se pelo menos uma empresa foi selecionada
        if not empresas_selecionadas:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Selecione pelo menos uma empresa"))
            )
            return
        
        # Atualizar usuário
        sucesso, mensagem = self.usuario_controller.atualizar_usuario(
            self.usuario_editando,  # Username original
            self.username_field.value,
            self.nome_field.value,
            self.senha_field.value if self.senha_field.value else None,  # Só atualiza senha se foi preenchida
            self.is_admin_checkbox.value,
            empresas_selecionadas
        )
        
        if sucesso:
            # Limpar campos
            self.username_field.value = ""
            self.nome_field.value = ""
            self.senha_field.value = ""
            self.is_admin_checkbox.value = False
            for checkbox in self.empresas_checkboxes.controls:
                checkbox.value = False
            
            # Resetar estado de edição
            self.usuario_editando = None
            self.btn_adicionar_usuario.visible = True
            self.btn_salvar_usuario.visible = False
            self.btn_cancelar_usuario.visible = False
            
            # Atualizar lista de usuários
            self.atualizar_lista_usuarios()
            
            # Mostrar mensagem de sucesso
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(mensagem))
            )
        else:
            # Mostrar mensagem de erro
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(mensagem),
                    bgcolor=ft.colors.RED_400
                )
            )
        
        self.page.update()

    def cancelar_edicao_usuario(self, e):
        """Cancela a edição de um usuário."""
        # Limpar campos
        self.username_field.value = ""
        self.nome_field.value = ""
        self.senha_field.value = ""
        self.is_admin_checkbox.value = False
        for checkbox in self.empresas_checkboxes.controls:
            checkbox.value = False
        
        # Resetar estado de edição
        self.usuario_editando = None
        self.btn_adicionar_usuario.visible = True
        self.btn_salvar_usuario.visible = False
        self.btn_cancelar_usuario.visible = False
        
        self.page.update()

    def excluir_usuario(self, e):
        """Exclui um usuário."""
        try:
            # Obter o username do evento
            username = e.control.data
            
            # Verificar se o usuário existe
            usuario = self.usuario_controller.get_usuario(username)
            if not usuario:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Usuário não encontrado"),
                        bgcolor=ft.colors.RED_400
                    )
                )
                return
            
            # Criar diálogo de confirmação
            dlg = ft.AlertDialog(
                title=ft.Text("Confirmar exclusão"),
                content=ft.Text(f"Deseja realmente excluir o usuário {username}?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: self.fechar_dialogo(e, dlg)),
                    ft.TextButton("Excluir", on_click=lambda e: self.confirmar_exclusao_usuario(e, dlg, username))
                ]
            )
            
            # Mostrar diálogo
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()
            
        except Exception as e:
            print(f"Erro ao excluir usuário: {e}")
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Erro ao excluir usuário: {str(e)}"),
                    bgcolor=ft.colors.RED_400
                )
            )
            self.page.update()

    def confirmar_exclusao_usuario(self, e, dlg, username):
        """Confirma a exclusão do usuário."""
        try:
            # Fechar o diálogo
            self.fechar_dialogo(e, dlg)
            
            # Excluir o usuário
            sucesso, mensagem = self.usuario_controller.excluir_usuario(username)
            
            # Mostrar mensagem de sucesso ou erro
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(mensagem),
                    bgcolor=ft.colors.GREEN_400 if sucesso else ft.colors.RED_400
                )
            )
            
            # Atualizar a interface
            self.atualizar_area_administrativa()
            
        except Exception as e:
            print(f"Erro ao excluir usuário: {e}")
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Erro ao excluir usuário: {str(e)}"),
                    bgcolor=ft.colors.RED_400
                )
            )
            self.page.update()

    def editar_usuario(self, e):
        """Inicia a edição de um usuário."""
        try:
            # Obter o username do usuário a ser editado
            username = e.control.data
            
            # Buscar dados do usuário
            usuario = self.usuario_controller.get_usuario(username)
            if not usuario:
                self.page.overlay.append(
                    ft.SnackBar(
                        content=ft.Text("Usuário não encontrado"),
                        action="OK"
                    )
                )
                self.page.update()
                return
            
            # Preencher campos com dados do usuário
            self.username_field.value = usuario["username"]
            self.nome_field.value = usuario["nome"]
            self.senha_field.value = ""  # Não preencher senha por segurança
            self.is_admin_checkbox.value = usuario["is_admin"]
            
            # Marcar empresas do usuário
            empresas_usuario = self.usuario_controller.get_empresas_usuario(username)
            for checkbox in self.empresas_checkboxes.controls:
                checkbox.value = any(emp["codigo"] == checkbox.data for emp in empresas_usuario)
            
            # Armazenar username original para atualização
            self.usuario_editando = username
            
            # Atualizar interface
            self.btn_adicionar_usuario.visible = False
            self.btn_salvar_usuario.visible = True
            self.btn_cancelar_usuario.visible = True
            
            self.page.update()
            
        except Exception as e:
            print(f"Erro ao preparar edição do usuário: {e}")
            self.page.overlay.append(
                ft.SnackBar(
                    content=ft.Text(f"Erro ao preparar edição do usuário: {str(e)}"),
                    action="OK"
                )
            )
            self.page.update()

    def forcar_atualizacao_interface(self):
        """Força a atualização completa da interface."""
        try:
            # Atualiza o container principal
            if hasattr(self, 'main_container'):
                self.main_container.update()
            
            # Atualiza a área administrativa
            self.atualizar_area_administrativa()
            
            # Força a atualização da página
            self.page.update()
        except Exception as e:
            print(f"Erro ao forçar atualização da interface: {str(e)}")
            # Tenta uma atualização básica em caso de erro
            self.page.update()

if __name__ == "__main__":
    app = TelaContratos()
    ft.app(target=app.main, port=8551) 