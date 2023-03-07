from dataclasses import dataclass
from di import Container, bind_by_type
from di.dependent import Dependent
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
)

from field_of_dreams.core.common import UnitOfWork, Mediator
from field_of_dreams.core.protocols.gateways import (
    ChatGateway,
    GameGateway,
    UserGateway,
    WordGateway,
    PlayerGateway,
)
from field_of_dreams.infrastructure.sqlalchemy.gateways import (
    ChatGatewayImpl,
    GameGatewayImpl,
    PlayerGatewayImpl,
    UserGatewayImpl,
    WordGatewayImpl,
)
from field_of_dreams.infrastructure.sqlalchemy.uow import (
    UnitOfWorkImpl,
)
from field_of_dreams.infrastructure.sqlalchemy.factories import (
    build_sa_session_factory,
    build_sa_session,
    build_sa_engine,
)
from field_of_dreams.config import Settings
from ..mediator import build_mediator


@dataclass
class DIScope:
    APP = "app"
    REQUEST = "request"


def build_container() -> Container:
    container = Container()
    container.bind(
        bind_by_type(
            Dependent(lambda *args: Settings(), scope=DIScope.APP), Settings
        )
    )
    build_sa(container)
    build_gateways(container)
    container.bind(
        bind_by_type(
            Dependent(build_mediator, scope=DIScope.REQUEST), Mediator
        )
    )
    return container


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
