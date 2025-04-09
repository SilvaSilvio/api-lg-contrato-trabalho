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
        # Log de entrada do método
        print("\n" + "=" * 70)
        print("DEPURAÇÃO DO CONTROLLER - MÉTODO BUSCAR_CONTRATOS")
        print("=" * 70)
        print(f"Parâmetros recebidos:")
        print(f"  - mês: {mes} (tipo: {type(mes)})")
        print(f"  - ano: {ano} (tipo: {type(ano)})")
        print(f"  - código empresa: {codigo_empresa} (tipo: {type(codigo_empresa)})")
        print(f"  - email operador: {email_operador} (tipo: {type(email_operador)})")
        
        # Validações
        if not mes or not ano:
            print("ERRO: Mês e ano são obrigatórios")
            return [], "Mês e ano são obrigatórios"
        
        try:
            mes_val = int(mes)
            ano_val = int(ano)
            
            if mes_val < 1 or mes_val > 12:
                print(f"ERRO: Mês inválido: {mes_val}")
                return [], "Mês deve estar entre 1 e 12"
            
            if ano_val < 2000 or ano_val > 2100:
                print(f"ERRO: Ano inválido: {ano_val}")
                return [], "Ano inválido"
                
            print(f"Validação de mês e ano OK: {mes_val}/{ano_val}")
        except ValueError:
            print(f"ERRO: Valores inválidos para conversão: mês={mes}, ano={ano}")
            return [], "Mês e ano devem ser números válidos"
        
        # Obter empresa selecionada
        empresa_selecionada = None
        if codigo_empresa:
            print(f"Buscando empresa com código: {codigo_empresa}")
            empresa_selecionada = self.empresa_model.get_empresa(codigo_empresa)
            if not empresa_selecionada:
                print(f"ERRO: Empresa não encontrada para o código: {codigo_empresa}")
                return [], "Empresa não encontrada"
            print(f"Empresa encontrada: {empresa_selecionada}")
        else:
            print("Nenhuma empresa específica selecionada, usando configuração padrão")
        
        # Obter operador selecionado e suas credenciais
        operador_selecionado = None
        operator_password = None
        if email_operador:
            print(f"Buscando operador com email: {email_operador}")
            operador_selecionado = self.operador_model.get_operador(email_operador)
            if not operador_selecionado:
                print(f"ERRO: Operador não encontrado para o email: {email_operador}")
                return [], "Operador não encontrado"
            print(f"Operador encontrado: {operador_selecionado}")
            
            # Se o operador selecionado for o mesmo do arquivo .env, usar a senha do .env
            import parametros_conexao
            if email_operador == parametros_conexao.config.username:
                operator_password = parametros_conexao.config.password
            else:
                operator_password = operador_selecionado['senha']
        else:
            print("Nenhum operador específico selecionado, usando credenciais padrão")
        
        # Buscar contratos
        try:
            print("\nIniciando busca de contratos com os seguintes parâmetros:")
            print(f"  - ano: {ano_val}")
            print(f"  - mês: {mes_val}")
            print(f"  - tenet_id: {empresa_selecionada['tenetID'] if empresa_selecionada else 'padrão'}")
            print(f"  - ambiente: {empresa_selecionada['ambiente'] if empresa_selecionada else 'padrão'}")
            print(f"  - operator_email: {operador_selecionado['email'] if operador_selecionado else 'padrão'}")
            print(f"  - operator_password: {'*****' if operator_password else 'padrão'}")
            
            contratos = self.contrato_model.buscar_contratos_por_mes(
                ano_val, 
                mes_val, 
                tenet_id=empresa_selecionada["tenetID"] if empresa_selecionada else None,
                ambiente=empresa_selecionada["ambiente"] if empresa_selecionada else None,
                operator_email=operador_selecionado["email"] if operador_selecionado else None,
                operator_password=operator_password
            )
            
            print(f"\nContratos retornados pelo model: {len(contratos)}")
            
            # Filtrar por empresa selecionada
            if codigo_empresa:
                print(f"Filtrando contratos para a empresa com código: {codigo_empresa}")
                contratos_antes = len(contratos)
                contratos = self.contrato_model.filtrar_contratos_por_empresa(contratos, codigo_empresa)
                print(f"Total após filtro por empresa: {len(contratos)} (removidos: {contratos_antes - len(contratos)})")
            
            print("=" * 70)
            return contratos, f"Encontrados {len(contratos)} contratos"
        except Exception as e:
            import traceback
            print(f"ERRO AO BUSCAR CONTRATOS: {str(e)}")
            print(traceback.format_exc())
            print("=" * 70)
            return [], f"Erro ao buscar contratos: {str(e)}" 