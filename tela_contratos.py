import flet as ft
from contrato_trabalho import ContratoTrabalhoLG
from controle_acesso import ControleAcesso
from database import Database
from datetime import datetime
import asyncio

class TelaContratos:
    def __init__(self):
        self.contrato_lg = ContratoTrabalhoLG()
        self.controle_acesso = ControleAcesso()
        self.db = Database()
        self.page = None  # Referência para a página
        self.tabela_empresas = None  # Referência para a tabela de empresas
        self.tabela_usuarios = None  # Referência para a tabela de usuários
        self.lista_empresas_usuarios = None  # Referência para a lista de empresas na aba usuários
        
    def main(self, page: ft.Page):
        self.page = page  # Armazenar referência da página
        page.title = "Sistema de Contratos de Trabalho"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
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
            width=1100,  # Largura fixa para garantir que todas as colunas sejam visíveis
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
                            scroll=ft.ScrollMode.ALWAYS,
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
            empresas = self.controle_acesso.get_empresas_permitidas()
            empresa_dropdown.options = [
                ft.dropdown.Option("", "Todas as Empresas")
            ] + [
                ft.dropdown.Option(emp["codigo"], f"{emp['codigo']} - {emp['nome']}")
                for emp in empresas
            ]
            empresa_dropdown.value = ""
            page.update()
        
        async def fazer_login(e):
            if self.controle_acesso.fazer_login(usuario.value, senha.value):
                # Login bem sucedido
                erro_login.visible = False
                info_usuario.value = f"Usuário: {self.controle_acesso.get_usuario_atual()}"
                
                # Verificar se é admin
                usuario_data = self.controle_acesso.db.get_usuario(usuario.value)
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
                await self.atualizar_area_administrativa()
            else:
                # Login falhou
                erro_login.value = "Usuário ou senha inválidos"
                erro_login.visible = True
            
            await page.update_async()
        
        async def fazer_logout(e):
            self.controle_acesso.fazer_logout()
            usuario.value = ""
            senha.value = ""
            empresa_dropdown.options = []
            tabs.visible = False
            
            # Voltar para tela de login
            self.main_container.content = ft.Column(
                [login_card],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
            await page.update_async()
        
        async def buscar_contratos(e):
            try:
                # Validar mês e ano
                if not mes.value or not ano.value:
                    page.show_snack_bar(
                        ft.SnackBar(content=ft.Text("Por favor, preencha mês e ano"))
                    )
                    return

                # Mostrar progresso
                self.progress.visible = True
                await page.update_async()

                # Limpar tabela atual
                data_table.rows.clear()

                # Obter empresa selecionada
                empresa_selecionada = None
                if empresa_dropdown.value:
                    empresa_selecionada = self.db.get_empresa(empresa_dropdown.value)

                # Obter operador selecionado
                operador_selecionado = None
                if operador_dropdown.value:
                    print(f"Email do operador selecionado: {operador_dropdown.value}")
                    operador_selecionado = self.db.get_operador(operador_dropdown.value)
                    print(f"Operador selecionado: {operador_selecionado}")
                    if operador_selecionado:
                        print(f"Credenciais do operador: {operador_selecionado['email']} / {operador_selecionado['senha']}")

                # Buscar contratos
                contratos = await self.buscar_contratos_api(
                    mes.value,
                    ano.value,
                    empresa_selecionada,
                    operador_selecionado
                )
                print(f"Total de contratos retornados da API: {len(contratos)}")
                
                # Filtrar contratos baseado nas permissões do usuário
                contratos_filtrados = self.controle_acesso.filtrar_contratos(contratos)
                print(f"Total de contratos após filtro de permissões: {len(contratos_filtrados)}")
                
                # Filtrar por empresa selecionada
                if empresa_dropdown.value:
                    contratos_filtrados = [
                        contrato for contrato in contratos_filtrados
                        if str(contrato.get('empresa', {}).get('Codigo', '')) == empresa_dropdown.value
                    ]
                    print(f"Total de contratos após filtro de empresa: {len(contratos_filtrados)}")
                
                # Preencher tabela
                for contrato in contratos_filtrados:
                    print(f"Adicionando contrato à tabela: {contrato['matricula']} - {contrato['nome']}")
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
                
                print(f"Total de linhas adicionadas à tabela: {len(data_table.rows)}")
                
                # Atualizar contador de registros
                total_registros = len(contratos_filtrados)
                table_container.content.controls[0].controls[1].value = f"Total de registros: {total_registros}"
                
                # Esconder progresso
                self.progress.visible = False
                await page.update_async()
                print("Atualização da página concluída")
            except Exception as e:
                page.show_snack_bar(
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
        
        # Checkbox para definir se é admin
        is_admin = ft.Checkbox(
            label="Usuário Administrador",
            value=False
        )
        
        # Lista de empresas para seleção
        empresas = ft.Column(
            [],
            scroll=ft.ScrollMode.AUTO,
            height=200
        )
        self.lista_empresas_usuarios = empresas  # Salvar referência
        
        # Lista de usuários
        lista_usuarios = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Usuário", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nome", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Empresas", weight=ft.FontWeight.BOLD)),
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
        self.tabela_usuarios = lista_usuarios  # Salvar referência
        
        # Botão de adicionar (declarado antes das funções que o usam)
        btn_adicionar = ft.ElevatedButton(
            "Adicionar Usuário",
            icon=ft.icons.ADD,
            on_click=None,  # Será definido depois
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
            ),
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )
        
        def validar_campos():
            if not username.value:
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("O campo Nome de usuário é obrigatório"),
                        bgcolor=ft.colors.RED_400
                    )
                )
                return False
            if not senha.value:
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("O campo Senha é obrigatório"),
                        bgcolor=ft.colors.RED_400
                    )
                )
                return False
            if not nome.value:
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("O campo Nome completo é obrigatório"),
                        bgcolor=ft.colors.RED_400
                    )
                )
                return False
                
            # Verificar se pelo menos uma empresa foi selecionada
            empresas_selecionadas = [
                cb.label.split(" - ")[0]
                for cb in empresas.controls
                if cb.value
            ]
            if not empresas_selecionadas:
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Selecione pelo menos uma empresa"),
                        bgcolor=ft.colors.RED_400
                    )
                )
                return False
                
            return True
        
        async def adicionar_usuario(self, e):
            """Adiciona um novo usuário ao sistema."""
            username = username.value
            nome = nome.value
            senha = senha.value
            is_admin = is_admin.value
            
            if not all([username, nome, senha]):
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Preencha todos os campos!"))
                )
                return
            
            # Obter empresas selecionadas
            empresas_selecionadas = []
            for checkbox in self.lista_empresas_usuarios.controls:
                if checkbox.value:
                    codigo = checkbox.label.split(" - ")[0]
                    empresas_selecionadas.append(codigo)
            
            # Criar usuário
            if self.db.criar_usuario(username, nome, senha, is_admin, empresas_selecionadas):
                # Limpar campos
                username.value = ""
                nome.value = ""
                senha.value = ""
                is_admin.value = False
                for checkbox in self.lista_empresas_usuarios.controls:
                    checkbox.value = False
                
                # Atualizar área administrativa
                await self.atualizar_area_administrativa()
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Erro ao criar usuário!"))
                )
        
        async def excluir_usuario(self, username):
            """Exclui um usuário do sistema."""
            if self.db.excluir_usuario(username):
                # Atualizar área administrativa
                await self.atualizar_area_administrativa()
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Erro ao excluir usuário!"))
                )
        
        async def editar_usuario(self, username):
            """Edita um usuário existente."""
            user = self.db.get_usuario(username)
            if not user:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Usuário não encontrado!"))
                )
                return
            
            # Preencher campos com dados do usuário
            username.value = user["username"]
            nome.value = user["nome"]
            is_admin.value = user["is_admin"]
            
            # Marcar empresas do usuário
            empresas_usuario = self.db.get_empresas_usuario(username)
            for checkbox in self.lista_empresas_usuarios.controls:
                codigo = checkbox.label.split(" - ")[0]
                checkbox.value = any(emp["codigo"] == codigo for emp in empresas_usuario)
            
            # Alterar botão para salvar
            btn_adicionar.text = "Salvar"
            btn_adicionar.on_click = lambda e: self.salvar_usuario(username)
            
            # Atualizar área administrativa
            await self.atualizar_area_administrativa()
        
        async def salvar_usuario(self, username_original):
            """Salva as alterações de um usuário."""
            username = username.value
            nome = nome.value
            senha = senha.value
            is_admin = is_admin.value
            
            if not all([username, nome]):
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Preencha todos os campos!"))
                )
                return
            
            # Obter empresas selecionadas
            empresas_selecionadas = []
            for checkbox in self.lista_empresas_usuarios.controls:
                if checkbox.value:
                    codigo = checkbox.label.split(" - ")[0]
                    empresas_selecionadas.append(codigo)
            
            # Atualizar usuário
            if self.db.atualizar_usuario(username_original, username, nome, senha, is_admin, empresas_selecionadas):
                # Limpar campos
                username.value = ""
                nome.value = ""
                senha.value = ""
                is_admin.value = False
                for checkbox in self.lista_empresas_usuarios.controls:
                    checkbox.value = False
                
                # Restaurar botão para adicionar
                btn_adicionar.text = "Adicionar"
                btn_adicionar.on_click = self.adicionar_usuario
                
                # Atualizar área administrativa
                await self.atualizar_area_administrativa()
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Erro ao atualizar usuário!"))
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
        
        def atualizar_lista_usuarios():
            lista_usuarios.rows.clear()
            for user in self.db.get_todos_usuarios():
                # Obter empresas do usuário
                empresas_usuario = self.db.get_empresas_usuario(user["username"])
                empresas_str = ", ".join([f"{emp['codigo']} - {emp['nome']}" for emp in empresas_usuario])
                
                lista_usuarios.rows.append(
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
                                ft.Row([
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        icon_color=ft.colors.BLUE,
                                        tooltip="Editar",
                                        data=user["username"],
                                        on_click=lambda e: asyncio.create_task(self.editar_usuario(e.control.data))
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        icon_color=ft.colors.RED_400,
                                        tooltip="Excluir",
                                        data=user["username"],
                                        on_click=lambda e: asyncio.create_task(self.excluir_usuario(e.control.data))
                                    )
                                ])
                            )
                        ]
                    )
                )
            page.update()

        # Definir o on_click do botão adicionar
        btn_adicionar.on_click = adicionar_usuario
        
        # Atualizar listas
        atualizar_lista_empresas()
        atualizar_lista_usuarios()
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Gerenciar Usuários",
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
                                    nome,
                                    ft.Container(height=10),
                                    is_admin
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
                    btn_adicionar,
                    ft.Container(height=20),
                    lista_usuarios
                ],
                spacing=0
            ),
            padding=20
        )
    
    def criar_tab_empresas(self, page: ft.Page):
        # Campos do formulário
        codigo_empresa = ft.TextField(
            label="Código",
            width=200,
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        nome_empresa = ft.TextField(
            label="Nome",
            width=300,
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        tenetID_empresa = ft.TextField(
            label="TenetID",
            width=200,
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        ambiente_empresa = ft.TextField(
            label="Ambiente",
            width=200,
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.WHITE,
            value="producao"
        )
        
        # Lista de empresas
        tabela_empresas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nome", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("TenetID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ambiente", weight=ft.FontWeight.BOLD)),
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
        self.tabela_empresas = tabela_empresas  # Salvar referência
        
        def atualizar_lista_empresas():
            """Atualiza a lista de empresas na tabela."""
            tabela_empresas.rows.clear()
            for emp in self.db.get_todas_empresas():
                tabela_empresas.rows.append(
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
                                        on_click=lambda e: asyncio.create_task(self.editar_empresa(e.control.data))
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        icon_color=ft.colors.RED_400,
                                        tooltip="Excluir",
                                        data=emp["codigo"],
                                        on_click=lambda e: asyncio.create_task(self.excluir_empresa(e.control.data))
                                    )
                                ])
                            )
                        ]
                    )
                )
            page.update()
        
        def validar_campos():
            if not codigo_empresa.value:
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("O campo Código é obrigatório"),
                        bgcolor=ft.colors.RED_400
                    )
                )
                return False
            if not nome_empresa.value:
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("O campo Nome é obrigatório"),
                        bgcolor=ft.colors.RED_400
                    )
                )
                return False
            if not tenetID_empresa.value:
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("O campo TenetID é obrigatório"),
                        bgcolor=ft.colors.RED_400
                    )
                )
                return False
            return True
        
        async def adicionar_empresa(self, e):
            """Adiciona uma nova empresa ao sistema."""
            codigo = codigo_empresa.value
            nome = nome_empresa.value
            tenet_id = tenetID_empresa.value
            ambiente = ambiente_empresa.value
            
            if not all([codigo, nome, tenet_id, ambiente]):
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Preencha todos os campos!"))
                )
                return
            
            # Criar empresa
            if self.db.criar_empresa(codigo, nome, tenet_id, ambiente):
                # Limpar campos
                codigo_empresa.value = ""
                nome_empresa.value = ""
                tenetID_empresa.value = ""
                ambiente_empresa.value = "producao"
                
                # Atualizar área administrativa
                await self.atualizar_area_administrativa()
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Erro ao criar empresa!"))
                )
        
        async def excluir_empresa(self, codigo):
            """Exclui uma empresa do sistema."""
            if self.db.excluir_empresa(codigo):
                # Atualizar área administrativa
                await self.atualizar_area_administrativa()
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Erro ao excluir empresa!"))
                )
        
        async def editar_empresa(self, codigo):
            """Edita uma empresa existente."""
            empresa = self.db.get_empresa(codigo)
            if not empresa:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Empresa não encontrada!"))
                )
                return
            
            # Preencher campos com dados da empresa
            codigo_empresa.value = empresa["codigo"]
            nome_empresa.value = empresa["nome"]
            tenetID_empresa.value = empresa["tenetID"]
            ambiente_empresa.value = empresa["ambiente"]
            
            # Alterar botão para salvar
            btn_adicionar.text = "Salvar"
            btn_adicionar.on_click = lambda e: self.salvar_empresa(codigo)
            
            # Atualizar área administrativa
            await self.atualizar_area_administrativa()
        
        async def salvar_empresa(self, codigo_original):
            """Salva as alterações de uma empresa."""
            codigo = codigo_empresa.value
            nome = nome_empresa.value
            tenet_id = tenetID_empresa.value
            ambiente = ambiente_empresa.value
            
            if not all([codigo, nome, tenet_id, ambiente]):
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Preencha todos os campos!"))
                )
                return
            
            # Atualizar empresa
            if self.db.atualizar_empresa(codigo_original, codigo, nome, tenet_id, ambiente):
                # Limpar campos
                codigo_empresa.value = ""
                nome_empresa.value = ""
                tenetID_empresa.value = ""
                ambiente_empresa.value = "producao"
                
                # Restaurar botão para adicionar
                btn_adicionar.text = "Adicionar"
                btn_adicionar.on_click = self.adicionar_empresa
                
                # Atualizar área administrativa
                await self.atualizar_area_administrativa()
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Erro ao atualizar empresa!"))
                )
        
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
        
        # Atualizar lista
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
                            ft.Column(
                                [
                                    codigo_empresa,
                                    ft.Container(height=10),
                                    nome_empresa,
                                    ft.Container(height=10),
                                    tenetID_empresa,
                                    ft.Container(height=10),
                                    ambiente_empresa
                                ],
                                spacing=0
                            ),
                            ft.Container(width=20),
                            ft.Column(
                                [
                                    ft.Container(height=20),
                                    btn_adicionar
                                ],
                                spacing=0
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Container(height=20),
                    tabela_empresas
                ],
                spacing=0
            ),
            padding=20
        )

    def criar_tab_contratos(self, page):
        """Cria a tab de contratos."""
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
        
        # Atualizar lista de empresas
        def atualizar_empresas():
            empresas = self.controle_acesso.get_empresas_permitidas()
            empresa_dropdown.options = [
                ft.dropdown.Option("", "Todas as Empresas")
            ] + [
                ft.dropdown.Option(emp["codigo"], f"{emp['codigo']} - {emp['nome']}")
                for emp in empresas
            ]
            empresa_dropdown.value = ""
            page.update()
        
        # Atualizar lista de operadores
        def atualizar_operadores():
            operadores = self.db.get_todos_operadores()
            operador_dropdown.options = [
                ft.dropdown.Option("", "Usar credenciais padrão")
            ] + [
                ft.dropdown.Option(operador["email"], f"{operador['email']} ({'Ativo' if operador['ativo'] else 'Inativo'})")
                for operador in operadores
            ]
            operador_dropdown.value = ""
            print("Operadores disponíveis:", [op["email"] for op in operadores])
            page.update()
        
        # Indicador de carregamento
        progress = ft.ProgressBar(
            visible=False,
            color=ft.colors.BLUE,
            bgcolor=ft.colors.BLUE_GREY_100
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
            width=1100,  # Largura fixa para garantir que todas as colunas sejam visíveis
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
                            scroll=ft.ScrollMode.ALWAYS,
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
        
        async def buscar_contratos(e):
            try:
                # Validar mês e ano
                if not mes.value or not ano.value:
                    page.show_snack_bar(
                        ft.SnackBar(content=ft.Text("Por favor, preencha mês e ano"))
                    )
                    return

                # Mostrar progresso
                progress.visible = True
                await page.update_async()

                # Limpar tabela atual
                data_table.rows.clear()

                # Obter empresa selecionada
                empresa_selecionada = None
                if empresa_dropdown.value:
                    empresa_selecionada = self.db.get_empresa(empresa_dropdown.value)

                # Obter operador selecionado
                operador_selecionado = None
                if operador_dropdown.value:
                    print(f"Email do operador selecionado: {operador_dropdown.value}")
                    operador_selecionado = self.db.get_operador(operador_dropdown.value)
                    print(f"Operador selecionado: {operador_selecionado}")
                    if operador_selecionado:
                        print(f"Credenciais do operador: {operador_selecionado['email']} / {operador_selecionado['senha']}")

                # Buscar contratos
                contratos = await self.buscar_contratos_api(
                    mes.value,
                    ano.value,
                    empresa_selecionada,
                    operador_selecionado
                )
                print(f"Total de contratos retornados da API: {len(contratos)}")
                
                # Filtrar contratos baseado nas permissões do usuário
                contratos_filtrados = self.controle_acesso.filtrar_contratos(contratos)
                print(f"Total de contratos após filtro de permissões: {len(contratos_filtrados)}")
                
                # Filtrar por empresa selecionada
                if empresa_dropdown.value:
                    contratos_filtrados = [
                        contrato for contrato in contratos_filtrados
                        if str(contrato.get('empresa', {}).get('Codigo', '')) == empresa_dropdown.value
                    ]
                    print(f"Total de contratos após filtro de empresa: {len(contratos_filtrados)}")
                
                # Preencher tabela
                for contrato in contratos_filtrados:
                    print(f"Adicionando contrato à tabela: {contrato['matricula']} - {contrato['nome']}")
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
                
                print(f"Total de linhas adicionadas à tabela: {len(data_table.rows)}")
                
                # Atualizar contador de registros
                total_registros = len(contratos_filtrados)
                table_container.content.controls[0].controls[1].value = f"Total de registros: {total_registros}"
                
                # Esconder progresso
                progress.visible = False
                await page.update_async()
                print("Atualização da página concluída")
            except Exception as e:
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Erro ao buscar contratos: {e}"),
                        bgcolor=ft.colors.RED_400,
                        action="OK"
                    )
                )
        
        # Botão de buscar
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
        
        # Atualizar lista de empresas e operadores
        atualizar_empresas()
        atualizar_operadores()
        
        return ft.Container(
            content=ft.Column(
                [
                    filtros_card,
                    progress,
                    table_container
                ],
                spacing=0
            ),
            padding=20
        )

    def criar_tab_operadores(self, page):
        """Cria a tab de operadores."""
        # Campos de entrada
        email_operador = ft.TextField(
            label="Email",
            width=300,
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        senha_operador = ft.TextField(
            label="Senha",
            width=300,
            password=True,
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.WHITE
        )
        
        switch_operador_ativo = ft.Switch(
            label="Ativo",
            value=True
        )
        
        # Lista de operadores
        tabela_operadores = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Email", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
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
        self.tabela_operadores = tabela_operadores  # Salvar referência
        
        async def atualizar_lista_operadores(self):
            """Atualiza a lista de operadores na tabela."""
            self.tabela_operadores.rows.clear()
            for operador in self.db.get_todos_operadores():
                self.tabela_operadores.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(operador['email'])),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(
                                        "Ativo" if operador['ativo'] else "Inativo",
                                        color=ft.colors.WHITE,
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                    bgcolor=ft.colors.GREEN if operador['ativo'] else ft.colors.RED_400,
                                    border_radius=15,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5)
                                )
                            ),
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        icon_color=ft.colors.BLUE,
                                        tooltip="Editar",
                                        data=operador['email'],
                                        on_click=lambda e: asyncio.create_task(self.editar_operador(e.control.data))
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        icon_color=ft.colors.RED_400,
                                        tooltip="Excluir",
                                        data=operador['email'],
                                        on_click=lambda e: asyncio.create_task(self.excluir_operador(e.control.data))
                                    )
                                ])
                            )
                        ]
                    )
                )
            await self.page.update_async()
        
        async def adicionar_operador(self, e):
            """Adiciona um novo operador."""
            email = email_operador.value
            senha = senha_operador.value
            ativo = switch_operador_ativo.value
            
            if not email or not senha:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Preencha todos os campos!"))
                )
                return
            
            if self.db.adicionar_operador(email, senha, ativo):
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Operador adicionado com sucesso!"))
                )
                email_operador.value = ""
                senha_operador.value = ""
                switch_operador_ativo.value = True
                await self.atualizar_area_administrativa()
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Erro ao adicionar operador!"))
                )
            await self.page.update_async()
        
        async def editar_operador(self, email):
            """Edita um operador existente."""
            operador = self.db.get_operador(email)
            if operador:
                email_operador.value = operador['email']
                senha_operador.value = operador['senha']
                switch_operador_ativo.value = operador['ativo']
                btn_adicionar.text = "Atualizar Operador"
                btn_adicionar.on_click = lambda e: self.atualizar_operador(email)
                await self.atualizar_area_administrativa()
                await self.page.update_async()
        
        async def atualizar_operador(self, email):
            """Atualiza os dados de um operador existente."""
            email = email_operador.value
            senha = senha_operador.value
            ativo = switch_operador_ativo.value
            
            if not email or not senha:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Preencha todos os campos!"))
                )
                return
            
            if self.db.atualizar_operador(email, senha, ativo):
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Operador atualizado com sucesso!"))
                )
                email_operador.value = ""
                senha_operador.value = ""
                switch_operador_ativo.value = True
                btn_adicionar.text = "Adicionar Operador"
                btn_adicionar.on_click = self.adicionar_operador
                await self.atualizar_area_administrativa()
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Erro ao atualizar operador!"))
                )
            await self.page.update_async()
        
        async def excluir_operador(self, email):
            """Exclui um operador."""
            if self.db.excluir_operador(email):
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Operador excluído com sucesso!"))
                )
                await self.atualizar_area_administrativa()
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Erro ao excluir operador!"))
                )
            await self.page.update_async()
        
        # Botão de adicionar
        btn_adicionar = ft.ElevatedButton(
            "Adicionar Operador",
            icon=ft.icons.ADD,
            on_click=lambda e: asyncio.create_task(self.adicionar_operador(e)),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
            ),
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )
        
        # Atualizar lista inicial
        #asyncio.create_task(self.atualizar_lista_operadores())
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Gerenciar Operadores",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    email_operador,
                                    ft.Container(height=10),
                                    senha_operador,
                                    ft.Container(height=10),
                                    switch_operador_ativo
                                ],
                                spacing=0
                            ),
                            ft.Container(width=20),
                            ft.Column(
                                [
                                    ft.Container(height=20),
                                    btn_adicionar
                                ],
                                spacing=0
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Container(height=20),
                    tabela_operadores
                ],
                spacing=0
            ),
            padding=20
        )

    async def atualizar_area_administrativa(self):
        """Atualiza todas as listas da área administrativa."""
        await self.atualizar_lista_empresas()
        await self.atualizar_lista_usuarios()
        await self.atualizar_lista_operadores()
        await self.page.update_async()

    async def atualizar_lista_empresas(self):
        """Atualiza a lista de empresas na tabela."""
        if hasattr(self, 'tabela_empresas') and self.tabela_empresas:
            self.tabela_empresas.rows.clear()
            for emp in self.db.get_todas_empresas():
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
                                        on_click=lambda e: asyncio.create_task(self.editar_empresa(e.control.data))
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        icon_color=ft.colors.RED_400,
                                        tooltip="Excluir",
                                        data=emp["codigo"],
                                        on_click=lambda e: asyncio.create_task(self.excluir_empresa(e.control.data))
                                    )
                                ])
                            )
                        ]
                    )
                )
            await self.page.update_async()

    async def atualizar_lista_usuarios(self):
        """Atualiza a lista de usuários na tabela."""
        if hasattr(self, 'tabela_usuarios') and self.tabela_usuarios:
            self.tabela_usuarios.rows.clear()
            for user in self.db.get_todos_usuarios():
                # Obter empresas do usuário
                empresas_usuario = self.db.get_empresas_usuario(user["username"])
                empresas_str = ", ".join([f"{emp['codigo']} - {emp['nome']}" for emp in empresas_usuario])
                
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
                                ft.Row([
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        icon_color=ft.colors.BLUE,
                                        tooltip="Editar",
                                        data=user["username"],
                                        on_click=lambda e: asyncio.create_task(self.editar_usuario(e.control.data))
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        icon_color=ft.colors.RED_400,
                                        tooltip="Excluir",
                                        data=user["username"],
                                        on_click=lambda e: asyncio.create_task(self.excluir_usuario(e.control.data))
                                    )
                                ])
                            )
                        ]
                    )
                )
            await self.page.update_async()

    async def atualizar_lista_operadores(self):
        """Atualiza a lista de operadores na tabela."""
        if hasattr(self, 'tabela_operadores') and self.tabela_operadores:
            self.tabela_operadores.rows.clear()
            for operador in self.db.get_todos_operadores():
                self.tabela_operadores.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(operador['email'])),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(
                                        "Ativo" if operador['ativo'] else "Inativo",
                                        color=ft.colors.WHITE,
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                    bgcolor=ft.colors.GREEN if operador['ativo'] else ft.colors.RED_400,
                                    border_radius=15,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5)
                                )
                            ),
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        icon_color=ft.colors.BLUE,
                                        tooltip="Editar",
                                        data=operador['email'],
                                        on_click=lambda e: asyncio.create_task(self.editar_operador(e.control.data))
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        icon_color=ft.colors.RED_400,
                                        tooltip="Excluir",
                                        data=operador['email'],
                                        on_click=lambda e: asyncio.create_task(self.excluir_operador(e.control.data))
                                    )
                                ])
                            )
                        ]
                    )
                )
            await self.page.update_async()

    async def buscar_contratos_api(self, mes, ano, empresa_selecionada, operador_selecionado):
        try:
            # Validar mês e ano
            if not mes or not ano:
                raise ValueError("Mês e ano são obrigatórios")

            # Converter para inteiros
            mes_val = int(mes)
            ano_val = int(ano)

            # Validar valores
            if mes_val < 1 or mes_val > 12:
                raise ValueError("Mês deve estar entre 1 e 12")
            if ano_val < 2000 or ano_val > 2100:
                raise ValueError("Ano inválido")

            # Buscar contratos com os parâmetros da empresa selecionada
            contratos = self.contrato_lg.buscar_contratos_por_mes(
                ano_val, 
                mes_val, 
                tenet_id=empresa_selecionada["tenetID"] if empresa_selecionada else None,
                ambiente=empresa_selecionada["ambiente"] if empresa_selecionada else None,
                operator_email=operador_selecionado["email"] if operador_selecionado else None,
                operator_password=operador_selecionado["senha"] if operador_selecionado else None
            )

            return contratos
        except Exception as e:
            print(f"Erro ao buscar contratos: {e}")
            raise

if __name__ == "__main__":
    app = TelaContratos()
    ft.app(target=app.main) 