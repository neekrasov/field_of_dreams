import aiohttp
import typing

from field_of_dreams.config import Settings
from .poller import BasePollerImpl
from .bot import TelegramBot
from .protocols import Poller, Bot


def build_telegram_bot(
    settings: Settings, session: aiohttp.ClientSession
) -> Bot:
    bot = TelegramBot(session, settings.bot.token)
    return bot


def build_poller(
    bot: Bot, settings: Settings, session: aiohttp.ClientSession
) -> Poller:
    poller = BasePollerImpl(session, bot, settings.bot.timeout)
    return poller


async def build_client_session() -> typing.AsyncGenerator[
    aiohttp.ClientSession, None
]:
    session = aiohttp.ClientSession()
    yield session
    await session.close()
