import sqlite3
from typing import List, Dict, Optional
import hashlib

class Database:
    def __init__(self, db_file: str = "sistema_contratos.db"):
        self.db_file = db_file
        self.init_database()
        self.corrigir_estrutura_empresas()
        self.verify_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_file)
    
    def corrigir_estrutura_empresas(self):
        """Corrige a estrutura da tabela empresas se necessário."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar se a coluna tenetID existe
            cursor.execute("PRAGMA table_info(empresas)")
            colunas = [col[1] for col in cursor.fetchall()]
            
            if 'tenetID' not in colunas:
                # Fazer backup dos dados existentes
                cursor.execute("SELECT codigo, nome FROM empresas")
                dados_antigos = cursor.fetchall()
                
                # Recriar a tabela com a estrutura correta
                cursor.execute("DROP TABLE empresas")
                cursor.execute('''
                    CREATE TABLE empresas (
                        codigo TEXT PRIMARY KEY,
                        nome TEXT NOT NULL,
                        tenetID TEXT NOT NULL,
                        ambiente TEXT NOT NULL
                    )
                ''')
                
                # Restaurar os dados com valores padrão para as novas colunas
                for codigo, nome in dados_antigos:
                    cursor.execute('''
                        INSERT INTO empresas (codigo, nome, tenetID, ambiente)
                        VALUES (?, ?, ?, ?)
                    ''', (codigo, nome, 'tenant1', 'producao'))
                
                conn.commit()
                return True
            return False
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Criar tabela de usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    username TEXT PRIMARY KEY,
                    senha TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    is_admin INTEGER DEFAULT 0
                )
            ''')
            
            # Criar tabela de empresas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS empresas (
                    codigo TEXT PRIMARY KEY,
                    nome TEXT NOT NULL,
                    tenetID TEXT NOT NULL,
                    ambiente TEXT NOT NULL
                )
            ''')
            
            # Criar tabela de permissões
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS permissoes (
                    usuario TEXT,
                    empresa_codigo TEXT,
                    PRIMARY KEY (usuario, empresa_codigo),
                    FOREIGN KEY (usuario) REFERENCES usuarios(username),
                    FOREIGN KEY (empresa_codigo) REFERENCES empresas(codigo)
                )
            ''')
            
            # Criar tabela de operadores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS operadores (
                    email TEXT PRIMARY KEY,
                    senha TEXT NOT NULL,
                    ativo BOOLEAN NOT NULL DEFAULT 1
                )
            ''')
            
            # Inserir dados iniciais se as tabelas estiverem vazias
            cursor.execute('SELECT COUNT(*) FROM usuarios')
            if cursor.fetchone()[0] == 0:
                # Inserir usuário admin
                senha_hash = hashlib.sha256('admin123'.encode()).hexdigest()
                cursor.execute('''
                    INSERT INTO usuarios (username, senha, nome, is_admin)
                    VALUES (?, ?, ?, ?)
                ''', ('admin', senha_hash, 'Administrador', 1))
                
                # Inserir algumas empresas de exemplo
                empresas = [
                    ('001', 'Grafeno', 'tenant1', 'producao'),
                    ('002', 'Sifra', 'tenant2', 'producao'),
                    ('003', 'Apas', 'tenant3', 'producao')
                ]
                cursor.executemany('''
                    INSERT INTO empresas (codigo, nome, tenetID, ambiente)
                    VALUES (?, ?, ?, ?)
                ''', empresas)
                
                # Dar acesso total ao admin
                for empresa in empresas:
                    cursor.execute('''
                        INSERT INTO permissoes (usuario, empresa_codigo)
                        VALUES (?, ?)
                    ''', ('admin', empresa[0]))
            
            conn.commit()
    
    def verify_database(self):
        """Verifica se o banco de dados foi inicializado corretamente."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print("Tabelas existentes:", tables)
            
            # Verificar usuários
            cursor.execute("SELECT * FROM usuarios")
            users = cursor.fetchall()
            print("Usuários:", users)
            
            # Verificar empresas
            cursor.execute("SELECT * FROM empresas")
            empresas = cursor.fetchall()
            print("Empresas:", empresas)
            
            # Verificar permissões
            cursor.execute("SELECT * FROM permissoes")
            permissoes = cursor.fetchall()
            print("Permissões:", permissoes)
    
    def verificar_login(self, username: str, senha: str) -> bool:
        """Verifica se as credenciais do usuário são válidas."""
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username FROM usuarios
                WHERE username = ? AND senha = ?
            ''', (username, senha_hash))
            return cursor.fetchone() is not None
    
    def get_usuario(self, username: str) -> Optional[Dict]:
        """Retorna os dados do usuário."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, nome, is_admin
                FROM usuarios
                WHERE username = ?
            ''', (username,))
            row = cursor.fetchone()
            if row:
                return {
                    "username": row[0],
                    "nome": row[1],
                    "is_admin": bool(row[2])
                }
            return None
    
    def get_empresas_permitidas(self, username: str) -> List[Dict]:
        """Retorna as empresas que o usuário tem permissão para acessar."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT e.codigo, e.nome
                FROM empresas e
                INNER JOIN permissoes p ON e.codigo = p.empresa_codigo
                INNER JOIN usuarios u ON p.usuario = u.username
                WHERE u.username = ?
            ''', (username,))
            return [{"codigo": row[0], "nome": row[1]} for row in cursor.fetchall()]
    
    def get_todas_empresas(self) -> List[Dict]:
        """Retorna todas as empresas cadastradas."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT codigo, nome, tenetID, ambiente FROM empresas')
            return [{"codigo": row[0], "nome": row[1], "tenetID": row[2], "ambiente": row[3]} for row in cursor.fetchall()]
    
    def adicionar_usuario(self, username: str, senha: str, nome: str, is_admin: bool, empresas: List[str]) -> bool:
        """Adiciona um novo usuário com suas permissões.
        
        Args:
            username: Nome de usuário
            senha: Senha do usuário
            nome: Nome completo do usuário
            is_admin: Se o usuário é administrador
            empresas: Lista de códigos das empresas que o usuário terá acesso
        """
        try:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO usuarios (username, senha, nome, is_admin)
                    VALUES (?, ?, ?, ?)
                ''', (username, senha_hash, nome, int(is_admin)))
                
                # Adicionar permissões
                cursor.executemany('''
                    INSERT INTO permissoes (usuario, empresa_codigo)
                    VALUES (?, ?)
                ''', [(username, empresa) for empresa in empresas])
                
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def atualizar_usuario(self, username: str, senha: str, nome: str, is_admin: bool, empresas: List[str]) -> bool:
        """Atualiza os dados de um usuário existente.
        
        Args:
            username: Nome de usuário
            senha: Nova senha do usuário
            nome: Nome completo do usuário
            is_admin: Se o usuário é administrador
            empresas: Lista de códigos das empresas que o usuário terá acesso
        """
        try:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE usuarios
                    SET senha = ?, nome = ?, is_admin = ?
                    WHERE username = ?
                ''', (senha_hash, nome, int(is_admin), username))
                
                # Atualizar permissões
                cursor.execute('''
                    DELETE FROM permissoes
                    WHERE usuario = ?
                ''', (username,))
                
                cursor.executemany('''
                    INSERT INTO permissoes (usuario, empresa_codigo)
                    VALUES (?, ?)
                ''', [(username, empresa) for empresa in empresas])
                
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def alterar_senha(self, username: str, nova_senha: str) -> bool:
        """Altera a senha de um usuário."""
        try:
            senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE usuarios
                    SET senha = ?
                    WHERE username = ?
                ''', (senha_hash, username))
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def get_todos_usuarios(self) -> List[Dict]:
        """Retorna todos os usuários cadastrados."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, nome, is_admin
                FROM usuarios
                ORDER BY username
            ''')
            return [
                {
                    "username": row[0],
                    "nome": row[1],
                    "is_admin": bool(row[2])
                }
                for row in cursor.fetchall()
            ]
    
    def get_empresas_usuario(self, username: str) -> List[Dict]:
        """Retorna todas as empresas que um usuário tem acesso."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT e.codigo, e.nome
                FROM empresas e
                JOIN permissoes p ON e.codigo = p.empresa_codigo
                WHERE p.usuario = ?
                ORDER BY e.codigo
            ''', (username,))
            return [
                {
                    "codigo": row[0],
                    "nome": row[1]
                }
                for row in cursor.fetchall()
            ]
    
    def excluir_usuario(self, username: str) -> bool:
        """Exclui um usuário e suas permissões."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Excluir permissões primeiro
                cursor.execute('''
                    DELETE FROM permissoes
                    WHERE usuario = ?
                ''', (username,))
                
                # Excluir usuário
                cursor.execute('''
                    DELETE FROM usuarios
                    WHERE username = ?
                ''', (username,))
                
                conn.commit()
                return True
            except sqlite3.Error:
                return False
    
    def adicionar_empresa(self, codigo: str, nome: str, tenetID: str, ambiente: str) -> bool:
        """Adiciona uma nova empresa ao sistema.
        
        Args:
            codigo: Código único da empresa
            nome: Nome da empresa
            tenetID: ID do tenant no sistema
            ambiente: Ambiente (producao ou homologacao)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO empresas (codigo, nome, tenetID, ambiente)
                    VALUES (?, ?, ?, ?)
                ''', (codigo, nome, tenetID, ambiente))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_empresa(self, codigo: str) -> Optional[Dict]:
        """Retorna os dados de uma empresa específica.
        
        Args:
            codigo: Código da empresa
            
        Returns:
            Optional[Dict]: Dados da empresa ou None se não encontrada
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT codigo, nome, tenetID, ambiente
                FROM empresas
                WHERE codigo = ?
            ''', (codigo,))
            row = cursor.fetchone()
            if row:
                return {
                    "codigo": row[0],
                    "nome": row[1],
                    "tenetID": row[2],
                    "ambiente": row[3]
                }
            return None
    
    def atualizar_empresa(self, codigo: str, nome: str, tenetID: str, ambiente: str) -> bool:
        """Atualiza os dados de uma empresa existente.
        
        Args:
            codigo: Código da empresa a ser atualizada
            nome: Novo nome da empresa
            tenetID: Novo ID do tenant
            ambiente: Novo ambiente
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE empresas
                    SET nome = ?, tenetID = ?, ambiente = ?
                    WHERE codigo = ?
                ''', (nome, tenetID, ambiente, codigo))
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def excluir_empresa(self, codigo: str) -> bool:
        """Exclui uma empresa do sistema.
        
        Args:
            codigo: Código da empresa a ser excluída
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Excluir permissões primeiro
                cursor.execute('''
                    DELETE FROM permissoes
                    WHERE empresa_codigo = ?
                ''', (codigo,))
                
                # Excluir empresa
                cursor.execute('''
                    DELETE FROM empresas
                    WHERE codigo = ?
                ''', (codigo,))
                
                conn.commit()
                return True
            except sqlite3.Error:
                return False
    
    def adicionar_operador(self, email: str, senha: str, ativo: bool) -> bool:
        """Adiciona um novo operador."""
        try:
            cursor = self.get_connection().cursor()
            cursor.execute(
                'INSERT INTO operadores (email, senha, ativo) VALUES (?, ?, ?)',
                (email, senha, ativo)
            )
            self.get_connection().commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def atualizar_operador(self, email: str, senha: str, ativo: bool) -> bool:
        """Atualiza os dados de um operador existente."""
        try:
            cursor = self.get_connection().cursor()
            cursor.execute(
                'UPDATE operadores SET senha = ?, ativo = ? WHERE email = ?',
                (senha, ativo, email)
            )
            self.get_connection().commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def excluir_operador(self, email: str) -> bool:
        """Exclui um operador."""
        try:
            cursor = self.get_connection().cursor()
            cursor.execute('DELETE FROM operadores WHERE email = ?', (email,))
            self.get_connection().commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def get_operador(self, email: str) -> dict:
        """Retorna os dados de um operador específico."""
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT * FROM operadores WHERE email = ?', (email,))
        row = cursor.fetchone()
        if row:
            return {
                'email': row[0],
                'senha': row[1],
                'ativo': bool(row[2])
            }
        return None
    
    def get_todos_operadores(self) -> list:
        """Retorna todos os operadores cadastrados."""
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT * FROM operadores')
        return [
            {
                'email': row[0],
                'senha': row[1],
                'ativo': bool(row[2])
            }
            for row in cursor.fetchall()
        ] 