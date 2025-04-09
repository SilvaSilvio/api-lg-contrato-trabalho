from contrato_trabalho import ContratoTrabalhoLG

class ContratoModel:
    def __init__(self, contrato_lg=None):
        self.contrato_lg = contrato_lg or ContratoTrabalhoLG()
    
    def buscar_contratos_por_mes(self, ano, mes, tenet_id=None, ambiente=None, operator_email=None, operator_password=None):
        """Busca contratos por mês e ano, com opções de filtro por empresa e operador."""
        return self.contrato_lg.buscar_contratos_por_mes(
            ano, 
            mes, 
            tenet_id=tenet_id,
            ambiente=ambiente,
            operator_email=operator_email,
            operator_password=operator_password
        )
    
    def filtrar_contratos_por_empresa(self, contratos, codigo_empresa):
        """Filtra contratos por código de empresa."""
        if not codigo_empresa:
            return contratos
        
        return [
            contrato for contrato in contratos
            if str(contrato.get('empresa', {}).get('Codigo', '')) == codigo_empresa
        ] 