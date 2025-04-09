from typing import Dict, List, Set, Optional
from database import Database

# Definição dos usuários e suas senhas
USUARIOS = {
    "master": "master123",  # Usuário master com acesso total
    "joao": "joao123",     # Analista João
    "maria": "maria123",   # Analista Maria
    "pedro": "pedro123"    # Analista Pedro
}

# Definição das empresas que cada usuário pode acessar
PERMISSOES_EMPRESAS = {
    "master": ["*"],  # * significa acesso a todas as empresas
    "joao": ["1", "2", "3", "4"],  # Códigos das empresas que João pode acessar
    "maria": ["2", "5", "6"],      # Empresas que Maria pode acessar
    "pedro": ["1", "7", "8", "9"]  # Empresas que Pedro pode acessar
}

class ControleAcesso:
    def __init__(self):
        self.db = Database()
        self.usuario_atual = None
    
    def fazer_login(self, username: str, senha: str) -> bool:
        """Verifica as credenciais e faz o login do usuário."""
        if self.db.verificar_login(username, senha):
            self.usuario_atual = username
            return True
        return False
    
    def fazer_logout(self):
        """Faz o logout do usuário atual."""
        self.usuario_atual = None
    
    def get_usuario_atual(self) -> Optional[str]:
        """Retorna o nome do usuário atual."""
        if self.usuario_atual:
            usuario = self.db.get_usuario(self.usuario_atual)
            return usuario["nome"] if usuario else None
        return None
    
    def get_empresas_permitidas(self) -> List[Dict]:
        """Retorna a lista de empresas que o usuário atual tem permissão para acessar."""
        if not self.usuario_atual:
            return []
        
        usuario = self.db.get_usuario(self.usuario_atual)
        if usuario and usuario["is_admin"]:
            return self.db.get_todas_empresas()
        
        return self.db.get_empresas_permitidas(self.usuario_atual)
    
    def filtrar_contratos(self, contratos: List[Dict]) -> List[Dict]:
        """Filtra os contratos com base nas permissões do usuário atual."""
        if not self.usuario_atual:
            return []
        
        usuario = self.db.get_usuario(self.usuario_atual)
        if usuario and usuario["is_admin"]:
            return contratos
        
        empresas_permitidas = {emp["codigo"] for emp in self.get_empresas_permitidas()}
        print(f"Empresas permitidas para o usuário {self.usuario_atual}: {empresas_permitidas}")
        
        contratos_filtrados = [
            contrato for contrato in contratos
            if str(contrato.get('empresa', {}).get('Codigo', '')) in empresas_permitidas
        ]
        
        print(f"Contratos antes do filtro: {len(contratos)}")
        print(f"Contratos após filtro: {len(contratos_filtrados)}")
        
        return contratos_filtrados
    
    def tem_acesso_empresa(self, codigo_empresa: str) -> bool:
        """Verifica se o usuário atual tem acesso a uma determinada empresa."""
        if not self.usuario_atual:
            return False
        
        usuario = self.db.get_usuario(self.usuario_atual)
        if usuario and usuario["is_admin"]:
            return True
        
        empresas_permitidas = {emp["codigo"] for emp in self.get_empresas_permitidas()}
        return codigo_empresa in empresas_permitidas
    
    def adicionar_usuario(self, username: str, senha: str, nome: str, empresas: List[str]) -> bool:
        """Adiciona um novo usuário ao sistema."""
        return self.db.adicionar_usuario(username, senha, nome, empresas)
    
    def atualizar_usuario(self, username: str, nome: str, empresas: List[str]) -> bool:
        """Atualiza os dados de um usuário existente."""
        return self.db.atualizar_usuario(username, nome, empresas)
    
    def alterar_senha(self, username: str, nova_senha: str) -> bool:
        """Altera a senha de um usuário."""
        return self.db.alterar_senha(username, nova_senha)

    def get_empresas_permitidas_str(self) -> str:
        """Retorna uma string formatada com as empresas permitidas do usuário atual."""
        if not self.usuario_atual:
            return "Nenhum usuário logado"
        
        empresas_permitidas = self.get_empresas_permitidas()
        
        # Se o usuário tem acesso a todas as empresas
        if len(empresas_permitidas) == len(self.db.get_todas_empresas()):
            return "Todas as empresas"
        
        # Retorna uma string formatada com as empresas permitidas
        return ", ".join(emp["nome"] for emp in empresas_permitidas)

    def get_empresas_permitidas_list(self) -> List[Dict]:
        """Retorna uma lista de empresas permitidas para o usuário atual."""
        if not self.usuario_atual:
            return []
        
        empresas_permitidas = self.get_empresas_permitidas()
        
        # Se o usuário tem acesso a todas as empresas
        if len(empresas_permitidas) == len(self.db.get_todas_empresas()):
            return self.db.get_todas_empresas()
        
        # Retorna uma lista de empresas permitidas
        return empresas_permitidas 