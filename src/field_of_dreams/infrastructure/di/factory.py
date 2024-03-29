import inspect
import aiohttp
from typing import Optional, Any
from aiohttp.web import Request
from redis.asyncio import Redis
from di.api.dependencies import DependentBase
from di.dependent import Dependent
from di import Container, bind_by_type
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
)
from field_of_dreams.infrastructure.tgbot.protocols import Bot, Poller, Storage
from field_of_dreams.presentation.tgbot.views.game import (
    GameView,
    GameViewImpl,
)
from field_of_dreams.infrastructure.tgbot.factory import (
    build_telegram_bot,
    build_client_session,
)
from field_of_dreams.infrastructure.redis.factory import build_redis
from field_of_dreams.presentation.tgbot.states.factory import (
    build_redis_storage,
)
from field_of_dreams.core.common import UnitOfWork, Mediator
from field_of_dreams.core.services.hasher import PasswordHasher
from field_of_dreams.core.protocols.gateways import (
    ChatGateway,
    GameGateway,
    UserGateway,
    WordGateway,
    PlayerGateway,
    UserStatsGateway,
    AdminGateway,
)
from field_of_dreams.infrastructure.sqlalchemy.gateways import (
    ChatGatewayImpl,
    GameGatewayImpl,
    PlayerGatewayImpl,
    UserGatewayImpl,
    WordGatewayImpl,
    UserStatsGatewayImpl,
    AdminGatewayImpl,
)
from field_of_dreams.infrastructure.sqlalchemy.uow import UnitOfWorkImpl
from field_of_dreams.infrastructure.sqlalchemy.factories import (
    build_sa_session_factory,
    build_sa_session,
    build_sa_engine,
)
from field_of_dreams.infrastructure.rabbitmq.factory import build_rabbit_poller
from field_of_dreams.config import Settings
from ..mediator import build_mediator
from .container import DIContainer, DIScope


def build_container() -> DIContainer:
    container = Container()
    container.bind(match_request)
    container.bind(
        bind_by_type(
            Dependent(lambda *args: Settings(), scope=DIScope.APP), Settings
        )
    )
    container.bind(
        bind_by_type(
            Dependent(build_password_hasher, scope=DIScope.APP), PasswordHasher
        )
    )
    container.bind(
        bind_by_type(Dependent(build_redis, scope=DIScope.APP), Redis)
    )
    build_sa(container)
    build_gateways(container)
    build_tg(container)
    container.bind(
        bind_by_type(
            Dependent(build_mediator, scope=DIScope.REQUEST), Mediator
        )
    )
    return DIContainer(container, (DIScope.APP, DIScope.REQUEST))


def build_gateways(container: Container) -> None:
    container.bind(
        bind_by_type(
            Dependent(ChatGatewayImpl, scope=DIScope.REQUEST), ChatGateway
        )
    )
    container.bind(
        bind_by_type(
            Dependent(GameGatewayImpl, scope=DIScope.REQUEST), GameGateway
        )
    )
    container.bind(
        bind_by_type(
            Dependent(PlayerGatewayImpl, scope=DIScope.REQUEST), PlayerGateway
        )
    )
    container.bind(
        bind_by_type(
            Dependent(UserGatewayImpl, scope=DIScope.REQUEST), UserGateway
        )
    )
    container.bind(
        bind_by_type(
            Dependent(WordGatewayImpl, scope=DIScope.REQUEST), WordGateway
        )
    )
    container.bind(
        bind_by_type(
            Dependent(UnitOfWorkImpl, scope=DIScope.REQUEST), UnitOfWork
        )
    )
    container.bind(
        bind_by_type(
            Dependent(UserStatsGatewayImpl, scope=DIScope.REQUEST),
            UserStatsGateway,
        )
    )
    container.bind(
        bind_by_type(
            Dependent(AdminGatewayImpl, scope=DIScope.REQUEST),
            AdminGateway,
        )
    )


def build_sa(container: Container) -> None:
    container.bind(
        bind_by_type(
            Dependent(build_sa_engine, scope=DIScope.APP), AsyncEngine
        )
    )
    container.bind(
        bind_by_type(
            Dependent(build_sa_session_factory, scope=DIScope.APP),
            async_sessionmaker[AsyncSession],
        )
    )
    container.bind(
        bind_by_type(
            Dependent(build_sa_session, scope=DIScope.REQUEST), AsyncSession
        )
    )


def build_tg(container: Container):
    container.bind(
        bind_by_type(
            Dependent(build_client_session, scope=DIScope.APP),
            aiohttp.ClientSession,
        )
    )
    container.bind(
        bind_by_type(
            Dependent(build_telegram_bot, scope=DIScope.APP),
            Bot,
        )
    )
    container.bind(
        bind_by_type(
            Dependent(build_rabbit_poller, scope=DIScope.APP),
            Poller,
        )
    )
    container.bind(
        bind_by_type(
            Dependent(GameViewImpl, scope=DIScope.APP),
            GameView,
        ),
    )
    container.bind(
        bind_by_type(
            Dependent(build_redis_storage, scope=DIScope.APP),
            Storage,
        ),
    )


# Fix params for aiohttp-apispec for view no types
def match_request(
    param: Optional[inspect.Parameter],
    dependent: DependentBase[Any],
) -> Optional[DependentBase[Any]]:
    if param is not None and param.name in ("_", "request"):
        return Dependent(Request, scope=DIScope.REQUEST)
    return None


def build_password_hasher(settings: Settings) -> PasswordHasher:
    return PasswordHasher(settings.api.salt)
