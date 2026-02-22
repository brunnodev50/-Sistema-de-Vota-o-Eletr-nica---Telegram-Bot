#!/usr/bin/env python3
"""
Script de inicialização e verificação do sistema de votação
"""

import os
import sys

def verificar_arquivos():
    """Verifica se todos os arquivos necessários existem"""
    arquivos_necessarios = [
        'bot.py',
        'database.py',
        'validacao.py',
        'foto_manager.py',
        'config.py',
        'requirements.txt'
    ]
    
    print("🔍 Verificando arquivos...")
    faltando = []
    
    for arquivo in arquivos_necessarios:
        if not os.path.exists(arquivo):
            faltando.append(arquivo)
            print(f"   ❌ {arquivo} - NÃO ENCONTRADO")
        else:
            print(f"   ✅ {arquivo}")
    
    if faltando:
        print(f"\n❌ Arquivos faltando: {', '.join(faltando)}")
        return False
    
    print("\n✅ Todos os arquivos necessários estão presentes!")
    return True

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    print("\n🔍 Verificando dependências...")
    
    dependencias = {
        'telebot': 'pyTelegramBotAPI',
        'requests': 'requests',
        'dotenv': 'python-dotenv'
    }
    
    faltando = []
    
    for modulo, pacote in dependencias.items():
        try:
            __import__(modulo)
            print(f"   ✅ {pacote}")
        except ImportError:
            faltando.append(pacote)
            print(f"   ❌ {pacote} - NÃO INSTALADO")
    
    if faltando:
        print(f"\n❌ Dependências faltando: {', '.join(faltando)}")
        print("\n💡 Para instalar, execute:")
        print("   pip install -r requirements.txt")
        return False
    
    print("\n✅ Todas as dependências estão instaladas!")
    return True

def verificar_configuracao():
    """Verifica se o arquivo .env existe"""
    print("\n🔍 Verificando configuração...")
    
    if not os.path.exists('.env'):
        print("   ❌ Arquivo .env não encontrado")
        print("\n💡 Para configurar:")
        print("   1. Copie o arquivo: cp .env.example .env")
        print("   2. Edite o .env e adicione seu token do Telegram")
        return False
    
    print("   ✅ Arquivo .env encontrado")
    
    # Verifica se o token foi configurado
    with open('.env', 'r') as f:
        conteudo = f.read()
        if 'SEU_TOKEN_AQUI' in conteudo:
            print("   ⚠️  Token ainda não foi configurado no .env")
            return False
    
    print("   ✅ Token configurado")
    return True

def criar_pasta_fotos():
    """Cria a pasta de fotos se não existir"""
    print("\n🔍 Verificando pasta de fotos...")
    
    if not os.path.exists('foto_presidentes'):
        os.makedirs('foto_presidentes')
        print("   ✅ Pasta 'foto_presidentes' criada")
    else:
        print("   ✅ Pasta 'foto_presidentes' já existe")
    
    return True

def main():
    """Função principal"""
    print("=" * 60)
    print("🗳️  SISTEMA DE VOTAÇÃO ELETRÔNICA - VERIFICAÇÃO")
    print("=" * 60)
    
    # Verifica arquivos
    if not verificar_arquivos():
        sys.exit(1)
    
    # Verifica dependências
    if not verificar_dependencias():
        sys.exit(1)
    
    # Verifica configuração
    if not verificar_configuracao():
        sys.exit(1)
    
    # Cria pasta de fotos
    criar_pasta_fotos()
    
    print("\n" + "=" * 60)
    print("✅ SISTEMA PRONTO PARA USO!")
    print("=" * 60)
    print("\n💡 Para iniciar o bot, execute:")
    print("   python bot.py")
    print("\n📚 Para ver a documentação completa:")
    print("   cat README.md")
    print("\n")

if __name__ == '__main__':
    main()
