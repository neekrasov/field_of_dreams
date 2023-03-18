import enum
from typing import Sequence, Optional, Any
from di.executors import AsyncExecutor
from di.api.scopes import Scope
from di import Container, ScopeState
from di.dependent import Dependent
from di._container import DependencyType
from di.api.providers import DependencyProvider, DependencyProviderType


class DIContainer:
    def __init__(self, container: Container, scopes: Sequence[Scope]):
        self._container = container
        self._executor = AsyncExecutor()
        self._cache = {}  # type: ignore
        self._scopes = scopes

    async def execute(
        self,
        handler: DependencyProviderType[DependencyType],
        state: ScopeState,
        scope: Scope,
        values: dict[DependencyProvider, Any] = {},
    ) -> DependencyType:
        handler_from_cache = self._cache.get(handler)
        if handler_from_cache:
            solved = handler_from_cache  # type: ignore
        else:
            solved = self._container.solve(
                Dependent(handler, scope=scope), self._scopes
            )
            self._cache[handler] = solved
        return await solved.execute_async(
            executor=self._executor, state=state, values=values
        )

    def enter_scope(
        self,
        scope: Scope,
        state: Optional[ScopeState] = None,
    ):
        return self._container.enter_scope(scope, state)


class DIScope(enum.Enum):
    APP = "app"
    REQUEST = "request"
