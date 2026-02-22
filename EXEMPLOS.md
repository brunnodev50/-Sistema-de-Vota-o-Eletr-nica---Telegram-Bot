# 📖 EXEMPLOS PRÁTICOS DE USO

## 🎯 Cenário Completo: Criando uma Eleição

### Passo 1: Configuração Inicial

```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Configure o token
cp .env.example .env
nano .env  # Adicione seu token do Telegram

# 3. Verifique se está tudo ok
python setup.py

# 4. Inicie o bot
python bot.py
```

### Passo 2: Cadastrar Partidos

**Administrador usa o comando:** `/cadastrar_partidos`

```
Bot: 🔒 Digite a senha de administrador:
Você: 1234

Bot: 🏛️ Digite o nome completo do partido:
Você: Partido dos Trabalhadores

Bot: 🔤 Digite a sigla do partido (ex: PT, PSDB):
Você: PT

Bot: ✅ Partido 'Partido dos Trabalhadores' (PT) adicionado com sucesso!
```

**Cadastre mais partidos:**

```
/cadastrar_partidos
Senha: 1234
Nome: Partido da Social Democracia Brasileira
Sigla: PSDB
✅ Partido adicionado!

/cadastrar_partidos
Senha: 1234
Nome: Partido Liberal
Sigla: PL
✅ Partido adicionado!
```

### Passo 3: Definir o Ano da Eleição

**Comando:** `/definir_ano`

```
Bot: 🔒 Digite a senha de administrador:
Você: 1234

Bot: 📅 Digite o ano da votação:
Você: 2024

Bot: ✅ Ano da votação definido para 2024!
```

### Passo 4: Cadastrar Candidatos

**Primeiro candidato:** `/inserir_presidente`

```
Bot: 🔒 Digite a senha de administrador:
Você: 1234

Bot: 📅 Digite o ano da candidatura:
Você: 2024

Bot: 👤 Digite o nome do candidato:
Você: João Silva

Bot: 🔢 Digite o número do candidato:
Você: 13

Bot: 🏛️ Escolha o partido:
     1. PT - Partido dos Trabalhadores
     2. PSDB - Partido da Social Democracia Brasileira
     3. PL - Partido Liberal
     [Sem partido]
     
Você: [Clica em "1 - PT"]

Bot: 📸 Envie a foto do candidato (ou digite 'PULAR' para cadastrar sem foto):
Você: [Envia uma foto]

Bot: ✅ Candidato 'João Silva' (número 13) adicionado com sucesso!
```

**Segundo candidato:**

```
/inserir_presidente
Senha: 1234
Ano: 2024
Nome: Maria Santos
Número: 45
Partido: 2 - PSDB
Foto: [envia foto]
✅ Candidato adicionado!
```

**Terceiro candidato:**

```
/inserir_presidente
Senha: 1234
Ano: 2024
Nome: Pedro Oliveira
Número: 22
Partido: 3 - PL
Foto: [envia foto]
✅ Candidato adicionado!
```

### Passo 5: Verificar Candidatos

**Comando:** `/lista_presidente`

```
Bot: 📋 Candidatos de 2024:

     🔢 13 - João Silva
        🏛️ Partido dos Trabalhadores (PT)

     🔢 22 - Pedro Oliveira
        🏛️ Partido Liberal (PL)

     🔢 45 - Maria Santos
        🏛️ Partido da Social Democracia Brasileira (PSDB)
```

### Passo 6: Eleitores Votam

**Eleitor 1:**

```
Eleitor: /start

Bot: 🗳️ Bem-vindo ao Sistema de Votação Eletrônica!
     📅 Ano da eleição: 2024
     Status: ✅ Votação ABERTA
     
     Para votar, digite seu nome completo ou use o botão abaixo.

Eleitor: Carlos Alberto

Bot: 🆔 Digite seu CPF (somente números):
Eleitor: 12345678901

Bot: [Valida CPF via API]
     🗳️ Escolha seu candidato:
     [13 - João Silva (PT)]
     [22 - Pedro Oliveira (PL)]
     [45 - Maria Santos (PSDB)]

Eleitor: [Clica em "13 - João Silva (PT)"]

Bot: [Mostra foto do João Silva]
     ✅ Confirme seu voto:
     
     📋 Candidato: João Silva
     🔢 Número: 13
     🏛️ Partido: Partido dos Trabalhadores (PT)
     
     [✅ Confirmar] [❌ Cancelar]

Eleitor: [Clica em "✅ Confirmar"]

Bot: ✅ Voto registrado com sucesso!
     Obrigado por participar!
```

**Eleitor 2:**

```
/start
Nome: Ana Paula
CPF: 98765432100
Vota: 45 - Maria Santos (PSDB)
Confirma: ✅
✅ Voto registrado!
```

**Eleitor 3:**

```
/start
Nome: Roberto Costa
CPF: 11122233344
Vota: 13 - João Silva (PT)
Confirma: ✅
✅ Voto registrado!
```

### Passo 7: Ver Resultados Durante a Votação

**Qualquer pessoa pode usar:** `/start` > "📊 Ver Resultados"

```
Bot: 📊 Resultados da Eleição 2024:

     🔢 13 - João Silva (PT)
        📊 2 votos (66.67%)

     🔢 45 - Maria Santos (PSDB)
        📊 1 voto (33.33%)

     🔢 22 - Pedro Oliveira (PL)
        📊 0 votos (0.00%)

     📈 Total de votos: 3
     🏆 Vencedor: João Silva
```

### Passo 8: Encerrar a Votação

**Comando:** `/encerrar`

```
Bot: 🔒 Digite a senha de administrador:
Você: 1234

Bot: 🔒 Votação encerrada com sucesso!
```

Agora quando eleitores tentarem votar:

