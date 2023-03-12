from field_of_dreams.config import Settings
from ..tgbot.protocols import Bot, Poller
from .tg_poller import RabbitMQPoller


def build_rabbit_poller(
    bot: Bot,
    settings: Settings,
) -> Poller:
    return RabbitMQPoller(
        bot,
        settings.rabbit.url,
        settings.rabbit.queue,
    )
