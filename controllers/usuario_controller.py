from models.usuario import UsuarioModel
from models.empresa import EmpresaModel

class UsuarioController:
    def __init__(self, usuario_model=None, empresa_model=None):
        self.usuario_model = usuario_model or UsuarioModel()
        self.empresa_model = empresa_model or EmpresaModel()
    
    def get_todos_usuarios(self):
        """Retorna todos os usuários cadastrados."""
        return self.usuario_model.get_todos_usuarios()
    
    def get_usuario(self, username):
        """Retorna um usuário específico pelo nome de usuário."""
        return self.usuario_model.get_usuario(username)
    
    def criar_usuario(self, username, nome, senha, is_admin, empresas):
        """Cria um novo usuário."""
        # Validações
        if not username or not nome or not senha:
            return False, "Nome de usuário, nome completo e senha são obrigatórios"
        
        # Verificar se o usuário já existe
        if self.usuario_model.get_usuario(username):
            return False, "Usuário com este nome já existe"
        
        # Verificar se pelo menos uma empresa foi selecionada
        if not empresas:
            return False, "Selecione pelo menos uma empresa"
        
        # Criar usuário
        if self.usuario_model.criar_usuario(username, nome, senha, is_admin, empresas):
            return True, "Usuário criado com sucesso"
        else:
            return False, "Erro ao criar usuário"
    
    def atualizar_usuario(self, username_original, username, nome, senha, is_admin, empresas):
        """Atualiza os dados de um usuário existente."""
        # Validações
        if not username or not nome:
            return False, "Nome de usuário e nome completo são obrigatórios"
        
        # Verificar se o usuário existe
        if not self.usuario_model.get_usuario(username_original):
            return False, "Usuário não encontrado"
        
        # Verificar se o novo nome de usuário já existe (se for diferente do original)
        if username != username_original and self.usuario_model.get_usuario(username):
            return False, "Já existe um usuário com este nome"
        
        # Verificar se pelo menos uma empresa foi selecionada
        if not empresas:
            return False, "Selecione pelo menos uma empresa"
        
        # Atualizar usuário
        if self.usuario_model.atualizar_usuario(username_original, username, nome, senha, is_admin, empresas):
            return True, "Usuário atualizado com sucesso"
        else:
            return False, "Erro ao atualizar usuário"
    
    def excluir_usuario(self, username):
        """Exclui um usuário."""
        # Verificar se o usuário existe
        if not self.usuario_model.get_usuario(username):
            return False, "Usuário não encontrado"
        
        # Excluir usuário
        if self.usuario_model.excluir_usuario(username):
            return True, "Usuário excluído com sucesso"
        else:
            return False, "Erro ao excluir usuário"
    
    def verificar_login(self, username, senha):
        """Verifica se as credenciais de login são válidas."""
        return self.usuario_model.verificar_login(username, senha)
    
    def get_permissoes_usuario(self, username):
        """Retorna as permissões de um usuário."""
        return self.usuario_model.get_permissoes_usuario(username)
    
    def get_empresas_usuario(self, username):
        """Retorna as empresas associadas a um usuário."""
        return self.empresa_model.get_empresas_usuario(username) 