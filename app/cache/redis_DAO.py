from cryptography.fernet import Fernet  # noqa
from functools import wraps

from app.cache.redis_connector import RedisClient, RedisConnectionKwargs
from app.logger import logger


def get_full_class_name(obj) -> str:
    module = obj.__class__.__module__

    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__

    return str(module + '.' + obj.__class__.__name__)


class RedisCache:
    def __init__(self,
                 expiration_time: int,
                 prefix: str,
                 encryption_secret: str,
                 redis_connection_kwargs: RedisConnectionKwargs,
                 ):
        self._expiration_time = expiration_time
        self._prefix = prefix

        self.cipher_suite = Fernet(encryption_secret)
        self.redis_client = RedisClient(redis_connection_kwargs)

    @staticmethod
    def retry(retry_numer: int = 2):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                for _ in range(retry_numer):
                    try:
                        result = func(*args, **kwargs)
                        return result

                    except Exception as err:
                        logger.info(f'error interacting with redis'
                                    f' {get_full_class_name(err)}')

            return wrapper
        return decorator

    @staticmethod
    def prefix_adder(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            new_key = self._prefix + args[1]
            new_args = (args[0], new_key) + args[2:]

            return func(*new_args, **kwargs)
        return wrapper

    @staticmethod
    def encryption(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]

            if not args[2:]:
                result = func(*args, **kwargs)

            else:
                new_args = args[:2] + (self.cipher_suite.encrypt(args[2]), ) + args[3:]
                result = func(*new_args, **kwargs)

            if result:
                return self.cipher_suite.decrypt(result)

        return wrapper

    @encryption
    @prefix_adder
    @retry()
    def __setitem__(
            self,
            key: str,
            value: bytes
    ) -> None:
        self.redis_client.conn.set(key, value, ex=self._expiration_time)

    @encryption
    @prefix_adder
    @retry()
    def __getitem__(
            self,
            key: str,
    ) -> bytes:
        return self.redis_client.conn.get(key)

    @prefix_adder
    @retry()
    def __delitem__(
            self,
            key: str,
    ) -> None:
        if self.redis_client.conn.exists(key):
            self.redis_client.conn.delete(key)

    @prefix_adder
    @retry()
    def __contains__(
            self,
            key: str,
    ) -> bool:
        return self.redis_client.conn.exists(key)
