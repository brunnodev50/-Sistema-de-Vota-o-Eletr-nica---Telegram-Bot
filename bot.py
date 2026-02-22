import telebot
from telebot import types
from datetime import datetime
import os

# Importa os módulos customizados
from database import DatabaseManager
from validacao import validar_cpf
from foto_manager import FotoManager
from config import TOKEN, SENHA_ADMIN, PASTA_FOTOS

# Inicializa o bot
bot = telebot.TeleBot(TOKEN)

# Inicializa os gerenciadores
db = DatabaseManager()
foto_manager = FotoManager(PASTA_FOTOS)

# Dicionário para armazenar estados temporários dos usuários
user_states = {}

# ==================== FUNÇÕES AUXILIARES ====================

def verificar_senha(message, callback_sucesso, *args):
    """Verifica se a senha está correta"""
    bot.send_message(message.chat.id, "🔒 Digite a senha de administrador:")
    bot.register_next_step_handler(message, processar_senha, callback_sucesso, args)

def processar_senha(message, callback_sucesso, args):
    """Processa a senha digitada"""
    if message.text == SENHA_ADMIN:
        callback_sucesso(message, *args)
    else:
        bot.send_message(message.chat.id, "❌ Senha incorreta!")

def criar_menu_principal():
    """Cria o menu principal"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📊 Ver Resultados"),
        types.KeyboardButton("🗳️ Votar"),
        types.KeyboardButton("ℹ️ Ajuda")
    )
    return markup

# ==================== COMANDO /START ====================

@bot.message_handler(commands=['start'])
def start(message):
    """Inicia o bot"""
    ano_atual = db.get_ano_atual()
    votacao_ativa = db.votacao_ativa()
    
    mensagem = f"🗳️ *Bem-vindo ao Sistema de Votação Eletrônica!*\n\n"
    mensagem += f"📅 Ano da eleição: *{ano_atual}*\n"
    mensagem += f"Status: {'✅ Votação ABERTA' if votacao_ativa else '🔒 Votação ENCERRADA'}\n\n"
    
    if votacao_ativa:
        mensagem += "Para votar, digite seu nome completo ou use o botão abaixo."
        markup = criar_menu_principal()
    else:
        mensagem += "A votação está encerrada. Você pode ver os resultados."
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(types.KeyboardButton("📊 Ver Resultados"))
    
    bot.send_message(message.chat.id, mensagem, parse_mode='Markdown', reply_markup=markup)
    
    if votacao_ativa:
        bot.register_next_step_handler(message, processar_resposta_menu)

def processar_resposta_menu(message):
    """Processa a resposta do menu principal"""
    texto = message.text
    
    if texto == "🗳️ Votar":
        iniciar_votacao(message)
    elif texto == "📊 Ver Resultados":
        mostrar_resultados(message)
    elif texto == "ℹ️ Ajuda":
        mostrar_ajuda(message)
    else:
        # Se não for um botão, assume que é o nome para votação
        solicitar_nome(message)

# ==================== PROCESSO DE VOTAÇÃO ====================

def iniciar_votacao(message):
    """Inicia o processo de votação"""
    if not db.votacao_ativa():
        bot.send_message(message.chat.id, "❌ A votação está encerrada!")
        return
    
    bot.send_message(message.chat.id, "📝 Digite seu nome completo:")
    bot.register_next_step_handler(message, solicitar_nome)

def solicitar_nome(message):
    """Solicita o nome do eleitor"""
    nome = message.text.strip()
    
    if len(nome) < 3:
        bot.send_message(message.chat.id, "❌ Nome inválido. Digite seu nome completo:")
        bot.register_next_step_handler(message, solicitar_nome)
        return
    
    bot.send_message(message.chat.id, "🆔 Digite seu CPF (somente números):")
    bot.register_next_step_handler(message, solicitar_cpf, nome)

def solicitar_cpf(message, nome):
    """Solicita e valida o CPF"""
    cpf = message.text.strip()
    
    # Valida o CPF
    valido, mensagem_validacao = validar_cpf(cpf)
    
    if not valido:
        bot.send_message(
            message.chat.id, 
            f"❌ {mensagem_validacao}\n\nDigite novamente seu CPF:"
        )
        bot.register_next_step_handler(message, solicitar_cpf, nome)
        return
    
    # Remove caracteres não numéricos
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    
    # Verifica se já votou
    ano_atual = db.get_ano_atual()
    if db.verificar_voto(cpf_limpo, ano_atual):
        bot.send_message(
            message.chat.id, 
            "❌ Este CPF já votou nesta eleição!\n\nVocê não pode votar mais de uma vez."
        )
        return
    
    # Lista os candidatos
    candidatos = db.listar_candidatos(ano_atual)
    
    if not candidatos:
        bot.send_message(message.chat.id, "❌ Nenhum candidato disponível para votação.")
        return
    
    # Cria os botões com os candidatos
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    
    for candidato in candidatos:
        candidato_id, nome_cand, numero, foto_path, partido_nome, partido_sigla, ano = candidato
        texto_botao = f"{numero} - {nome_cand}"
        if partido_sigla:
            texto_botao += f" ({partido_sigla})"
        markup.add(texto_botao)
    
    bot.send_message(
        message.chat.id, 
        "🗳️ *Escolha seu candidato:*\n\nClique em um dos botões abaixo:", 
        parse_mode='Markdown',
        reply_markup=markup
    )
    
    bot.register_next_step_handler(message, processar_voto, cpf_limpo, nome, candidatos)

def processar_voto(message, cpf, nome_eleitor, candidatos):
    """Processa a escolha do candidato"""
    escolha = message.text
    
    # Extrai o número do candidato da escolha
    try:
        numero_candidato = int(escolha.split(' - ')[0])
    except:
        bot.send_message(message.chat.id, "❌ Opção inválida. Tente novamente.")
        return
    
    # Busca o candidato escolhido
    candidato_escolhido = None
    for candidato in candidatos:
        if candidato[2] == numero_candidato:  # candidato[2] é o número
            candidato_escolhido = candidato
            break
    
    if not candidato_escolhido:
        bot.send_message(message.chat.id, "❌ Candidato não encontrado.")
        return
    
    candidato_id, nome_cand, numero, foto_path, partido_nome, partido_sigla, ano = candidato_escolhido
    
    # Mostra a foto do candidato se existir
    if foto_path and os.path.exists(foto_path):
        with open(foto_path, 'rb') as foto:
            bot.send_photo(message.chat.id, foto)
    
    # Cria mensagem de confirmação
    texto_confirmacao = f"✅ *Confirme seu voto:*\n\n"
    texto_confirmacao += f"📋 Candidato: *{nome_cand}*\n"
    texto_confirmacao += f"🔢 Número: *{numero}*\n"
    if partido_sigla:
        texto_confirmacao += f"🏛️ Partido: *{partido_nome} ({partido_sigla})*\n"
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("✅ Confirmar", "❌ Cancelar")
    
    bot.send_message(message.chat.id, texto_confirmacao, parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler(message, confirmar_voto, cpf, nome_eleitor, candidato_id)

def confirmar_voto(message, cpf, nome_eleitor, candidato_id):
    """Confirma e registra o voto"""
    if message.text == "✅ Confirmar":
        ano_atual = db.get_ano_atual()
        sucesso, mensagem = db.registrar_voto(cpf, nome_eleitor, candidato_id, ano_atual)
        
        if sucesso:
            bot.send_message(
                message.chat.id, 
                "✅ *Voto registrado com sucesso!*\n\nObrigado por participar!",
                parse_mode='Markdown',
                reply_markup=types.ReplyKeyboardRemove()
            )
        else:
            bot.send_message(message.chat.id, f"❌ {mensagem}")
    else:
        bot.send_message(
            message.chat.id, 
            "❌ Votação cancelada.",
            reply_markup=types.ReplyKeyboardRemove()
        )

# ==================== GERENCIAMENTO DE PARTIDOS ====================

@bot.message_handler(commands=['cadastrar_partidos'])
def cadastrar_partido_inicio(message):
    """Inicia o cadastro de partido"""
    verificar_senha(message, cadastrar_partido_pedir_nome)

def cadastrar_partido_pedir_nome(message):
    """Pede o nome do partido"""
    bot.send_message(message.chat.id, "🏛️ Digite o nome completo do partido:")
    bot.register_next_step_handler(message, cadastrar_partido_pedir_sigla)

def cadastrar_partido_pedir_sigla(message):
    """Pede a sigla do partido"""
    nome_partido = message.text
    bot.send_message(message.chat.id, "🔤 Digite a sigla do partido (ex: PT, PSDB):")
    bot.register_next_step_handler(message, cadastrar_partido_finalizar, nome_partido)

def cadastrar_partido_finalizar(message, nome_partido):
    """Finaliza o cadastro do partido"""
    sigla = message.text.upper()
    sucesso, mensagem = db.adicionar_partido(nome_partido, sigla)
    bot.send_message(message.chat.id, f"{'✅' if sucesso else '❌'} {mensagem}")

@bot.message_handler(commands=['lista_partidos'])
def listar_partidos(message):
    """Lista todos os partidos cadastrados"""
    partidos = db.listar_partidos()
    
    if not partidos:
        bot.send_message(message.chat.id, "❌ Nenhum partido cadastrado.")
        return
    
    mensagem = "🏛️ *Partidos Cadastrados:*\n\n"
    for partido_id, nome, sigla in partidos:
        mensagem += f"ID: {partido_id} | *{sigla}* - {nome}\n"
    
    bot.send_message(message.chat.id, mensagem, parse_mode='Markdown')

# ==================== GERENCIAMENTO DE CANDIDATOS ====================

@bot.message_handler(commands=['inserir_presidente'])
def inserir_presidente_inicio(message):
    """Inicia o cadastro de candidato"""
    verificar_senha(message, inserir_presidente_escolher_ano)

def inserir_presidente_escolher_ano(message):
    """Escolhe o ano da candidatura"""
    bot.send_message(message.chat.id, "📅 Digite o ano da candidatura:")
    bot.register_next_step_handler(message, inserir_presidente_pedir_nome)

def inserir_presidente_pedir_nome(message):
    """Pede o nome do candidato"""
    try:
        ano = int(message.text)
        user_states[message.chat.id] = {'ano': ano}
        bot.send_message(message.chat.id, "👤 Digite o nome do candidato:")
        bot.register_next_step_handler(message, inserir_presidente_pedir_numero)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Ano inválido. Digite novamente:")
        bot.register_next_step_handler(message, inserir_presidente_pedir_nome)

def inserir_presidente_pedir_numero(message):
    """Pede o número do candidato"""
    user_states[message.chat.id]['nome'] = message.text
    bot.send_message(message.chat.id, "🔢 Digite o número do candidato:")
    bot.register_next_step_handler(message, inserir_presidente_pedir_partido)

def inserir_presidente_pedir_partido(message):
    """Pede o partido do candidato"""
    try:
        numero = int(message.text)
        user_states[message.chat.id]['numero'] = numero
        
        # Lista os partidos disponíveis
        partidos = db.listar_partidos()
        
        if not partidos:
            bot.send_message(
                message.chat.id, 
                "❌ Nenhum partido cadastrado. Use /cadastrar_partidos primeiro."
            )
            return
        
        mensagem = "🏛️ *Escolha o partido:*\n\n"
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        
        for partido_id, nome, sigla in partidos:
            mensagem += f"{partido_id}. {sigla} - {nome}\n"
            markup.add(f"{partido_id} - {sigla}")
        
        markup.add("Sem partido")
        
        bot.send_message(message.chat.id, mensagem, parse_mode='Markdown', reply_markup=markup)
        bot.register_next_step_handler(message, inserir_presidente_pedir_foto)
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Número inválido. Digite novamente:")
        bot.register_next_step_handler(message, inserir_presidente_pedir_partido)

def inserir_presidente_pedir_foto(message):
    """Pede a foto do candidato"""
    escolha = message.text
    
    if escolha == "Sem partido":
        partido_id = None
    else:
        try:
            partido_id = int(escolha.split(' - ')[0])
        except:
            bot.send_message(message.chat.id, "❌ Partido inválido.")
            return
    
    user_states[message.chat.id]['partido_id'] = partido_id
    
    bot.send_message(
        message.chat.id, 
        "📸 Envie a foto do candidato (ou digite 'PULAR' para cadastrar sem foto):",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(message, inserir_presidente_finalizar)

def inserir_presidente_finalizar(message):
    """Finaliza o cadastro do candidato"""
    state = user_states.get(message.chat.id, {})
    
    if not state:
        bot.send_message(message.chat.id, "❌ Erro: sessão expirada.")
        return
    
    foto_path = None
    
    # Verifica se foi enviada uma foto
    if message.content_type == 'photo':
        # Baixa a foto
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Salva a foto
        nome_arquivo = foto_manager.gerar_nome_arquivo(state['numero'], state['ano'])
        foto_path = os.path.join(PASTA_FOTOS, nome_arquivo)
        
        with open(foto_path, 'wb') as new_file:
            new_file.write(downloaded_file)
    
    # Cadastra o candidato
    sucesso, mensagem = db.adicionar_candidato(
        state['nome'],
        state['numero'],
        foto_path,
        state['partido_id'],
        state['ano']
    )
    
    bot.send_message(message.chat.id, f"{'✅' if sucesso else '❌'} {mensagem}")
    
    # Limpa o estado
    if message.chat.id in user_states:
        del user_states[message.chat.id]

@bot.message_handler(commands=['editar_presidente'])
def editar_presidente_inicio(message):
    """Inicia a edição de candidato"""
    verificar_senha(message, editar_presidente_listar)

def editar_presidente_listar(message):
    """Lista os candidatos para edição"""
    ano_atual = db.get_ano_atual()
    candidatos = db.listar_candidatos(ano_atual)
    
    if not candidatos:
        bot.send_message(message.chat.id, "❌ Nenhum candidato cadastrado para este ano.")
        return
    
    mensagem = f"📋 *Candidatos de {ano_atual}:*\n\n"
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    
    for candidato in candidatos:
        candidato_id, nome, numero, foto_path, partido_nome, partido_sigla, ano = candidato
        mensagem += f"ID: {candidato_id} | {numero} - {nome}"
        if partido_sigla:
            mensagem += f" ({partido_sigla})"
        mensagem += "\n"
        markup.add(f"{candidato_id}")
    
    bot.send_message(message.chat.id, mensagem, parse_mode='Markdown', reply_markup=markup)
    bot.send_message(message.chat.id, "🔢 Digite o ID do candidato que deseja editar:")
    bot.register_next_step_handler(message, editar_presidente_escolher_campo)

def editar_presidente_escolher_campo(message):
    """Escolhe o campo a ser editado"""
    try:
        candidato_id = int(message.text)
        candidato = db.get_candidato_por_id(candidato_id)
        
        if not candidato:
            bot.send_message(message.chat.id, "❌ Candidato não encontrado.")
            return
        
        user_states[message.chat.id] = {'candidato_id': candidato_id}
        
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Nome", "Número", "Partido", "Foto")
        
        bot.send_message(
            message.chat.id, 
            "✏️ O que deseja editar?",
            reply_markup=markup
        )
        bot.register_next_step_handler(message, editar_presidente_processar)
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ ID inválido.")

def editar_presidente_processar(message):
    """Processa a edição do candidato"""
    campo = message.text
    state = user_states.get(message.chat.id, {})
    
    if not state:
        bot.send_message(message.chat.id, "❌ Erro: sessão expirada.")
        return
    
    state['campo'] = campo
    
    if campo == "Nome":
        bot.send_message(message.chat.id, "👤 Digite o novo nome:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, editar_presidente_finalizar)
    elif campo == "Número":
        bot.send_message(message.chat.id, "🔢 Digite o novo número:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, editar_presidente_finalizar)
    elif campo == "Partido":
        partidos = db.listar_partidos()
        mensagem = "🏛️ *Escolha o novo partido:*\n\n"
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        
        for partido_id, nome, sigla in partidos:
            mensagem += f"{partido_id}. {sigla} - {nome}\n"
            markup.add(f"{partido_id} - {sigla}")
        
        markup.add("Sem partido")
        
        bot.send_message(message.chat.id, mensagem, parse_mode='Markdown', reply_markup=markup)
        bot.register_next_step_handler(message, editar_presidente_finalizar)
    elif campo == "Foto":
        bot.send_message(message.chat.id, "📸 Envie a nova foto:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, editar_presidente_finalizar)

def editar_presidente_finalizar(message):
    """Finaliza a edição do candidato"""
    state = user_states.get(message.chat.id, {})
    
    if not state:
        bot.send_message(message.chat.id, "❌ Erro: sessão expirada.")
        return
    
    candidato_id = state['candidato_id']
    campo = state['campo']
    
    if campo == "Nome":
        sucesso, mensagem = db.atualizar_candidato(candidato_id, nome=message.text)
    elif campo == "Número":
        try:
            numero = int(message.text)
            sucesso, mensagem = db.atualizar_candidato(candidato_id, numero=numero)
        except ValueError:
            bot.send_message(message.chat.id, "❌ Número inválido.")
            return
    elif campo == "Partido":
        escolha = message.text
        if escolha == "Sem partido":
            partido_id = None
        else:
            try:
                partido_id = int(escolha.split(' - ')[0])
            except:
                bot.send_message(message.chat.id, "❌ Partido inválido.")
                return
        sucesso, mensagem = db.atualizar_candidato(candidato_id, partido_id=partido_id)
    elif campo == "Foto":
        if message.content_type == 'photo':
            # Deleta foto antiga se existir
            candidato = db.get_candidato_por_id(candidato_id)
            if candidato and candidato[3]:
                foto_manager.deletar_foto(candidato[3])
            
            # Baixa nova foto
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            nome_arquivo = foto_manager.gerar_nome_arquivo(candidato[2], candidato[7])
            foto_path = os.path.join(PASTA_FOTOS, nome_arquivo)
            
            with open(foto_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            
            sucesso, mensagem = db.atualizar_candidato(candidato_id, foto_path=foto_path)
        else:
            bot.send_message(message.chat.id, "❌ Por favor, envie uma foto.")
            return
    
    bot.send_message(message.chat.id, f"{'✅' if sucesso else '❌'} {mensagem}")
    
    if message.chat.id in user_states:
        del user_states[message.chat.id]

@bot.message_handler(commands=['deletar_presidente'])
def deletar_presidente_inicio(message):
    """Inicia a exclusão de candidato"""
    verificar_senha(message, deletar_presidente_listar)

def deletar_presidente_listar(message):
    """Lista os candidatos para exclusão"""
    ano_atual = db.get_ano_atual()
    candidatos = db.listar_candidatos(ano_atual)
    
    if not candidatos:
        bot.send_message(message.chat.id, "❌ Nenhum candidato cadastrado.")
        return
    
    mensagem = f"📋 *Candidatos de {ano_atual}:*\n\n"
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    
    for candidato in candidatos:
        candidato_id, nome, numero, foto_path, partido_nome, partido_sigla, ano = candidato
        mensagem += f"ID: {candidato_id} | {numero} - {nome}\n"
        markup.add(f"{candidato_id}")
    
    bot.send_message(message.chat.id, mensagem, parse_mode='Markdown', reply_markup=markup)
    bot.send_message(message.chat.id, "🔢 Digite o ID do candidato que deseja deletar:")
    bot.register_next_step_handler(message, deletar_presidente_finalizar)

def deletar_presidente_finalizar(message):
    """Finaliza a exclusão do candidato"""
    try:
        candidato_id = int(message.text)
        
        # Deleta a foto se existir
        candidato = db.get_candidato_por_id(candidato_id)
        if candidato and candidato[3]:
            foto_manager.deletar_foto(candidato[3])
        
        sucesso, mensagem = db.deletar_candidato(candidato_id)
        bot.send_message(
            message.chat.id, 
            f"{'✅' if sucesso else '❌'} {mensagem}",
            reply_markup=types.ReplyKeyboardRemove()
        )
    except ValueError:
        bot.send_message(message.chat.id, "❌ ID inválido.")

@bot.message_handler(commands=['lista_presidente'])
def lista_presidente(message):
    """Lista todos os candidatos"""
    ano_atual = db.get_ano_atual()
    candidatos = db.listar_candidatos(ano_atual)
    
    if not candidatos:
        bot.send_message(message.chat.id, f"❌ Nenhum candidato cadastrado para {ano_atual}.")
        return
    
    mensagem = f"📋 *Candidatos de {ano_atual}:*\n\n"
    
    for candidato in candidatos:
        candidato_id, nome, numero, foto_path, partido_nome, partido_sigla, ano = candidato
        mensagem += f"🔢 *{numero}* - {nome}"
        if partido_sigla:
            mensagem += f"\n   🏛️ {partido_nome} ({partido_sigla})"
        mensagem += "\n\n"
    
    bot.send_message(message.chat.id, mensagem, parse_mode='Markdown')

# ==================== CONTROLE DA VOTAÇÃO ====================

@bot.message_handler(commands=['definir_ano'])
def definir_ano_inicio(message):
    """Define o ano da votação"""
    verificar_senha(message, definir_ano_processar)

def definir_ano_processar(message):
    """Processa a definição do ano"""
    bot.send_message(message.chat.id, "📅 Digite o ano da votação:")
    bot.register_next_step_handler(message, definir_ano_finalizar)

def definir_ano_finalizar(message):
    """Finaliza a definição do ano"""
    try:
        ano = int(message.text)
        db.set_ano_atual(ano)
        bot.send_message(message.chat.id, f"✅ Ano da votação definido para {ano}!")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Ano inválido.")

@bot.message_handler(commands=['encerrar'])
def encerrar_votacao_inicio(message):
    """Encerra a votação"""
    verificar_senha(message, encerrar_votacao_processar)

def encerrar_votacao_processar(message):
    """Processa o encerramento da votação"""
    db.set_config('votacao_ativa', '0')
    bot.send_message(message.chat.id, "🔒 Votação encerrada com sucesso!")

@bot.message_handler(commands=['reabrir'])
def reabrir_votacao_inicio(message):
    """Reabre a votação"""
    verificar_senha(message, reabrir_votacao_processar)

def reabrir_votacao_processar(message):
    """Processa a reabertura da votação"""
    db.set_config('votacao_ativa', '1')
    bot.send_message(message.chat.id, "✅ Votação reaberta com sucesso!")

@bot.message_handler(commands=['zerar_votos'])
def zerar_votos_inicio(message):
    """Zera os votos do ano atual"""
    verificar_senha(message, zerar_votos_confirmar)

def zerar_votos_confirmar(message):
    """Confirma antes de zerar os votos"""
    ano_atual = db.get_ano_atual()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("✅ SIM", "❌ NÃO")
    
    bot.send_message(
        message.chat.id, 
        f"⚠️ Tem certeza que deseja apagar todos os votos de {ano_atual}?",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, zerar_votos_processar)

def zerar_votos_processar(message):
    """Processa o zeramento dos votos"""
    if message.text == "✅ SIM":
        ano_atual = db.get_ano_atual()
        sucesso, mensagem = db.zerar_votos(ano_atual)
        bot.send_message(
            message.chat.id, 
            f"{'✅' if sucesso else '❌'} {mensagem}",
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        bot.send_message(
            message.chat.id, 
            "❌ Operação cancelada.",
            reply_markup=types.ReplyKeyboardRemove()
        )

# ==================== RESULTADOS ====================

def mostrar_resultados(message, ano=None):
    """Mostra os resultados da votação"""
    if ano is None:
        ano = db.get_ano_atual()
    
    resultados = db.get_resultados(ano)
    total_votos = db.get_total_votos(ano)
    
    if total_votos == 0:
        bot.send_message(message.chat.id, f"❌ Nenhum voto registrado para {ano}.")
        return
    
    mensagem = f"📊 *Resultados da Eleição {ano}:*\n\n"
    
    vencedor = resultados[0] if resultados else None
    
    for nome, numero, sigla, votos in resultados:
        porcentagem = (votos / total_votos) * 100 if total_votos > 0 else 0
        mensagem += f"🔢 *{numero}* - {nome}"
        if sigla:
            mensagem += f" ({sigla})"
        mensagem += f"\n   📊 {votos} votos ({porcentagem:.2f}%)\n\n"
    
    mensagem += f"📈 *Total de votos:* {total_votos}\n"
    
    if vencedor and vencedor[3] > 0:
        mensagem += f"🏆 *Vencedor:* {vencedor[0]}\n"
    
    bot.send_message(message.chat.id, mensagem, parse_mode='Markdown')

@bot.message_handler(commands=['resultados_anteriores'])
def resultados_anteriores_inicio(message):
    """Mostra resultados de eleições anteriores"""
    anos = db.listar_anos_eleicoes()
    
    if not anos:
        bot.send_message(message.chat.id, "❌ Nenhuma eleição anterior encontrada.")
        return
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    
    for ano in anos:
        markup.add(str(ano))
    
    bot.send_message(
        message.chat.id, 
        "📅 *Eleições Anteriores:*\n\nEscolha um ano:",
        parse_mode='Markdown',
        reply_markup=markup
    )
    bot.register_next_step_handler(message, resultados_anteriores_mostrar)

def resultados_anteriores_mostrar(message):
    """Mostra os resultados do ano escolhido"""
    try:
        ano = int(message.text)
        mostrar_resultados(message, ano)
    except ValueError:
        bot.send_message(
            message.chat.id, 
            "❌ Ano inválido.",
            reply_markup=types.ReplyKeyboardRemove()
        )

# ==================== AJUDA ====================

@bot.message_handler(commands=['ajuda'])
def mostrar_ajuda(message):
    """Mostra a ajuda do sistema"""
    mensagem = """
📚 *COMANDOS DISPONÍVEIS:*

👥 *Para Eleitores:*
/start - Iniciar o bot
/ajuda - Mostrar esta ajuda

🔧 *Para Administradores:*

*Partidos:*
/cadastrar_partidos - Cadastrar partido
/lista_partidos - Listar partidos

*Candidatos:*
/inserir_presidente - Cadastrar candidato
/editar_presidente - Editar candidato
/deletar_presidente - Deletar candidato
/lista_presidente - Listar candidatos

*Votação:*
/definir_ano - Definir ano da eleição
/encerrar - Encerrar votação
/reabrir - Reabrir votação
/zerar_votos - Zerar votos do ano atual

*Resultados:*
/resultados_anteriores - Ver eleições anteriores

⚠️ Todos os comandos administrativos requerem senha.
    """
    bot.send_message(message.chat.id, mensagem, parse_mode='Markdown')

# ==================== INICIA O BOT ====================

if __name__ == '__main__':
    print("🤖 Bot iniciado com sucesso!")
    print(f"📅 Ano atual: {db.get_ano_atual()}")
    print(f"🗳️ Votação ativa: {'Sim' if db.votacao_ativa() else 'Não'}")
    bot.polling(none_stop=True)
