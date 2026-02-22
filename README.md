# 🗳️ Sistema de Votação Eletrônica - Telegram Bot

Sistema completo de votação eletrônica via Telegram com gerenciamento de candidatos, partidos e múltiplas eleições.

## 📋 Funcionalidades

### ✅ Principais Recursos

- ✅ **Validação de CPF Real**: Valida se o CPF existe usando BrasilAPI
- ✅ **Gestão de Fotos**: Fotos dos candidatos armazenadas automaticamente
- ✅ **Sistema de Partidos**: Cadastro e associação de candidatos a partidos
- ✅ **Múltiplas Eleições**: Histórico de eleições por ano
- ✅ **Edição de Candidatos**: Editar nome, número, partido e foto
- ✅ **Segurança**: Senha administrativa para operações sensíveis
- ✅ **Código Modular**: Dividido em módulos para melhor manutenção

### 🎯 Funcionalidades Detalhadas

#### Para Eleitores:
- Votação com validação de CPF real
- Visualização de fotos dos candidatos
- Confirmação de voto antes de registrar
- Impossível votar duas vezes na mesma eleição

#### Para Administradores:
- Cadastrar, editar e deletar partidos
- Cadastrar, editar e deletar candidatos
- Definir ano da eleição
- Encerrar e reabrir votações
- Ver resultados de eleições anteriores
- Zerar votos de um ano específico

## 📦 Instalação

### 1. Clone ou baixe os arquivos

```bash
# Estrutura de arquivos:
bot.py              # Arquivo principal do bot
database.py         # Gerenciamento do banco de dados
validacao.py        # Validação de CPF
foto_manager.py     # Gerenciamento de fotos
config.py           # Configurações
requirements.txt    # Dependências
.env.example        # Exemplo de configuração
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure o bot

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env e adicione suas configurações
nano .env
```

No arquivo `.env`, configure:
```
TELEGRAM_BOT_TOKEN=seu_token_do_botfather
SENHA_ADMIN=sua_senha_segura
```

### 4. Execute o bot

```bash
python bot.py
```

## 🎮 Comandos do Bot

### 👥 Comandos para Eleitores

| Comando | Descrição |
|---------|-----------|
| `/start` | Inicia o bot e permite votar |
| `/ajuda` | Mostra todos os comandos disponíveis |

### 🔧 Comandos Administrativos

#### Gestão de Partidos
| Comando | Descrição |
|---------|-----------|
| `/cadastrar_partidos` | Cadastra um novo partido |
| `/lista_partidos` | Lista todos os partidos cadastrados |

#### Gestão de Candidatos
| Comando | Descrição |
|---------|-----------|
| `/inserir_presidente` | Cadastra um novo candidato |
| `/editar_presidente` | Edita dados de um candidato |
| `/deletar_presidente` | Remove um candidato |
| `/lista_presidente` | Lista todos os candidatos |

#### Controle da Votação
| Comando | Descrição |
|---------|-----------|
| `/definir_ano` | Define o ano da eleição |
| `/encerrar` | Encerra a votação atual |
| `/reabrir` | Reabre a votação |
| `/zerar_votos` | Apaga todos os votos do ano atual |

#### Resultados
| Comando | Descrição |
|---------|-----------|
| `/resultados_anteriores` | Mostra resultados de eleições passadas |

## 🗂️ Estrutura do Banco de Dados

### Tabelas

#### `partidos`
- `id` - ID único do partido
- `nome` - Nome completo do partido
- `sigla` - Sigla do partido
- `data_criacao` - Data de criação

#### `candidatos`
- `id` - ID único do candidato
- `nome` - Nome completo
- `numero` - Número do candidato
- `foto_path` - Caminho da foto
- `partido_id` - ID do partido (FK)
- `ano` - Ano da candidatura
- `data_criacao` - Data de criação

#### `votos`
- `id` - ID único do voto
- `cpf` - CPF do eleitor
- `nome` - Nome do eleitor
- `candidato_id` - ID do candidato votado (FK)
- `ano` - Ano da eleição
- `data_voto` - Data e hora do voto

