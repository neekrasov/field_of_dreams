import logging
import asyncio

from aiohttp.client import ClientResponseError
from field_of_dreams.infrastructure.tgbot import bot, states, types
from field_of_dreams.core.common.exception import (
    ApplicationException,
    GameOver,
    QueueAccessError,
)

logger = logging.getLogger()


async def application_exception_handler(
    update: types.Update, e: ApplicationException, bot: bot.Bot
):
    chat_id = update.message.chat.id  # type: ignore
    logger.info(
        "Exception in chat {}: {}".format(
            chat_id,
            e.message,
        )
    )
    await bot.send_message(chat_id, e.message)


async def game_over_exception_handler(
    update: types.Update, e: GameOver, bot: bot.Bot
):
    if update.message:
        chat_id = update.message.chat.id  # type: ignore
    else:
        chat_id = update.callback_query.message.chat.id  # type: ignore
    timer = bot.get_timer(chat_id)
    if timer:
        timer.del_all()
    bot.set_state(chat_id, states.GameState.FINISHED)
    await bot.send_message(chat_id, e.message)


async def queue_access_exception_handler(
    update: types.Update, e: QueueAccessError, bot: bot.Bot
):
    if update.message:
        chat_id = update.message.chat.id  # type: ignore
        await bot.send_message(chat_id, e.message)
    else:
        chat_id = update.callback_query.message.chat.id  # type: ignore
        await bot.answer_callback_query(update.callback_query.id, e.message)  # type: ignore # noqa


async def too_many_requests_handler(
    update: types.Update, e: ClientResponseError, bot: bot.Bot
):
    logging.info("Too many requests error")
    await asyncio.sleep(20)
    msg = "Сервер перегружен, пожалуйста начните игру позже..."
    if update.message:
        chat_id = update.message.chat.id  # type: ignore
        await bot.send_message(chat_id, msg)
    else:
        chat_id = update.callback_query.message.chat.id  # type: ignore
        await bot.answer_callback_query(update.callback_query.id, msg)  # type: ignore # noqa

    timer = bot.get_timer(chat_id)  # type: ignore
    if timer:
        timer.del_all()
