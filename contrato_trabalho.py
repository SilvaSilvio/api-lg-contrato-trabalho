from zeep import Client
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
from requests import Session
from requests.auth import HTTPBasicAuth
from datetime import datetime, date
from typing import Dict, Any, Optional, List
import time
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

#from parametros_conexao import usuario, senha, ambiente, tenetId, config

class ContratoTrabalhoLG:
    def __init__(self):
        self.client = None
        self.operator_email = None
        self.operator_password = None
        self._initialize_client()

    def _initialize_client(self, operator_email=None, operator_password=None):
        """Inicializa o cliente WSDL com as configurações do LG."""
        # Armazenar credenciais do operador se fornecidas
        self.operator_email = operator_email
        self.operator_password = operator_password
        
        # Usar credenciais do operador se fornecidas, caso contrário usar as padrão
        auth_username = operator_email # if operator_email else usuario
        auth_password = operator_password # if operator_password else senha
        
        print(f"auth_username: {auth_username}")
        print(f"auth_password: {auth_password}")
        
        
        # Configurar sessão com autenticação básica
        session = Session()
        session.auth = HTTPBasicAuth(auth_username, auth_password)

        # Configurar transporte com sessão autenticada
        transport = Transport(session=session)

        # Plugin para histórico (útil para debug)
        history = HistoryPlugin()

        # Criar cliente SOAP com WSDL
        self.client = Client(
            wsdl='https://prd-api1.lg.com.br/v1/ServicoDeContratoDeTrabalho',
            transport=transport,
            plugins=[history]
        )

    def buscar_contratos_mes_atual(self) -> List[Dict[str, Any]]:
        """
        Busca contratos com data de admissão no mês atual.
        
        Returns:
            List[Dict[str, Any]]: Lista de contratos do mês atual
        """
        hoje = date.today()
        return self.buscar_contratos_por_mes(hoje.year, hoje.month)

    def buscar_contratos_por_mes(self, ano: int, mes: int, tenet_id: str = None, ambiente: str = None, operator_email: str = None, operator_password: str = None) -> List[Dict[str, Any]]:
        """
        Busca contratos com data de admissão em um mês específico.
        
        Args:
            ano: Ano para filtrar (ex: 2025)
            mes: Mês para filtrar (1-12, ex: 4 para abril)
            tenet_id: ID do tenant no sistema (opcional, usa o valor padrão se não fornecido)
            ambiente: Ambiente (opcional, usa o valor padrão se não fornecido)
            operator_email: Email do operador para autenticação (opcional)
            operator_password: Senha do operador para autenticação (opcional)
            
        Returns:
            List[Dict[str, Any]]: Lista de contratos do mês especificado
        """
        try:
            # Se credenciais de operador foram fornecidas, reinicializar o cliente
            if operator_email and operator_password:
                self._initialize_client(operator_email, operator_password)
            
            # Usar os parâmetros fornecidos ou os valores padrão
            tenet_id_to_use = tenet_id if tenet_id is not None else tenetId
            ambiente_to_use = ambiente if ambiente is not None else ambiente
            
            print(f"tenet_id_to_use: {tenet_id_to_use}")
            print(f"ambiente_to_use: {ambiente_to_use}")
            
            # Obter primeiro dia do mês especificado
            data_referencia = date(ano, mes, 1)

            # Ajuste do namespace
            header_factory = self.client.type_factory('ns3')
            filtro_factory = self.client.type_factory('ns1')

            # Criar o objeto 'LGContextoAmbiente'
            contexto_ambiente = header_factory.LGContextoAmbiente(
                Ambiente=ambiente_to_use
            )

            # Criar os tokens para autenticação
            token_usuario = header_factory.LGTokenUsuario(
                Senha=self.operator_password, # if self.operator_password else senha,
                Usuario=self.operator_email, # if self.operator_email else usuario,
                GuidTenant=tenet_id_to_use
            )

            autenticacao = header_factory.LGAutenticacao(
                TokenUsuario=token_usuario
            )

            # Criar o tipo para Empresas
            filtro_com_codigo_type = self.client.get_type('{lg.com.br/api/dto/v1}FiltroComCodigoNumerico')
            empresas_type = self.client.get_type('{lg.com.br/api/dto/v1}ArrayOfFiltroComCodigoNumerico')
            
            # Criar o objeto de empresa
            empresa = filtro_com_codigo_type(Codigo='1')
            empresas = empresas_type([empresa])

            # Criar o filtro específico para DATA_ADMISSAO
            filtro_especifico_type = self.client.get_type('{lg.com.br/api/dto/v1}FiltroDeCamposEspecificos')
            array_filtro_especifico_type = self.client.get_type('{lg.com.br/api/dto/v1}ArrayOfFiltroDeCamposEspecificos')

            # Criar filtro para DATA_ADMISSAO - usando operação de maior ou igual
            # Operação 4 = Maior ou igual
            filtro_data_admissao = filtro_especifico_type(
                Campo=2,  # 2 = DATA_ADMISSAO
                Operacao=4,  # Operação de maior ou igual
                ValoresParaFiltrar=[
                    data_referencia.strftime("%Y-%m-%d")
                ]
            )

            # Criar array de filtros específicos
            filtros_especificos = array_filtro_especifico_type([filtro_data_admissao])

            # Lista para armazenar todos os contratos
            todos_contratos = []
            pagina = 0
            total_paginas = None  # Será atualizado com o valor real na primeira chamada

            # Loop para buscar todas as páginas
            while True:
                print(f'Buscando página {pagina + 1}...')
                
                # Criar filtro com paginação
                filtro = filtro_factory.FiltroDeContratoPorDemanda(
                    Empresas=empresas,
                    PaginaAtual=pagina,
                    FiltrosEspecificos=filtros_especificos
                )

                # Chamar o serviço
                response = self.client.service.ConsultarListaPorDemanda(
                    filtro=filtro,
                    _soapheaders={
                        "LGContextoAmbiente": contexto_ambiente,
                        "LGAutenticacao": autenticacao
                    }
                )
                
                print("Resposta completa:")
                print(response)

                if not response:
                    print("Resposta vazia recebida do servidor")
                    break

                # Na primeira chamada, obter o total de páginas
                if total_paginas is None:
                    total_paginas = response.TotalDePaginas
                    print(f'Total de páginas a serem buscadas: {total_paginas}')

                # Processar contratos da página atual
                if hasattr(response, 'Retorno') and hasattr(response.Retorno, 'ContratoDeTrabalhoParcial'):
                    contratos_pagina = response.Retorno.ContratoDeTrabalhoParcial
                    for contrato in contratos_pagina:
                        data_admissao = contrato.DataAdmissao.date()
                        # Adicionar todos os contratos com data de admissão >= data_referencia
                        todos_contratos.append({
                            'nome': contrato.Pessoa.Nome,
                            'cpf': contrato.Pessoa.Cpf,
                            'data_admissao': self._format_date(str(data_admissao)),
                            'cargo': contrato.Cargo.Descricao,
                            'departamento': contrato.CentroDeCusto.Descricao,
                            'matricula': contrato.Matricula,
                            'situacao': contrato.SituacaoDoColaborador.Descricao,
                            'empresa': {
                                'Codigo': contrato.Empresa.Codigo
                            }
                        })
                    print(f'Contratos encontrados na página {pagina + 1}: {len(contratos_pagina)}')
                else:
                    print(f'Nenhum contrato encontrado na página {pagina + 1}')

                # Incrementar página
                pagina += 1

                # Verificar se já buscamos todas as páginas
                if pagina >= total_paginas:
                    print(f'Buscamos todas as {total_paginas} páginas disponíveis')
                    break

                # Pequena pausa para não sobrecarregar o servidor
                time.sleep(0.5)

            print(f'Total de contratos encontrados com data de admissão a partir de {self._format_date(str(data_referencia))}: {len(todos_contratos)}')
            
            # Ordenar contratos por data de admissão
            todos_contratos.sort(key=lambda x: datetime.strptime(x['data_admissao'], '%d/%m/%Y'))
            
            # Imprimir detalhes de cada contrato
            if todos_contratos:
                print("\nContratos encontrados:")
                for contrato in todos_contratos:
                    print(f"\nMatrícula: {contrato['matricula']}")
                    print(f"Nome: {contrato['nome']}")
                    print(f"Data Admissão: {contrato['data_admissao']}")
                    print(f"Cargo: {contrato['cargo']}")
                    print(f"Departamento: {contrato['departamento']}")
                    print(f"Situação: {contrato['situacao']}")
            
            return todos_contratos

        except Exception as e:
            print(f"Erro ao buscar contratos do mês {mes}/{ano}: {str(e)}")
            # Imprimir detalhes do erro para debug
            import traceback
            traceback.print_exc()
            return []

    def _format_date(self, date_str: str) -> str:
        """Formata a data para o padrão brasileiro."""
        try:
            if not date_str:
                return None
            date_obj = datetime.strptime( date_str, "%Y-%m-%d" )
            return date_obj.strftime("%d/%m/%Y")
        except:
            return date_str

# Exemplo de uso
if __name__ == "__main__":
    contrato = ContratoTrabalhoLG()
    
    # Busca contratos do mês atual
    # contratos = contrato.buscar_contratos_mes_atual()
    
    # Busca contratos de um mês específico (abril/2025)
    contratos = contrato.buscar_contratos_por_mes(2025, 4)
    
    if contratos:
        print(f"\nEncontrados {len(contratos)} contratos no mês especificado:")
        for contrato in contratos:
            print("\nContrato:")
            for key, value in contrato.items():
                print(f"{key}: {value}")
    else:
        print("Nenhum contrato encontrado para o mês especificado.") 