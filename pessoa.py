from zeep import Client
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep.helpers import serialize_object
import parametros_conexao as parametros
import time
from typing import Dict, Any, Optional
from datetime import datetime

import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

lista_contatos = []

# Configurar sessão com autenticação básica
session = Session()
session.auth = HTTPBasicAuth(parametros.usuario, parametros.senha)

# Configurar transporte com sessão autenticada
transport = Transport(session=session)

# Plugin para histórico ( útil para debug )
history = HistoryPlugin()

# Criar cliente SOAP com WSDL #/Consultar?wsdl
client = Client(wsdl='https://prd-api1.lg.com.br/v1/ServicoDeColaborador', transport=transport, plugins=[history])


# print("Operações disponíveis no serviço:")
# for service in client.wsdl.services.values():
#     for port in service.ports.values():
#         operations = port.binding._operations.values()
#         for operation in operations:
#             print(f"Operação: {operation.name}")
#             print(f"  Entrada: {operation.input.signature()}")

#             print(f"  Saída: {operation.output.signature()}")


# Ajuste do namespace
header_factory = client.type_factory('ns4')
filtro_factory = client.type_factory('ns1')

# Criar o objeto 'LGContextoAmbiente'
contexto_ambiente = header_factory.LGContextoAmbiente(
    Ambiente=parametros.ambiente
)

# Criar os tokens para autenticação
token_usuario = header_factory.LGTokenUsuario(
    Senha=parametros.senha,
    Usuario=parametros.usuario,
    GuidTenant=parametros.tenetId
)

autenticacao = header_factory.LGAutenticacao(
    TokenUsuario=token_usuario
)
# array_of_int_type = client.get_type('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}ArrayOfint')

filtro = filtro_factory.FiltroDePessoa(
        PessoaId = '707'

    )

try:
    # Atualizar o filtro com o número da página
    # filtro.PaginaAtual = pagina

    # Chamar o serviço Consultar para cada página
    response = client.service.Consultar(
        filtro=filtro,
        _soapheaders={
            "LGContextoAmbiente": contexto_ambiente,
            "LGAutenticacao": autenticacao
        }
    )
    
    # Contatos.obter_dados_contatos( response, lista_contatos )
    
    print( response )
    
    # print(response)
    # Pessoa.obter_dados_pessoa( response, pessoa )
    
    # Calcular o tempo total de execução
    
    
    # total_paginas = response['TotalDePaginas']
    # pagina += 1

except Exception as e:
    # print(f"Erro ao chamar o serviço na página {pagina}: {e}")
    # Log da última solicitação e resposta para depuração
    print("Última solicitação enviada:")
    print( history.last_sent )
    print("Última resposta recebida:")
    print( history.last_received )

end_time = time.time()
# execution_time = end_time - start_time
# print(f'O tempo de processamento foi de {execution_time:.4f} segundos')

class PessoaLG:
    def __init__(self):
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Inicializa o cliente WSDL com as configurações do LG."""
        params = config.get_client_params()
        self.client = Client(
            params['wsdl_url'],
            timeout=params['timeout']
        )

    def buscar_dados_pessoais(self, cpf: str) -> Optional[Dict[str, Any]]:
        """
        Busca dados pessoais de um funcionário pelo CPF.
        
        Args:
            cpf (str): CPF do funcionário
            
        Returns:
            Optional[Dict[str, Any]]: Dados pessoais do funcionário ou None se não encontrado
        """
        try:
            # Chama a operação de busca de pessoa
            result = self.client.service.buscarPessoa(
                cpf=cpf,
                **config.get_auth_params()
            )
            
            if not result:
                return None
                
            # Formata os dados retornados
            return {
                'nome': result.nome,
                'cpf': result.cpf,
                'data_nascimento': self._format_date(result.dataNascimento),
                'email': result.email,
                'telefone': result.telefone,
                'endereco': {
                    'logradouro': result.endereco.logradouro,
                    'numero': result.endereco.numero,
                    'complemento': result.endereco.complemento,
                    'bairro': result.endereco.bairro,
                    'cidade': result.endereco.cidade,
                    'estado': result.endereco.estado,
                    'cep': result.endereco.cep
                }
            }
        except Exception as e:
            print(f"Erro ao buscar dados pessoais: {str(e)}")
            return None

    def _format_date(self, date_str: str) -> str:
        """Formata a data para o padrão brasileiro."""
        try:
            if not date_str:
                return None
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d/%m/%Y")
        except:
            return date_str

# Exemplo de uso
if __name__ == "__main__":
    pessoa = PessoaLG()
    dados = pessoa.buscar_dados_pessoais("123.456.789-00")
    if dados:
        print("Dados encontrados:")
        print(dados)
    else:
        print("Pessoa não encontrada")

