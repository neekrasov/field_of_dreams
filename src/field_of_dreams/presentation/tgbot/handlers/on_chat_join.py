from field_of_dreams.infrastructure.tgbot.bot import TelegramBot
from field_of_dreams.application.common import Mediator
from field_of_dreams.application.handlers.join_chat import JoinToChatCommand


async def on_chat_join(update: dict, bot: TelegramBot, mediator: Mediator):
    me = await bot.get_me()
    bot_name = me["result"]["username"]
    joined_name = update["message"]["new_chat_member"]["username"]
    if bot_name == joined_name:
        await mediator.send(
            JoinToChatCommand(
                chat_id=update["message"]["chat"]["id"],
                chat_name=update["message"]["chat"]["title"],
            )
        )
