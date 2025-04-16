from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
from settings import setup
from email.utils import parseaddr
from db import (save_ln_address, get_ln_address, get_username_ln_address_total_check_in,
                check_in, clear_checkins, count_checkins, is_checked)
from scheduler.asyncio import Scheduler
from scheduler.trigger import *
from datetime import timezone, timedelta, time, date, datetime
from payment import send_prize, is_valid_ln_address

bot = Bot(token=setup.BOT_TOKEN)
dp = Dispatcher()

sort_day_text = "Sexta"
sort_day = 4  # De 0 - 6 onde 0 é Segunda e 6 é Domingo


def is_valid_email(email: str) -> bool:
    name, addr = parseaddr(email)
    return "@" in addr and "." in addr


def next_saturday():
    today = date.today()
    days_until_saturday = (sort_day - today.weekday()) % 7
    if days_until_saturday == 0:
        days_until_saturday = 7
    result = today + timedelta(days=days_until_saturday)
    return result.day


async def async_filter(async_func, iterable):
    for item in iterable:
        should_yield = await async_func(item)
        if should_yield:
            yield item


@dp.message(Command("vincular"))
async def link_command(message: Message):
    if username := message.from_user.username:
        if message.text:
            texto = message.text.lower().split()
            email = list(filter(is_valid_email, texto))
            valid_ln_address = [a async for a in async_filter(is_valid_ln_address, email)]
            if len(valid_ln_address) > 1:
                await message.reply("❌ Apenas um LNAddress pode ser vinculado.\n"
                                    "Por favor tente com apenas um endereço!")
            elif len(valid_ln_address) == 1:
                user_id = message.from_user.id
                save_ln_address(user_id, username, valid_ln_address[0])
                await message.reply(f"✅ Endereço de pagamento cadastrado com "
                                    f"sucesso: {valid_ln_address[0]}\n"
                                    f"Para participar dos nossos sorteios,"
                                    f" faça o /check_in semanal.")
            else:
                await message.reply("❌ Nenhum Endereço valido detectado!\n"
                                    "Por favor tente novamente com outro endereço!")
    else:
        await message.reply("⚙️ Antes de vincular o endereço configure seu username no seu perfil!")


@dp.message(Command("info"))
async def info_command(message: Message):
    msg = ("⚠️INFORMAÇÕES | FREE SATS\n"
           f"🗓 Sorteio {sort_day_text}, dia {next_saturday()} às 20:00 UTC:\n"
           f"👥 Número de participantes: {count_checkins()}\n\n"
           f"⚡️Prêmio: {setup.prize_amount} sats\n"
           "\n---\n\n"
           "1️⃣ Vincular endereço\n"
           "Vincule seu endereço lightning (Lnaddees) de alguma carteira "
           "compatível para poder participar.\n\n"
           "Como fazer: passe o comando /vincular + seu endereço lightning.\n\n"
           "Ex: /vincular seuendereco@lnaddress.com\n\n"
           "2️⃣ Faça o Check in semanal\n\n"
           "Após vincular seu endereço, passe o comando /check_in para "
           "participar do sorteio semanal.\n"
           "\n---\n\n"
           "📝 Lista de comandos:\n"
           "🔗 /vincular + LNAddress : configura um endereço de recebimento para seu usuario\n"
           "ℹ️ /info : Mostra informações\n"
           "☑️ /check_in : Valida sua participação no sorteio da semana atual\n"
           "🤖 /bot : Mostra mensagem de boas vindas\n"
           "⌨️ /comandos : Mostra os comandos do bot\n"
           "👤 /perfil : Exibe seu endereço cadastrado para recebimento\n")
    await message.reply(msg)


@dp.message(Command("perfil"))
async def info_command(message: Message):
    user_id = message.from_user.id
    if ln_address := get_ln_address(user_id):
        msg = ("🔸Seus dados cadastrados\n\n"
               f"Lnaddress: {ln_address}")
        if is_checked(user_id) is False:
            msg += (f"\n\n☑️ Faça o Check-in com o comando /check_in "
                    "para participar do sorteio dessa semana!\n")
        await message.reply(msg)

    else:
        await message.reply("Você ainda não tem perfil!\n "
                            "Siga o passo a passo descrito em /info "
                            "para ter seu perfil.")


@dp.message(Command("check_in"))
async def check_in_command(message: Message):
    user_id = message.from_user.id
    check_in(user_id)
    checked = is_checked(user_id)
    if checked is True:
        await message.reply(
            "🎉 Parabens!\n"
            f"🤑 Agora você está participando do sorteio "
            f"semanal valendo {setup.prize_amount} sats!\n"
            f"🗓 Acontecerá no proximo {sort_day_text}, dia {next_saturday()} às 20:00 UTC"
        )
    else:
        await message.reply(
            "🔗 Vincule seu endereço lightning (Lnaddees) de alguma "
            "carteira compatível para poder participar.\n\n"
            "Como fazer: passe o comando /vincular + seu endereço lightning.\n\n"
            "Ex: /vincular seuendereco@lnaddress.com"
        )


@dp.message(Command("comandos"))
async def commands_command(message: Message):
    await message.reply(
        "📝 Lista de comandos:\n\n"
        "🔗 /vincular + LNAddress : configura um endereço de recebimento para seu usuario\n"
        "ℹ️ /info : Mostra informações sobre o proximo sorteio\n"
        "☑️ /check_in : Valida sua participação no sorteio da semana atual\n"
        "🤖 /bot : Mostra mensagem de boas vindas\n"
        "⌨️ /comandos : Mostra os comandos do bot\n"
        "👤 /perfil : Exibe seu endereço cadastrado para recebimento\n"
    )


@dp.message(Command("bot"))
async def bot_command(message: Message):
    first_name = message.from_user.first_name
    await message.reply(
        f"Olá {first_name}! 👋\n"
        "⌨️ Use /comandos para ver os comandos do bot!"
    )


async def sort():
    if result := get_username_ln_address_total_check_in():
        ln_address, username, total = result
        if result := await send_prize(ln_address):
            invoice, preimage = result
            today = datetime.now()
            link = f"https://lnreceipt.jaonoctus.dev/?invoice={invoice}&preimage={preimage}"
            await bot.send_message(
                chat_id=setup.CHAT_ID,
                text=f"🍀 SORTEIO | LNADDRESS PREMIADO {today.strftime('%d / %m / %Y')}\n\n"
                     f"Prêmio: {setup.prize_amount} sats\n"
                     f"Participantes: {total}\n"
                     f"Vencedor: @{username}\n"
                     f"Endereço de pagamento: {ln_address}\n"
                     f"Data do sorteio: {today.strftime('%d / %m / %Y - %H:%M:%S')}\n"
                     f"Invoice: <a href='{link}'>{invoice}</a>\n\n"
                     f"⚡️⚡️ Parabéns, você foi o vencedor dessa semana, Stay Humble, stack sats.",
                parse_mode="HTML"
            )
            clear_checkins()
    else:
        await bot.send_message(
            chat_id=setup.CHAT_ID,
            text=f"Parece que Ninguem quer SATS! 😢"
        )


async def main():
    schedule = Scheduler(tzinfo=timezone.utc)
    if setup.DEV_MODE:
        schedule.cyclic(timedelta(minutes=1), sort)
    else:
        schedule.weekly(
            [
                Friday(time(hour=20, tzinfo=timezone.utc)),
            ],
            sort
        )
    print("Rotina de sorteios iniciada...")
    print("Bot rodando no grupo...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
