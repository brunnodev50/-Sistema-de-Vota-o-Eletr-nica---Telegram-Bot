import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Bot
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'SEU_TOKEN_AQUI')

# Senha de administrador (recomendado usar variável de ambiente)
SENHA_ADMIN = os.getenv('SENHA_ADMIN', '1234')

# Configurações do banco de dados
DATABASE_NAME = 'votacao.db'

# Configurações de fotos
PASTA_FOTOS = 'foto_presidentes'

# Configurações de API
API_TIMEOUT = 5  # Timeout para validação de CPF via API
