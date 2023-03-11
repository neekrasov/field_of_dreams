from typing import Callable, Awaitable
from aiohttp.web_response import StreamResponse

Controller = Callable[..., Awaitable[StreamResponse]]
