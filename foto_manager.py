import os
from datetime import datetime

class FotoManager:
    def __init__(self, pasta_fotos='foto_presidentes'):
        self.pasta_fotos = pasta_fotos
        self.criar_pasta_se_necessario()
    
    def criar_pasta_se_necessario(self):
        """Cria a pasta de fotos se ela não existir"""
        if not os.path.exists(self.pasta_fotos):
            os.makedirs(self.pasta_fotos)
            print(f"Pasta '{self.pasta_fotos}' criada com sucesso!")
    
    def gerar_nome_arquivo(self, numero_candidato, ano):
        """Gera um nome único para o arquivo da foto"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"candidato_{numero_candidato}_{ano}_{timestamp}.jpg"
    
    def salvar_foto(self, file_info, numero_candidato, ano):
        """Salva a foto do candidato"""
        try:
            nome_arquivo = self.gerar_nome_arquivo(numero_candidato, ano)
            caminho_completo = os.path.join(self.pasta_fotos, nome_arquivo)
            
            # Retorna o caminho relativo para salvar no banco
            return caminho_completo, True
        except Exception as e:
            return None, False
    
    def deletar_foto(self, caminho_foto):
        """Deleta a foto de um candidato"""
        try:
            if caminho_foto and os.path.exists(caminho_foto):
                os.remove(caminho_foto)
                return True
            return False
        except Exception as e:
            print(f"Erro ao deletar foto: {e}")
            return False
    
    def foto_existe(self, caminho_foto):
        """Verifica se a foto existe"""
        return caminho_foto and os.path.exists(caminho_foto)
