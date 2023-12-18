from cryptography.fernet import Fernet  # noqa
from os import getpid
from redis import Redis, ConnectionPool
from typing import TypedDict

from app.logger import logger


class RedisConnectionKwargs(TypedDict):
    host: str
    port: int
    db: int
    password: str


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]


class RedisClient(metaclass=Singleton):
    def __init__(
            self,
            redis_connection_kwargs: RedisConnectionKwargs,
    ):
        self.redis_connection_kwargs = redis_connection_kwargs

        self._pool = ConnectionPool(
            **self.redis_connection_kwargs
        )

        logger.info(f'PID {getpid()}: initializing redis pool')

    @property
    def conn(self):
        if not hasattr(self, '_conn'):
            self._get_connection()
        return self._conn

    def _get_connection(self):
        self._conn = Redis(connection_pool=self._pool)
