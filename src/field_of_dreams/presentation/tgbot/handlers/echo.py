from field_of_dreams.infrastructure.tgbot import TelegramBot


async def echo_handler(update: dict, bot: TelegramBot):
    await bot.send_message(
        update["message"]["chat"]["id"], update["message"]["text"]
    )
