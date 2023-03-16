import logging

from field_of_dreams.core.common import Mediator
from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.handlers.join_chat import JoinToChatCommand
from field_of_dreams.infrastructure.tgbot import filters, types, bot, protocols

logger = logging.getLogger()


async def start(
    update: types.Update,
    bot: bot.Bot,
    mediator: Mediator,
    storage: protocols.Storage,
):
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


async def help(update: types.Update, bot: bot.Bot):
    chat_id = update.message.chat.id  # type: ignore
    await bot.send_message(
        chat_id,
        text=(
            "🤖Команды:\n"
            "/help - получить справку.\n"
            "/start - начать взаимодействие с ботом. \n"
            "/game - начать игру. \n"
            "/finish - принудительно завершить игру "
            "(только от имени инициатора или администратора чата).\n"
            "/top - посмотреть топ игроков чата.\n"
            "\n📒Правила:\n"
            "Игроки по очереди называют буквы и им присвается рандомное "
            "количество баллов в случае успешного ответа. "
            "Ход передается другому игроку, если была названа "
            "буква которой нет в слове или она была названа раньше. "
            "Есть возможность назвать слово сразу. "
            "Если пользователь ответил правильно - ему присуждается победа. "
            "Если ответ неверный - он выбывает из игры. "
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
    bot.add_handler(
        help,
        [
            filters.MessageFilter(),
            filters.GroupFilter(),
            filters.CommandFilter("/help"),
        ],
    )
