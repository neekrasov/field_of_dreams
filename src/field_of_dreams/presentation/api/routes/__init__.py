from aiohttp.web import UrlDispatcher
from .admin import admin_router
from .word import word_router


def setup_routes(router: UrlDispatcher) -> None:
    router.add_routes(admin_router)
    router.add_routes(word_router)
