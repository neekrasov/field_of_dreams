import logging
import asyncio

from aiohttp.client import ClientResponseError
from field_of_dreams.infrastructure.tgbot import types, protocols
from field_of_dreams.presentation.tgbot.states import GameStatus, GameState
from field_of_dreams.core.common.exception import (
    ApplicationException,
    GameOver,
    QueueAccessError,
)

logger = logging.getLogger()


async def application_exception_handler(
    update: types.Update, e: ApplicationException, bot: protocols.Bot, **kwargs
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
    update: types.Update,
    e: GameOver,
    bot: protocols.Bot,
    storage: protocols.Storage,
):
    if update.message:
        chat_id = update.message.chat.id  # type: ignore
    else:
        chat_id = update.callback_query.message.chat.id  # type: ignore

    logger.info("Game over in chat %s", chat_id)
    timer = bot.get_timer(chat_id)
    if timer:
        timer.del_all()
    await storage.set_state(chat_id, GameState(GameStatus.FINISHED))
    await bot.send_message(chat_id, e.message)


async def queue_access_exception_handler(
    update: types.Update, e: QueueAccessError, bot: protocols.Bot, **kwargs
):
    if update.message:
        chat_id = update.message.chat.id  # type: ignore
        user_id = update.message.from_user.id  # type: ignore
        logger.info(
            "Queue access exception in chat %s, for user %s ", chat_id, user_id
        )
        await bot.send_message(chat_id, e.message)
    else:
        chat_id = update.callback_query.message.chat.id  # type: ignore
        user_id = update.callback_query.from_user.id  # type: ignore
        logger.info(
            "Queue access exception in chat %s, for user %s ", chat_id, user_id
        )
        await bot.answer_callback_query(update.callback_query.id, e.message)  # type: ignore # noqa


async def too_many_requests_handler(
    update: types.Update, e: ClientResponseError, bot: protocols.Bot, **kwargs
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
