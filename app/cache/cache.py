from functools import wraps
from pickle import loads, dumps

from app.cache.redis_DAO import RedisCache
from app.config import logger, settings


_cache = RedisCache(
    expiration_time=settings.dns.cache_expiration_time_s,
    prefix=settings.redis.prefix,
    encryption_secret=settings.redis.secret,
    redis_connection_kwargs=settings.redis.connection_kwargs,
)


def cache_for_resolve(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global _cache

        request = kwargs['request'] if 'request' in kwargs else args[1]
        key = repr(request)

        if key in _cache:
            logger.info(f'request found in cache, {request.q.qname}')
            result = loads(_cache[key])

            return result

        result = func(*args, **kwargs)
        _cache[key] = dumps(result)

        return result

    return wrapper
