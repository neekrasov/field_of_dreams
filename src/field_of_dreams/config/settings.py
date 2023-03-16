import os
from dataclasses import dataclass, field


@dataclass(slots=True)
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


@dataclass(slots=True)
class BotSettings:
    token: str = field(init=False)
    timeout: int = field(init=False)
    players_waiting_time: int = field(init=False, default=20)
    max_turn_time: int = field(init=False, default=15)
    question_read_time: int = field(init=False, default=15)
    random_score_from: int = field(init=False, default=5)
    random_score_to: int = field(init=False, default=20)
    word_score_to: int = field(init=False, default=40)

    def __post_init__(self):
        self._read_env()

    def _read_env(self):
        self.token = os.getenv("BOT_TOKEN")
        self.timeout = int(os.getenv("BOT_TIMEOUT"))
        self.max_turn_time = int(os.getenv("BOT_MAX_TURN_TIME"))
        self.question_read_time = int(os.getenv("BOT_QUESTION_READ_TIME"))
        self.players_waiting_time = int(os.getenv("BOT_PLAYERS_WAITING_TIME"))
        self.random_score_from = int(os.getenv("BOT_RANDOM_SCORE_FROM"))
        self.random_score_to = int(os.getenv("BOT_RANDOM_SCORE_TO"))
        self.word_score_to = int(os.getenv("BOT_WORD_SCORE_TO"))


@dataclass(slots=True)
class AdminSettings:
    email: str = field(init=False)
    password: str = field(init=False)

    def __post_init__(self):
        self._read_env()

    def _read_env(self):
        self.email = os.getenv("ADMIN_EMAIL")
        self.password = os.getenv("ADMIN_PASSWORD")


@dataclass(slots=True)
class RabbitMQSettings:
    username: str = field(init=False)
    password: str = field(init=False)
    host: str = field(init=False)
    port: int = field(init=False)
    queue: str = field(init=False)
    url: str = field(init=False)

    def __post_init__(self):
        self._read_env()

    def _read_env(self):
        self.username = os.getenv("RABBIT_USERNAME")
        self.password = os.getenv("RABBIT_PASSWORD")
        self.host = os.getenv("RABBIT_HOST")
        self.port = os.getenv("RABBIT_PORT")
        self.queue = os.getenv("RABBIT_QUEUE")
        self.url = "amqp://{username}:{password}@{host}:{port}/".format(
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
        )


@dataclass(slots=True)
class APISettings:
    admin: AdminSettings = field(init=False, default_factory=AdminSettings)
    session_key: str = field(init=False)
    host: str = field(init=False)
    port: int = field(init=False)
    salt: str = field(init=False)

    def __post_init__(self):
        self._read_env()

    def _read_env(self):
        self.session_key = os.getenv("API_SESSION_KEY")
        self.host = os.getenv("API_HOST")
        self.port = os.getenv("API_PORT")
        self.salt = os.getenv("API_SALT")


@dataclass(slots=True)
class RedisSettings:
    host: str = field(init=False)
    port: int = field(init=False)
    chat_prefix: str = field(init=False)

    def __post_init__(self):
        self._read_env()

    def _read_env(self):
        self.host = os.getenv("REDIS_HOST")
        self.port = os.getenv("REDIS_PORT")
        self.chat_prefix = os.getenv("REDIS_CHAT_PREFIX")


@dataclass(slots=True)
class Settings:
    postgres: PGSettings = field(init=False, default_factory=PGSettings)
    bot: BotSettings = field(init=False, default_factory=BotSettings)
    api: APISettings = field(init=False, default_factory=APISettings)
    redis: RedisSettings = field(init=False, default_factory=RedisSettings)
    rabbit: RabbitMQSettings = field(
        init=False, default_factory=RabbitMQSettings
    )
    logging_config_path: str = field(init=False)

    def __post_init__(self):
        self._read_env()

    def _read_env(self):
        self.logging_config_path = os.getenv("LOGGING_CONFIG_PATH")
