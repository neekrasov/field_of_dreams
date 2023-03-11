import logging

from field_of_dreams.infrastructure.tgbot import bot, states, types
from field_of_dreams.core.common.exception import (
    ApplicationException,
    GameOver,
    QueueAccessError,
)

logger = logging.getLogger("bot")


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
    state = bot.get_state(chat_id)
    if state and state.value.data:
        task = state.value.data.get("task")
        if task:
            task.cancel()
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
