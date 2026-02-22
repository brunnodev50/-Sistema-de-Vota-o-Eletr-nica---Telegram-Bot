import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_name='votacao.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.criar_tabelas()
    
    @contextmanager
    def get_cursor(self):
        """Context manager para criar cursores temporários"""
        cursor = self.conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    
    def criar_tabelas(self):
        """Cria todas as tabelas necessárias"""
        with self.get_cursor() as cursor:
            # Tabela de partidos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS partidos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL,
                    sigla TEXT UNIQUE NOT NULL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de candidatos com ano e partido
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS candidatos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    numero INTEGER NOT NULL,
                    foto_path TEXT,
                    partido_id INTEGER,
                    ano INTEGER NOT NULL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (partido_id) REFERENCES partidos(id),
                    UNIQUE(numero, ano)
                )
            ''')
            
            # Tabela de votos com ano
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS votos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpf TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    candidato_id INTEGER NOT NULL,
                    ano INTEGER NOT NULL,
                    data_voto TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (candidato_id) REFERENCES candidatos(id),
                    UNIQUE(cpf, ano)
                )
            ''')
            
            # Tabela de configurações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracoes (
                    chave TEXT PRIMARY KEY,
                    valor TEXT
                )
            ''')
            
            self.conn.commit()
        
        # Inicializa configurações padrão
        with self.get_cursor() as cursor:
            cursor.execute('SELECT valor FROM configuracoes WHERE chave = "votacao_ativa"')
            if cursor.fetchone() is None:
                cursor.execute('INSERT INTO configuracoes (chave, valor) VALUES ("votacao_ativa", "1")')
            
            cursor.execute('SELECT valor FROM configuracoes WHERE chave = "ano_atual"')
            if cursor.fetchone() is None:
                ano_atual = datetime.now().year
                cursor.execute('INSERT INTO configuracoes (chave, valor) VALUES ("ano_atual", ?)', (str(ano_atual),))
            
            self.conn.commit()
    
    def get_config(self, chave):
        """Obtém uma configuração"""
        with self.get_cursor() as cursor:
            cursor.execute('SELECT valor FROM configuracoes WHERE chave = ?', (chave,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def set_config(self, chave, valor):
        """Define uma configuração"""
        with self.get_cursor() as cursor:
            cursor.execute('INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)', (chave, valor))
            self.conn.commit()
    
    def votacao_ativa(self):
        """Verifica se a votação está ativa"""
        return self.get_config('votacao_ativa') == '1'
    
    def get_ano_atual(self):
        """Retorna o ano atual da votação"""
        ano = self.get_config('ano_atual')
        return int(ano) if ano else datetime.now().year
    
    def set_ano_atual(self, ano):
        """Define o ano atual da votação"""
        self.set_config('ano_atual', str(ano))
    
    # PARTIDOS
    def adicionar_partido(self, nome, sigla):
        """Adiciona um novo partido"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute('INSERT INTO partidos (nome, sigla) VALUES (?, ?)', (nome, sigla))
                self.conn.commit()
            return True, f"Partido '{nome}' ({sigla}) adicionado com sucesso!"
        except sqlite3.IntegrityError:
            return False, f"Partido '{nome}' ou sigla '{sigla}' já existe."
    
    def listar_partidos(self):
        """Lista todos os partidos"""
        with self.get_cursor() as cursor:
            cursor.execute('SELECT id, nome, sigla FROM partidos ORDER BY nome')
            return cursor.fetchall()
    
    def get_partido_por_id(self, partido_id):
        """Obtém um partido pelo ID"""
        with self.get_cursor() as cursor:
            cursor.execute('SELECT id, nome, sigla FROM partidos WHERE id = ?', (partido_id,))
            return cursor.fetchone()
    
    def deletar_partido(self, partido_id):
        """Deleta um partido"""
        with self.get_cursor() as cursor:
            cursor.execute('SELECT nome FROM partidos WHERE id = ?', (partido_id,))
            partido = cursor.fetchone()
            if partido is None:
                return False, "Partido não encontrado."
            
            cursor.execute('DELETE FROM partidos WHERE id = ?', (partido_id,))
            self.conn.commit()
            return True, f"Partido '{partido[0]}' deletado com sucesso."
    
    # CANDIDATOS
    def adicionar_candidato(self, nome, numero, foto_path, partido_id, ano):
        """Adiciona um novo candidato"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    'INSERT INTO candidatos (nome, numero, foto_path, partido_id, ano) VALUES (?, ?, ?, ?, ?)',
                    (nome, numero, foto_path, partido_id, ano)
                )
                self.conn.commit()
            return True, f"Candidato '{nome}' (número {numero}) adicionado com sucesso!"
        except sqlite3.IntegrityError:
            return False, f"Já existe um candidato com o número {numero} para o ano {ano}."
    
    def listar_candidatos(self, ano=None):
        """Lista todos os candidatos de um ano específico ou do ano atual"""
        if ano is None:
            ano = self.get_ano_atual()
        
        with self.get_cursor() as cursor:
            cursor.execute('''
                SELECT c.id, c.nome, c.numero, c.foto_path, p.nome, p.sigla, c.ano
                FROM candidatos c
                LEFT JOIN partidos p ON c.partido_id = p.id
                WHERE c.ano = ?
                ORDER BY c.numero
            ''', (ano,))
            return cursor.fetchall()
    
    def get_candidato_por_id(self, candidato_id):
        """Obtém um candidato pelo ID"""
        with self.get_cursor() as cursor:
            cursor.execute('''
                SELECT c.id, c.nome, c.numero, c.foto_path, c.partido_id, p.nome, p.sigla, c.ano
                FROM candidatos c
                LEFT JOIN partidos p ON c.partido_id = p.id
                WHERE c.id = ?
            ''', (candidato_id,))
            return cursor.fetchone()
    
    def atualizar_candidato(self, candidato_id, nome=None, numero=None, foto_path=None, partido_id=None):
        """Atualiza os dados de um candidato"""
        candidato = self.get_candidato_por_id(candidato_id)
        if candidato is None:
            return False, "Candidato não encontrado."
        
        updates = []
        params = []
        
        if nome is not None:
            updates.append("nome = ?")
            params.append(nome)
        if numero is not None:
            updates.append("numero = ?")
            params.append(numero)
        if foto_path is not None:
            updates.append("foto_path = ?")
            params.append(foto_path)
        if partido_id is not None:
            updates.append("partido_id = ?")
            params.append(partido_id)
        
        if not updates:
            return False, "Nenhum dado para atualizar."
        
        params.append(candidato_id)
        query = f"UPDATE candidatos SET {', '.join(updates)} WHERE id = ?"
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                self.conn.commit()
            return True, "Candidato atualizado com sucesso!"
        except sqlite3.IntegrityError:
            return False, "Erro ao atualizar: número já existe para este ano."
    
    def deletar_candidato(self, candidato_id):
        """Deleta um candidato"""
        with self.get_cursor() as cursor:
            cursor.execute('SELECT nome FROM candidatos WHERE id = ?', (candidato_id,))
            candidato = cursor.fetchone()
            if candidato is None:
                return False, "Candidato não encontrado."
            
            cursor.execute('DELETE FROM candidatos WHERE id = ?', (candidato_id,))
            self.conn.commit()
            return True, f"Candidato '{candidato[0]}' deletado com sucesso."
    
    # VOTOS
    def registrar_voto(self, cpf, nome, candidato_id, ano):
        """Registra um voto"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    'INSERT INTO votos (cpf, nome, candidato_id, ano) VALUES (?, ?, ?, ?)',
                    (cpf, nome, candidato_id, ano)
                )
                self.conn.commit()
            return True, "Voto registrado com sucesso!"
        except sqlite3.IntegrityError:
            return False, "Você já votou nesta eleição."
    
    def verificar_voto(self, cpf, ano=None):
        """Verifica se o CPF já votou no ano especificado"""
        if ano is None:
            ano = self.get_ano_atual()
        
        with self.get_cursor() as cursor:
            cursor.execute('SELECT candidato_id FROM votos WHERE cpf = ? AND ano = ?', (cpf, ano))
            return cursor.fetchone() is not None
    
    def get_resultados(self, ano=None):
        """Obtém os resultados da votação"""
        if ano is None:
            ano = self.get_ano_atual()
        
        with self.get_cursor() as cursor:
            cursor.execute('''
                SELECT c.nome, c.numero, p.sigla, COUNT(v.id) as votos
                FROM candidatos c
                LEFT JOIN votos v ON c.id = v.candidato_id AND v.ano = ?
                LEFT JOIN partidos p ON c.partido_id = p.id
                WHERE c.ano = ?
                GROUP BY c.id
                ORDER BY votos DESC, c.numero
            ''', (ano, ano))
            return cursor.fetchall()
    
    def get_total_votos(self, ano=None):
        """Obtém o total de votos"""
        if ano is None:
            ano = self.get_ano_atual()
        
        with self.get_cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM votos WHERE ano = ?', (ano,))
            return cursor.fetchone()[0]
    
    def listar_anos_eleicoes(self):
        """Lista todos os anos que tiveram eleições"""
        with self.get_cursor() as cursor:
            cursor.execute('SELECT DISTINCT ano FROM votos ORDER BY ano DESC')
            return [row[0] for row in cursor.fetchall()]
    
    def zerar_votos(self, ano=None):
        """Zera os votos de um ano específico"""
        if ano is None:
            ano = self.get_ano_atual()
        
        with self.get_cursor() as cursor:
            cursor.execute('DELETE FROM votos WHERE ano = ?', (ano,))
            self.conn.commit()
        return True, f"Todos os votos do ano {ano} foram apagados."
    
    def reset_total(self):
        """Apaga TODOS os dados do banco"""
        with self.get_cursor() as cursor:
            cursor.execute('DELETE FROM votos')
            cursor.execute('DELETE FROM candidatos')
            cursor.execute('DELETE FROM partidos')
            self.conn.commit()
        return True, "Banco de dados completamente resetado!"
    
    def fechar(self):
        """Fecha a conexão com o banco"""
        self.conn.close()