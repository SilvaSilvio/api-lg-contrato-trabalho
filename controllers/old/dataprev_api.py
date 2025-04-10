import requests
from typing import Dict, Any, Optional
import json
import os
from dotenv import load_dotenv

class DataPrevAPI:
    def __init__(self):
        self.base_url = "https://apigateway.conectagov.estaleiro.serpro.gov.br/api-beneficios-previdenciarios/v3"
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Obter credenciais do arquivo .env
        self.api_key = os.getenv('DATAPREV_API_KEY')
        self.client_id = os.getenv('DATAPREV_CLIENT_ID')
        self.client_secret = os.getenv('DATAPREV_CLIENT_SECRET')
        
        if not all([self.api_key, self.client_id, self.client_secret]):
            raise ValueError("Credenciais da API DataPrev não encontradas no arquivo .env")
        
    def buscar_beneficios(self, cpf: str) -> Dict[str, Any]:
        """
        Busca benefícios previdenciários de uma pessoa pelo CPF.
        
        Args:
            cpf (str): CPF da pessoa (apenas números)
            
        Returns:
            Dict[str, Any]: Dados dos benefícios ou mensagem de erro
        """
        try:
            # Formatar URL com o CPF
            url = f"{self.base_url}/beneficios?cpf={cpf}"
            
            # Headers de autenticação
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Client-Id': self.client_id,
                'Client-Secret': self.client_secret,
                'Content-Type': 'application/json'
            }
            
            # Fazer a requisição GET com os headers
            response = requests.get(url, headers=headers)
            
            # Verificar se a requisição foi bem sucedida
            response.raise_for_status()
            
            # Retornar os dados em formato JSON
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar benefícios: {str(e)}")
            return {
                "erro": True,
                "mensagem": f"Erro ao buscar benefícios: {str(e)}"
            }
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar resposta: {str(e)}")
            return {
                "erro": True,
                "mensagem": "Erro ao processar resposta do servidor"
            }
        except Exception as e:
            print(f"Erro inesperado: {str(e)}")
            return {
                "erro": True,
                "mensagem": "Erro inesperado ao buscar benefícios"
            }

# Exemplo de uso:
if __name__ == "__main__":
    api = DataPrevAPI()
    resultado = api.buscar_beneficios("02075527202")  # Substitua pelo CPF desejado
    print(json.dumps(resultado, indent=2, ensure_ascii=False)) 