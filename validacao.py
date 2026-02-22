import requests
import re

def validar_cpf_formato(cpf):
    """Valida o formato do CPF (somente números e 11 dígitos)"""
    cpf = re.sub(r'\D', '', cpf)
    return len(cpf) == 11 and cpf.isdigit()

def calcular_digito_verificador(cpf, posicoes):
    """Calcula um dígito verificador do CPF"""
    soma = sum(int(cpf[i]) * posicoes[i] for i in range(len(posicoes)))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto

def validar_cpf_matematicamente(cpf):
    """Valida o CPF matematicamente (dígitos verificadores)"""
    cpf = re.sub(r'\D', '', cpf)
    
    if not validar_cpf_formato(cpf):
        return False
    
    # CPFs com todos os dígitos iguais são inválidos
    if cpf == cpf[0] * 11:
        return False
    
    # Valida primeiro dígito verificador
    posicoes_primeiro = list(range(10, 1, -1))
    primeiro_digito = calcular_digito_verificador(cpf[:9], posicoes_primeiro)
    
    if primeiro_digito != int(cpf[9]):
        return False
    
    # Valida segundo dígito verificador
    posicoes_segundo = list(range(11, 1, -1))
    segundo_digito = calcular_digito_verificador(cpf[:10], posicoes_segundo)
    
    return segundo_digito == int(cpf[10])

def validar_cpf_api(cpf):
    """Valida o CPF através de uma API externa para verificar se existe"""
    cpf = re.sub(r'\D', '', cpf)
    
    if not validar_cpf_matematicamente(cpf):
        return False, "CPF inválido matematicamente"
    
    try:
        # Usando API pública de validação de CPF
        url = f"https://brasilapi.com.br/api/cpf/v1/{cpf}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return True, "CPF válido"
        else:
            return False, "CPF não encontrado na base de dados"
    except requests.exceptions.RequestException:
        # Se a API falhar, aceita apenas validação matemática
        if validar_cpf_matematicamente(cpf):
            return True, "CPF válido (validação offline)"
        return False, "CPF inválido"

def validar_cpf(cpf):
    """Função principal de validação de CPF"""
    cpf_limpo = re.sub(r'\D', '', cpf)
    
    # Primeira validação: formato
    if not validar_cpf_formato(cpf_limpo):
        return False, "CPF deve conter 11 dígitos"
    
    # Segunda validação: matemática
    if not validar_cpf_matematicamente(cpf_limpo):
        return False, "CPF inválido"
    
    # Terceira validação: API (verifica se existe)
    valido, mensagem = validar_cpf_api(cpf_limpo)
    
    return valido, mensagem
