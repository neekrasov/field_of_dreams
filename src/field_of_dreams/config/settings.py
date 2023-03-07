import os
from dataclasses import dataclass, field


@dataclass
class PGSettings:
    user: str = field(init=False)
    password: str = field(init=False)
    host: str = field(init=False)
    db: str = field(init=False)
    port: str = field(init=False)
    url: str = field(init=False)

    def __post_init__(self):
        self._read_env()

    def _read_env(self):
        self.user = os.getenv("POSTGRES_USER")
        self.password = os.getenv("POSTGRES_PASSWORD")
        self.host = os.getenv("POSTGRES_HOST")
        self.db = os.getenv("POSTGRES_DB")
        self.port = os.getenv("POSTGRES_PORT")
        self.url = (
            "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}".format(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                db=self.db,
            )
        )


@dataclass
class BotSettings:
    token: str = field(init=False)
    timeout: int = field(init=False)
    players_waiting_time: int = field(init=False, default=20)
    max_turn_time: int = field(init=False, default=15)

    def __post_init__(self):
        self._read_env()

    def _read_env(self):
        self.token = os.getenv("BOT_TOKEN")
        self.timeout = os.getenv("BOT_TIMEOUT")


@dataclass
class AdminSettings:
    email: str = field(init=False)
    password: str = field(init=False)

    def __post_init__(self):
        self._read_env()

    def _read_env(self):
        self.email = os.getenv("ADMIN_EMAIL")
        self.password = os.getenv("ADMIN_PASSWORD")


@dataclass
class Settings:
    session_key: str = field(init=False)

    postgres: PGSettings = field(init=False, default_factory=PGSettings)
    bot: BotSettings = field(init=False, default_factory=BotSettings)
    admin: AdminSettings = field(init=False, default_factory=AdminSettings)

    def __post_init__(self):
        self._read_env()

    def _read_env(self):
        self.session_key = os.getenv("SESSION_KEY")
