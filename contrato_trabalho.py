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
    # URL fixa do WSDL
    WSDL_URL = 'https://prd-api1.lg.com.br/v1/ServicoDeContratoDeTrabalho'

    def __init__(self):
        self.client = None
        # Remover inicialização das credenciais no construtor
        # self.operator_email = None
        # self.operator_password = None
        # self.tenet_id = None
        # self.ambiente = None
        # self.wsdl_url = None
        # self._initialize_client()

    def _initialize_client(self, operator_email: str, operator_password: str, tenet_id: str, ambiente: str):
        """Inicializa o cliente WSDL com as credenciais fornecidas."""
        if not all([operator_email, operator_password, tenet_id, ambiente]):
            raise ValueError("Todos os parâmetros são obrigatórios: operator_email, operator_password, tenet_id, ambiente")

        # Criar sessão com autenticação básica
        session = Session()
        session.auth = HTTPBasicAuth(operator_email, operator_password)
        
        # Criar transporte com a sessão autenticada
        transport = Transport(session=session)
        
        # Plugin para histórico (útil para debug)
        history = HistoryPlugin()

        # Criar cliente SOAP com WSDL
        self.client = Client(
            wsdl=self.WSDL_URL,
            transport=transport,
            plugins=[history]
        )

    def buscar_contratos_mes_atual(self, operator_email, operator_password, tenet_id, ambiente) -> List[Dict[str, Any]]:
        """
        Busca contratos com data de admissão no mês atual.
        
        Returns:
            List[Dict[str, Any]]: Lista de contratos do mês atual
        """
        hoje = date.today()
        return self.buscar_contratos_por_mes(hoje.year, hoje.month, tenet_id, ambiente, operator_email, operator_password)

    def buscar_contratos_por_mes(self, ano: int, mes: int, tenet_id: str, ambiente: str, operator_email: str, operator_password: str) -> List[Dict[str, Any]]:
        """
        Busca contratos com data de admissão em um mês específico.
        
        Args:
            ano: Ano para filtrar (ex: 2025)
            mes: Mês para filtrar (1-12, ex: 4 para abril)
            tenet_id: ID do tenant no sistema (obrigatório)
            ambiente: Ambiente (obrigatório)
            operator_email: Email do operador para autenticação (obrigatório)
            operator_password: Senha do operador para autenticação (obrigatório)
            
        Returns:
            List[Dict[str, Any]]: Lista de contratos do mês especificado
        """
        try:
            # Log detalhado dos parâmetros recebidos
            print("\n" + "=" * 80)
            print("DEPURAÇÃO DE CONTRATO_TRABALHO - MÉTODO BUSCAR_CONTRATOS_POR_MES")
            print("=" * 80)
            print(f"Parâmetros recebidos:")
            print(f"  - ano: {ano} (tipo: {type(ano)})")
            print(f"  - mês: {mes} (tipo: {type(mes)})")
            print(f"  - tenet_id: {tenet_id} (tipo: {type(tenet_id)})")
            print(f"  - ambiente: {ambiente} (tipo: {type(ambiente)})")
            print(f"  - operator_email: {operator_email} (tipo: {type(operator_email)})")
            print(f"  - operator_password: {'***' if operator_password else None} (tipo: {type(operator_password)})")
            print(f"  - wsdl_url: {self.WSDL_URL}")
            
            # Validar parâmetros obrigatórios
            if not all([tenet_id, ambiente, operator_email, operator_password]):
                raise ValueError("Todos os parâmetros são obrigatórios: tenet_id, ambiente, operator_email, operator_password")
            
            # Reinicializar cliente com as credenciais fornecidas
            self._initialize_client(
                operator_email=operator_email,
                operator_password=operator_password,
                tenet_id=tenet_id,
                ambiente=ambiente
            )
            
            # Obter primeiro dia do mês especificado
            data_referencia = date(ano, mes, 1)
            print(f"  - data_referencia: {data_referencia} (primeiro dia do mês)")

            # Ajuste do namespace
            header_factory = self.client.type_factory('ns3')
            filtro_factory = self.client.type_factory('ns1')

            # Criar o objeto 'LGContextoAmbiente'
            contexto_ambiente = header_factory.LGContextoAmbiente(
                Ambiente=ambiente
            )

            # Criar os tokens para autenticação
            token_usuario = header_factory.LGTokenUsuario(
                Senha=operator_password,
                Usuario=operator_email,
                GuidTenant=tenet_id
            )

            autenticacao = header_factory.LGAutenticacao(
                TokenUsuario=token_usuario
            )
            
            print(f"\nDados de autenticação preparados:")
            print(f"  - Usuario: {operator_email}")
            print(f"  - Senha: {'***' if operator_password else None}")
            print(f"  - GuidTenant: {tenet_id}")
            print(f"  - Ambiente: {ambiente}")

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
                
                # Criar filtro com paginação - sem filtrar por empresa
                filtro = filtro_factory.FiltroDeContratoPorDemanda(
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
    # contratos = contrato.buscar_contratos_por_mes(2025, 4)
    
    # if contratos:
    #     print(f"\nEncontrados {len(contratos)} contratos no mês especificado:")
    #     for contrato in contratos:
    #         print("\nContrato:")
    #         for key, value in contrato.items():
    #             print(f"{key}: {value}")
    # else:
    #     print("Nenhum contrato encontrado para o mês especificado.") 