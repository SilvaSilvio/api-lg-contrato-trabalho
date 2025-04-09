from models.empresa import EmpresaModel

class EmpresaController:
    def __init__(self, model=None):
        self.model = model or EmpresaModel()
    
    def get_todas_empresas(self):
        """Retorna todas as empresas cadastradas."""
        return self.model.get_todas_empresas()
    
    def get_empresa(self, codigo):
        """Retorna uma empresa específica pelo código."""
        return self.model.get_empresa(codigo)
    
    def criar_empresa(self, codigo, nome, tenet_id, ambiente):
        """Cria uma nova empresa."""
        # Validações
        if not codigo or not nome or not tenet_id or not ambiente:
            return False, "Todos os campos são obrigatórios"
        
        # Verificar se a empresa já existe
        if self.model.get_empresa(codigo):
            return False, "Empresa com este código já existe"
        
        # Criar empresa
        sucesso, mensagem = self.model.criar_empresa(codigo, nome, tenet_id, ambiente)
        return sucesso, mensagem
    
    def atualizar_empresa(self, codigo_original, codigo, nome, tenet_id, ambiente):
        """Atualiza os dados de uma empresa existente."""
        # Validações
        if not codigo or not nome or not tenet_id or not ambiente:
            return False, "Todos os campos são obrigatórios"
        
        # Verificar se a empresa existe
        if not self.model.get_empresa(codigo_original):
            return False, "Empresa não encontrada"
        
        # Verificar se o novo código já existe (se for diferente do original)
        if codigo != codigo_original and self.model.get_empresa(codigo):
            return False, "Já existe uma empresa com este código"
        
        # Atualizar empresa
        if self.model.atualizar_empresa(codigo_original, codigo, nome, tenet_id, ambiente):
            return True, "Empresa atualizada com sucesso"
        else:
            return False, "Erro ao atualizar empresa"
    
    def excluir_empresa(self, codigo):
        """Exclui uma empresa."""
        # Excluir empresa
        if self.model.excluir_empresa(codigo):
            return True, "Empresa excluída com sucesso"
        else:
            return False, "Erro ao excluir empresa"
    
    def get_empresas_usuario(self, username):
        """Retorna as empresas associadas a um usuário."""
        return self.model.get_empresas_usuario(username) 