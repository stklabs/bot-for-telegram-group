import asyncio

import aiohttp
from aiohttp.client_exceptions import *
from nostr_sdk import (NostrWalletConnectUri, Nwc, PayInvoiceRequest)

from settings import setup


async def is_valid_ln_address(ln_address: str) -> bool:
    nickname, domain = ln_address.split("@")
    url = f"https://{domain}/.well-known/lnurlp/{nickname}"
    try:
        async with aiohttp.ClientSession() as session:
            # Etapa 1: Obter dados do LNURL-pay
            async with session.get(url) as resp:
                lnurl_data = await resp.json()

            if lnurl_data.get("status", None):
                return False
            return True
    except (ContentTypeError, ClientConnectorDNSError):
        return False


async def get_invoice_of_ln_address(
        ln_address: str, amount_sat: int, comment: str = "") -> str | None:
    amount_msat = amount_sat * 1000
    nickname, domain = ln_address.split("@")
    url = f"https://{domain}/.well-known/lnurlp/{nickname}"

    async with aiohttp.ClientSession() as session:
        # Etapa 1: Obter dados do LNURL-pay
        async with session.get(url) as resp:
            lnurl_data = await resp.json()

        if callback_url := lnurl_data.get("callback", None):
            min_amt = lnurl_data.get("minSendable", 1000)
            max_amt = lnurl_data.get("maxSendable", setup.prize_amount * 1000)
            if not (min_amt <= amount_msat <= max_amt):
                raise ValueError(
                    f"O valor deve estar entre {min_amt // 1000} e {max_amt // 1000} sats")

            # Etapa 2: Obter a fatura/invoice
            params = {"amount": amount_msat}
            if comment:
                max_comment_len = lnurl_data.get("commentAllowed", 0)
                if len(comment) <= max_comment_len:
                    params["comment"] = comment
            async with session.get(callback_url, params=params) as resp:
                invoice_data = await resp.json()
            return invoice_data["pr"]
        return None


async def send_prize(ln_address: str) -> tuple[str, str] | None:
    uri = NostrWalletConnectUri.parse(setup.nwc_uri)
    nwc = Nwc(uri)

    invoice = await get_invoice_of_ln_address(
        ln_address, setup.prize_amount,
        "🎉 Parabens! Você ganhou o premio dessa semana da Sats Lottu no Telegram! 🤑")
    if invoice:
        params = PayInvoiceRequest(invoice=invoice, id=None, amount=setup.prize_amount * 1000)
        result = await nwc.pay_invoice(params)
        return invoice, result.preimage
    return None


if __name__ == '__main__':
    asyncio.run(send_prize("fewruth77@walletofsatoshi.com"))
