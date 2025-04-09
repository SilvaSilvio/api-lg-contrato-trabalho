from database import Database

class EmpresaModel:
    def __init__(self, db=None):
        self.db = db or Database()
    
    def get_todas_empresas(self):
        """Retorna todas as empresas cadastradas."""
        return self.db.get_todas_empresas()
    
    def get_empresa(self, codigo):
        """Retorna uma empresa específica pelo código."""
        return self.db.get_empresa(codigo)
    
    def criar_empresa(self, codigo, nome, tenet_id, ambiente):
        """Cria uma nova empresa."""
        return self.db.criar_empresa(codigo, nome, tenet_id, ambiente)
    
    def atualizar_empresa(self, codigo_original, codigo, nome, tenet_id, ambiente):
        """Atualiza os dados de uma empresa existente."""
        return self.db.atualizar_empresa(codigo_original, codigo, nome, tenet_id, ambiente)
    
    def excluir_empresa(self, codigo):
        """Exclui uma empresa."""
        return self.db.excluir_empresa(codigo)
    
    def get_empresas_usuario(self, username):
        """Retorna as empresas associadas a um usuário."""
        return self.db.get_empresas_usuario(username) 