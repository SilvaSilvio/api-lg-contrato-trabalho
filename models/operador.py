from database import Database

class OperadorModel:
    def __init__(self, db=None):
        self.db = db or Database()
    
    def get_todos_operadores(self):
        """Retorna todos os operadores cadastrados."""
        return self.db.get_todos_operadores()
    
    def get_operador(self, email):
        """Retorna um operador específico pelo email."""
        return self.db.get_operador(email)
    
    def adicionar_operador(self, email, senha, ativo=True):
        """Adiciona um novo operador."""
        return self.db.adicionar_operador(email, senha, ativo)
    
    def atualizar_operador(self, email_original: str, email: str, senha: str, ativo: bool) -> None:
        """
        Atualiza um operador existente.
        
        Args:
            email_original (str): Email original do operador a ser atualizado
            email (str): Novo email do operador
            senha (str): Nova senha do operador
            ativo (bool): Novo status do operador
            
        Raises:
            ValueError: Se o operador não for encontrado ou se houver erro na atualização
        """
        try:
            # Verifica se o operador existe
            operador = self.get_operador(email_original)
            if not operador:
                raise ValueError(f"Operador com email {email_original} não encontrado")
            
            # Verifica se o novo email já está em uso por outro operador
            if email != email_original:
                operador_existente = self.get_operador(email)
                if operador_existente:
                    raise ValueError(f"Já existe um operador com o email {email}")
            
            # Atualiza o operador
            self.db.atualizar_operador(email_original, email, senha, ativo)
            
        except Exception as e:
            raise ValueError(f"Erro ao atualizar operador: {str(e)}")
    
    def excluir_operador(self, email):
        """Exclui um operador."""
        return self.db.excluir_operador(email) 