```
Eleitor: /start

Bot: 🗳️ Bem-vindo ao Sistema de Votação Eletrônica!
     📅 Ano da eleição: 2024
     Status: 🔒 Votação ENCERRADA
     
     A votação está encerrada. Você pode ver os resultados.
     [📊 Ver Resultados]
```

## 🔄 Cenários Adicionais

### Editar um Candidato

**Cenário:** Erro no número do candidato

```
/editar_presidente
Senha: 1234

Bot: 📋 Candidatos de 2024:
     ID: 1 | 13 - João Silva (PT)
     ID: 2 | 22 - Pedro Oliveira (PL)
     ID: 3 | 45 - Maria Santos (PSDB)
     
     🔢 Digite o ID do candidato que deseja editar:

Você: 2

Bot: ✏️ O que deseja editar?
     [Nome] [Número] [Partido] [Foto]

Você: [Clica em "Número"]

Bot: 🔢 Digite o novo número:
Você: 17

Bot: ✅ Candidato atualizado com sucesso!
```

### Mudar Partido de um Candidato

```
/editar_presidente
Senha: 1234
ID do candidato: 3
Campo: Partido
Novo partido: 1 - PT
✅ Candidato atualizado com sucesso!
```

### Ver Eleições Anteriores

**Cenário:** Ano seguinte, nova eleição

```
# Primeiro, defina o novo ano
/definir_ano
Senha: 1234
Ano: 2025

# Cadastre novos candidatos para 2025
# ... (mesmo processo)

# Para ver resultados de 2024:
/resultados_anteriores

Bot: 📅 Eleições Anteriores:
     [2024]
     [2023]
     
Você: [Clica em "2024"]

Bot: 📊 Resultados da Eleição 2024:
     [mostra resultados de 2024]
```

### Zerar Votos de um Ano

**Cenário:** Teste ou erro, precisa recomeçar

```
/zerar_votos
Senha: 1234

Bot: ⚠️ Tem certeza que deseja apagar todos os votos de 2024?
     [✅ SIM] [❌ NÃO]

Você: [Clica em "✅ SIM"]

Bot: ✅ Todos os votos do ano 2024 foram apagados.
```

## ❌ Cenários de Erro

### CPF Inválido

```
Eleitor: /start
Nome: José Silva
CPF: 12345678900  (CPF inválido)

Bot: ❌ CPF inválido
     Digite novamente seu CPF:

Eleitor: 11111111111  (Todos dígitos iguais)

Bot: ❌ CPF inválido
     Digite novamente seu CPF:

Eleitor: 12345678901  (CPF válido)

Bot: ✅ [Continua o processo]
```

### Tentativa de Votar Duas Vezes

```
Eleitor: /start
Nome: Carlos Alberto
CPF: 12345678901  (Já votou antes)

Bot: ❌ Este CPF já votou nesta eleição!
     Você não pode votar mais de uma vez.
```

### Número de Candidato Duplicado

```
/inserir_presidente
Senha: 1234
Ano: 2024
Nome: Novo Candidato
Número: 13  (Já existe)

Bot: ❌ Já existe um candidato com o número 13 para o ano 2024.
```

### Votação Encerrada

```
Eleitor: /start

Bot: 🗳️ Status: 🔒 Votação ENCERRADA
     A votação está encerrada. Você pode ver os resultados.
```

## 💡 Dicas de Uso

### 1. Organização de Partidos

Cadastre todos os partidos **antes** de cadastrar candidatos:

```
/cadastrar_partidos (PT)
/cadastrar_partidos (PSDB)
/cadastrar_partidos (PL)
/cadastrar_partidos (PDT)
/lista_partidos  (para verificar)
```

### 2. Números dos Candidatos

Use números tradicionais dos partidos:
- PT: 13
- PSDB: 45
- PL: 22
- PDT: 12

### 3. Fotos de Qualidade

- Use fotos quadradas (melhor visualização)
- Formato JPG ou PNG
- Tamanho recomendado: 500x500 pixels
- Fundo neutro

### 4. Backup do Banco

Faça backup regular do arquivo `votacao.db`:

```bash
# Backup diário
cp votacao.db backup_$(date +%Y%m%d).db

# Restaurar backup
cp backup_20240101.db votacao.db
```

### 5. Segurança da Senha

Mude a senha padrão no arquivo `.env`:

```bash
SENHA_ADMIN=minha_senha_super_segura_123
```

## 🎓 Casos de Uso Reais

### Eleição de Condomínio

```
1. Defina o ano: 2024
2. Cadastre os candidatos:
   - Síndico A (número 1)
   - Síndico B (número 2)
   - Síndico C (número 3)
3. Abra a votação por 7 dias
4. Encerre e divulgue resultados
```

### Eleição Estudantil

```
1. Cadastre chapas:
   - Chapa 1 - Renovação
   - Chapa 2 - Mudança
   - Chapa 3 - União
2. Cada chapa com foto e número
3. Votação de 24 horas
4. Resultados em tempo real
```

### Pesquisa de Opinião

```
1. Use candidatos como "opções"
2. Números de 1 a 5 (escala)
3. Sem fotos necessárias
4. Resultados imediatos
```

## 🔧 Manutenção

### Verificar Status

```python
# Execute no terminal Python:
from database import DatabaseManager
db = DatabaseManager()

print(f"Ano atual: {db.get_ano_atual()}")
print(f"Votação ativa: {db.votacao_ativa()}")
print(f"Total de votos: {db.get_total_votos()}")
```

### Limpar Dados Antigos

```python
# Apagar eleições muito antigas
from database import DatabaseManager
db = DatabaseManager()

# Apagar votos de 2020
db.zerar_votos(2020)
```

Esses exemplos cobrem os principais cenários de uso do sistema! 🎉
