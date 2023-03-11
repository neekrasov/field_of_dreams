import logging

from field_of_dreams.infrastructure.tgbot import filters, types, protocols
from field_of_dreams.core.common import Mediator
from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.handlers.get_chat_stats import GetChatStatsCommand

logger = logging.getLogger()


async def show_stats(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
):
    await mediator.send(GetChatStatsCommand(ChatID(update.message.chat.id)))  # type: ignore # noqa


def setup_handlers(bot: protocols.Bot):
    bot.add_handler(show_stats, [filters.CommandFilter("/top")])
