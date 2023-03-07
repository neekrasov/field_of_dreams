from field_of_dreams.infrastructure.tgbot import filters, types, bot
from field_of_dreams.core.common import Mediator
from field_of_dreams.core.handlers.join_chat import JoinToChatCommand


async def on_chat_join(
    update: types.Update, bot: bot.TelegramBot, mediator: Mediator
):
    me = await bot.get_me()
    joined_name = update.message.new_chat_member.username  # type: ignore
    if me.username == joined_name:
        await mediator.send(
            JoinToChatCommand(
                update.message.chat.id,  # type: ignore
                update.message.chat.title,  # type: ignore
            )
        )


def setup_handlers(bot: bot.TelegramBot):
    bot.add_handler(
        on_chat_join, [filters.GroupFilter(), filters.OnChatJoinFilter()]
    )
