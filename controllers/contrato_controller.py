from models.contrato import ContratoModel
from models.empresa import EmpresaModel
from models.operador import OperadorModel

class ContratoController:
    def __init__(self, contrato_model=None, empresa_model=None, operador_model=None):
        self.contrato_model = contrato_model or ContratoModel()
        self.empresa_model = empresa_model or EmpresaModel()
        self.operador_model = operador_model or OperadorModel()
    
    def buscar_contratos(self, mes, ano, codigo_empresa=None, email_operador=None):
        """Busca contratos com base nos filtros fornecidos."""
        # Validações
        if not mes or not ano:
            return [], "Mês e ano são obrigatórios"
        
        try:
            mes_val = int(mes)
            ano_val = int(ano)
            
            if mes_val < 1 or mes_val > 12:
                return [], "Mês deve estar entre 1 e 12"
            
            if ano_val < 2000 or ano_val > 2100:
                return [], "Ano inválido"
        except ValueError:
            return [], "Mês e ano devem ser números válidos"
        
        # Obter empresa selecionada
        empresa_selecionada = None
        if codigo_empresa:
            empresa_selecionada = self.empresa_model.get_empresa(codigo_empresa)
            if not empresa_selecionada:
                return [], "Empresa não encontrada"
        
        # Obter operador selecionado
        operador_selecionado = None
        if email_operador:
            operador_selecionado = self.operador_model.get_operador(email_operador)
            if not operador_selecionado:
                return [], "Operador não encontrado"
        
        # Buscar contratos
        try:
            contratos = self.contrato_model.buscar_contratos_por_mes(
                ano_val, 
                mes_val, 
                tenet_id=empresa_selecionada["tenetID"] if empresa_selecionada else None,
                ambiente=empresa_selecionada["ambiente"] if empresa_selecionada else None,
                operator_email=operador_selecionado["email"] if operador_selecionado else None,
                operator_password=operador_selecionado["senha"] if operador_selecionado else None
            )
            
            # Filtrar por empresa selecionada
            if codigo_empresa:
                contratos = self.contrato_model.filtrar_contratos_por_empresa(contratos, codigo_empresa)
            
            return contratos, f"Encontrados {len(contratos)} contratos"
        except Exception as e:
            return [], f"Erro ao buscar contratos: {str(e)}" 