#### `configuracoes`
- `chave` - Nome da configuração
- `valor` - Valor da configuração

## 📸 Gerenciamento de Fotos

As fotos dos candidatos são armazenadas na pasta `foto_presidentes/`:

- A pasta é criada automaticamente se não existir
- Cada foto tem um nome único: `candidato_{numero}_{ano}_{timestamp}.jpg`
- Ao editar um candidato, a foto antiga é automaticamente deletada
- Ao deletar um candidato, a foto é removida junto

## 🔐 Validação de CPF

O sistema utiliza três níveis de validação:

1. **Formato**: Verifica se tem 11 dígitos
2. **Matemática**: Valida os dígitos verificadores
3. **API**: Consulta a BrasilAPI para verificar se o CPF existe

Se a API falhar, aceita apenas a validação matemática.

## 🎯 Fluxo de Votação

1. Eleitor inicia o bot com `/start`
2. Verifica se a votação está aberta
3. Solicita nome completo
4. Solicita e valida CPF (verifica se existe)
5. Verifica se já votou neste ano
6. Mostra candidatos com fotos
7. Confirma o voto
8. Registra no banco de dados

## 📊 Sistema de Múltiplas Eleições

- Cada eleição tem um ano associado
- Candidatos são cadastrados para um ano específico
- Eleitores podem votar uma vez por ano
- Resultados históricos ficam salvos
- Use `/resultados_anteriores` para ver eleições passadas

## ⚙️ Configurações Avançadas

### Alterar Timeout da API
No arquivo `config.py`:
```python
API_TIMEOUT = 5  # segundos
```

### Alterar Pasta de Fotos
No arquivo `config.py`:
```python
PASTA_FOTOS = 'fotos_candidatos'
```

### Alterar Senha Admin
No arquivo `.env`:
```
SENHA_ADMIN=nova_senha_segura
```

## 🛡️ Segurança

- Todas as operações administrativas requerem senha
- Senhas devem ser armazenadas em variáveis de ambiente
- Nunca compartilhe o arquivo `.env`
- CPF é validado antes de aceitar voto
- Impossível votar duas vezes no mesmo ano

## 🐛 Solução de Problemas

### Bot não inicia
```bash
# Verifique se o token está correto no arquivo .env
# Verifique se todas as dependências estão instaladas
pip install -r requirements.txt
```

### Erro ao validar CPF
```bash
# Verifique sua conexão com a internet
# A BrasilAPI pode estar temporariamente indisponível
# O sistema continuará funcionando com validação offline
```

### Fotos não aparecem
```bash
# Verifique se a pasta foto_presidentes existe
# Verifique as permissões da pasta
chmod 755 foto_presidentes
```

## 📝 Exemplos de Uso

### Cadastrar um Partido
```
/cadastrar_partidos
> Digite a senha: 1234
> Digite o nome completo do partido: Partido dos Trabalhadores
> Digite a sigla: PT
✅ Partido 'Partido dos Trabalhadores' (PT) adicionado com sucesso!
```

### Cadastrar um Candidato
```
/inserir_presidente
> Digite a senha: 1234
> Digite o ano da candidatura: 2024
> Digite o nome do candidato: João Silva
> Digite o número do candidato: 13
> Escolha o partido: 1 - PT
> Envie a foto do candidato: [envia foto]
✅ Candidato 'João Silva' (número 13) adicionado com sucesso!
```

### Votar
```
/start
> Digite seu nome completo: Maria Santos
> Digite seu CPF: 12345678901
> [Sistema valida CPF]
> Escolha seu candidato: 13 - João Silva (PT)
> [Mostra foto do candidato]
> Confirme seu voto: ✅ Confirmar
✅ Voto registrado com sucesso!
```

## 📄 Licença

Este projeto está sob a licença MIT. Sinta-se livre para usar e modificar.

## 👨‍💻 Desenvolvedor

Desenvolvido com ❤️ por Brunno

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se livre para:
- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no repositório.
