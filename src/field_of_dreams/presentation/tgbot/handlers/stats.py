import logging

from field_of_dreams.infrastructure.tgbot import filters, types, protocols
from field_of_dreams.core.common import Mediator
from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.entities.user import UserID
from field_of_dreams.core.handlers.get_chat_stats import GetChatStatsCommand
from field_of_dreams.core.handlers.get_user_stats import GetUserStatsCommand

from field_of_dreams.presentation.tgbot.middlewares.throttling import (
    throttling,
)

logger = logging.getLogger()


@throttling()
async def show_chat_stats(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
):
    await mediator.send(GetChatStatsCommand(ChatID(update.message.chat.id)))  # type: ignore # noqa


@throttling()
async def show_user_stats(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
):
    await mediator.send(
        GetUserStatsCommand(
            UserID(update.message.from_user.id),  # type: ignore
            ChatID(update.message.chat.id),  # type: ignore
            update.message.from_user.username,  # type: ignore
        )
    )


def setup_handlers(bot: protocols.Bot):
    bot.add_handler(show_chat_stats, [filters.CommandFilter("/top")])
    bot.add_handler(show_user_stats, [filters.CommandFilter("/score")])
