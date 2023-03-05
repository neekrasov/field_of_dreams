import logging

from field_of_dreams.infrastructure.tgbot import TelegramBot
from field_of_dreams.application.common.exception import ApplicationException


logger = logging.getLogger()


async def application_exception_handler(
    update: dict, e: ApplicationException, bot: TelegramBot
):
    chat_id = update["message"]["chat"]["id"]
    logger.info(
        "Exception in chat {}: {}".format(
            chat_id,
            e.message,
        )
    )
    await bot.send_message(chat_id, e.message)
