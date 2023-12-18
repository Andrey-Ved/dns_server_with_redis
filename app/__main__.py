"""
This allows usage via `python -m app`
"""
from app.cache.redis_DAO import RedisCache
from app.config import settings
from app.dns.main import main


if __name__ == '__main__':
    redis_cache = RedisCache(
        expiration_time=settings.dns.cache_expiration_time_s,
        prefix=settings.redis.prefix,
        encryption_secret=settings.redis.secret,
        redis_connection_kwargs=settings.redis.connection_kwargs,
    )

    main(
        port=settings.dns.port,
        upstream=settings.dns.upstream,
        cache=redis_cache,
        zones_file=settings.dns.zones_file,
        )
