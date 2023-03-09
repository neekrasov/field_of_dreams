from field_of_dreams.core.common import Mediator
from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.handlers.join_chat import JoinToChatCommand
from field_of_dreams.infrastructure.tgbot import filters, types, bot


async def start(update: types.Update, bot: bot.Bot, mediator: Mediator):
    chat_id = update.message.chat.id  # type: ignore
    title = update.message.chat.title  # type: ignore

    await mediator.send(JoinToChatCommand(ChatID(chat_id), title))  # type: ignore # noqa
    await bot.send_message(
        chat_id,
        text=(
            "Привет! Я бот для игры 'Поле чудес' ! \n"
            "Чтобы начать играть, введите команду /game."
        ),
    )


def setup_handlers(bot: bot.TelegramBot):
    bot.add_handler(
        start,
        [
            filters.MessageFilter(),
            filters.GroupFilter(),
            filters.CommandFilter("/start"),
        ],
    )
