# 🤖 group-telegram-with-bot

Bot assíncrono para grupos de Telegram que realiza sorteios semanais e interage com usuários com base em comandos.

---

## 🚀 Funcionalidades

- Permite que membros do grupo façam **check-in semanal**
- Permite **vincular LNADDRESS**
- Realiza **sorteios automáticos** entre os participantes

---

## 📝 Lista de comandos

- 🔗 /vincular + LNAddress : configura um endereço de recebimento para seu usuario
- ℹ️ /info : Mostra informações sobre o proximo sorteio
- ☑️ /check_in : Valida sua participação no sorteio da semana atual
- 🤖 /bot : Mostra mensagem de boas vindas
- ⌨️ /comandos : Mostra os comandos do bot

---

## 🔧 Variáveis de Ambiente

Essas variáveis devem ser definidas no painel do Coolify ou num arquivo `.env` (caso esteja rodando localmente).

| Variável       | Descrição                                                                        |
|----------------|----------------------------------------------------------------------------------|
| `BOT_TOKEN`    | Token do seu bot do Telegram (obtido com o [@BotFather](https://t.me/BotFather)) |
| `CHAT_ID`      | ID do grupo onde o bot vai operar (com sinal de `-` se for supergrupo)           |
| `nwc_uri`      | URI da carteira NWC para geração de invoice                                      |
| `prize_amount` | Quantidade de sats para o sorteio semanal (Opcional, o padrão é 100 sats)        |
| `DEV_MODE`     | Modo de desenvolvimento (Opcional, `True` ou `False`, por padrão é `False`)      |

---

## 🐳 Docker

### Build e execução local

- Defina as variaveis de ambiente e rode o comando

```bash
docker compose up --build

