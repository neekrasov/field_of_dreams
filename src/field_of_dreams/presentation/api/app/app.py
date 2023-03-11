import logging.config
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp.web import (
    Application,
    _run_app,
)
from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from field_of_dreams.infrastructure.di import build_container, DIScope
from field_of_dreams.config import Settings
from .middlewares import setup_middlewares
from routes import setup_routes


async def main():
    settings = Settings()
    logging.config.fileConfig(settings.logging_config_path.strip())
    app = Application()
    container = build_container()
    setup_aiohttp_apispec(
        app, title="Puzzle Wheel", url="/docs/json", swagger_path="/docs"
    )
    session_setup(app, EncryptedCookieStorage(settings.api.session_key))
    async with container.enter_scope(DIScope.APP) as app_state:
        setup_middlewares(app, container, app_state)
        setup_routes(app.router)
        await _run_app(app, host=settings.api.host, port=settings.api.port)
