# Sistema de Gerenciamento de Contratos de Trabalho

Este sistema permite o gerenciamento de contratos de trabalho, empresas, usuários e operadores, com controle de acesso baseado em permissões.

## Funcionalidades

- **Gerenciamento de Contratos**: Consulta e visualização de contratos de trabalho por mês/ano
- **Gerenciamento de Empresas**: Cadastro, edição e exclusão de empresas
- **Gerenciamento de Usuários**: Cadastro, edição e exclusão de usuários com diferentes níveis de permissão
- **Gerenciamento de Operadores**: Cadastro, edição e exclusão de operadores para acesso à API
- **Controle de Acesso**: Sistema de login com diferentes níveis de permissão por empresa

## Requisitos

- Python 3.8+
- Flet (framework para interface gráfica)
- SQLite (banco de dados)

## Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/nome-do-repositorio.git
   cd nome-do-repositorio
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Configure o banco de dados:
   - Crie um arquivo `.env` na raiz do projeto com as configurações necessárias
   - Exemplo de configuração:
     ```
     DB_PATH=./database.db
     ```

## Uso

Para iniciar o aplicativo:

```
python tela_contratos.py
```

## Estrutura do Projeto

- `tela_contratos.py`: Interface principal do sistema
- `contrato_trabalho.py`: Lógica de negócios para contratos
- `controle_acesso.py`: Gerenciamento de usuários e permissões
- `database.py`: Acesso ao banco de dados

## Configuração de Dados Sensíveis

Para proteger dados sensíveis, crie um arquivo `.env` na raiz do projeto com as seguintes informações:

```
DB_PATH=./database.db
API_URL=https://api.exemplo.com
API_KEY=sua_chave_api
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes. 