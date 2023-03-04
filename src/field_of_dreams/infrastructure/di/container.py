from dataclasses import dataclass
from di import Container, bind_by_type
from di.dependent import Dependent
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
)

from field_of_dreams.application.common import UnitOfWork, Mediator
from field_of_dreams.application.protocols.gateways.chat import ChatGateway
from field_of_dreams.application.protocols.gateways.game import GameGateway
from field_of_dreams.application.protocols.gateways.user import UserGateway
from field_of_dreams.application.protocols.gateways.word import WordGateway
from field_of_dreams.application.protocols.gateways.player_turn import (
    PlayerTurnGateway,
)
from field_of_dreams.application.protocols.gateways.player import (
    PlayerGateway,
)
from field_of_dreams.infrastructure.memory.fake_uow import FakeUnitOfWork
from field_of_dreams.infrastructure.memory.fake_gateways.chat import (
    InMemoryChatGateway,
)
from field_of_dreams.infrastructure.memory.fake_gateways.game import (
    InMemoryGameGateway,
)
from field_of_dreams.infrastructure.memory.fake_gateways.player import (
    InMemoryPlayerGateway,
)
from field_of_dreams.infrastructure.memory.fake_gateways.player_turn import (
    InMemoryPlayerTurnGateway,
)
from field_of_dreams.infrastructure.memory.fake_gateways.user import (
    InMemoryUserGateway,
)
from field_of_dreams.infrastructure.memory.fake_gateways.word import (
    InMemoryWordGateway,
)
from field_of_dreams.config import Settings
from field_of_dreams.infrastructure.persistence.sqlalchemy.factories import (
    build_sa_session_factory,
    build_sa_session,
    build_sa_engine,
)
from ..mediator import build_mediator


@dataclass
class DIScope:
    APP = "app"
    REQUEST = "request"


def build_container() -> Container:
    container = Container()
    build_in_memory_gateways(container)
    container.bind(
        bind_by_type(
            Dependent(lambda *args: Settings(), scope=DIScope.APP), Settings
        )
    )
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
    container.bind(
        bind_by_type(
            Dependent(build_mediator, scope=DIScope.REQUEST), Mediator
        )
    )
    return container


def build_in_memory_gateways(container: Container):
    container.bind(
        bind_by_type(
            Dependent(
                lambda *args: InMemoryChatGateway({}),
                scope=DIScope.APP,
            ),
            ChatGateway,
        )
    )
    container.bind(
        bind_by_type(
            Dependent(
                lambda *args: InMemoryGameGateway({}),
                scope=DIScope.APP,
            ),
            GameGateway,
        )
    )
    container.bind(
        bind_by_type(
            Dependent(
                lambda *args: InMemoryUserGateway({}),
                scope=DIScope.APP,
            ),
            UserGateway,
        )
    )
    container.bind(
        bind_by_type(
            Dependent(
                lambda *args: InMemoryPlayerGateway({}),
                scope=DIScope.APP,
            ),
            PlayerGateway,
        )
    )
    container.bind(
        bind_by_type(
            Dependent(
                lambda *args: InMemoryPlayerTurnGateway({}),
                scope=DIScope.APP,
            ),
            PlayerTurnGateway,
        )
    )
    container.bind(
        bind_by_type(
            Dependent(
                lambda *args: InMemoryWordGateway({}),
                scope=DIScope.APP,
            ),
            WordGateway,
        )
    )
    container.bind(
        bind_by_type(
            Dependent(
                FakeUnitOfWork,
                scope=DIScope.APP,
            ),
            UnitOfWork,
        )
    )
