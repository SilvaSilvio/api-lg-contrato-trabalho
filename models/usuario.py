from database import Database

class UsuarioModel:
    def __init__(self, db=None):
        self.db = db or Database()
    
    def get_todos_usuarios(self):
        """Retorna todos os usuários cadastrados."""
        return self.db.get_todos_usuarios()
    
    def get_usuario(self, username):
        """Retorna um usuário específico pelo nome de usuário."""
        return self.db.get_usuario(username)
    
    def criar_usuario(self, username, nome, senha, is_admin, empresas):
        """Cria um novo usuário."""
        return self.db.criar_usuario(username, nome, senha, is_admin, empresas)
    
    def atualizar_usuario(self, username_original, username, nome, senha, is_admin, empresas):
        """Atualiza os dados de um usuário existente."""
        return self.db.atualizar_usuario(username, nome, senha, is_admin, empresas)
    
    def excluir_usuario(self, username):
        """Exclui um usuário."""
        return self.db.excluir_usuario(username)
    
    def verificar_login(self, username, senha):
        """Verifica se as credenciais de login são válidas."""
        return self.db.verificar_login(username, senha)
    
    def get_permissoes_usuario(self, username):
        """Retorna as permissões de um usuário."""
        return self.db.get_permissoes_usuario(username) 