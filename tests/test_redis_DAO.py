from pickle import loads, dumps

import pytest

from app.cache.redis_DAO import RedisCache
from app.config import settings


redis_cache = RedisCache(
    expiration_time=settings.dns.cache_expiration_time_s,
    prefix=settings.redis.prefix,
    encryption_secret=settings.redis.secret,
    redis_connection_kwargs=settings.redis.connection_kwargs,
)


TEST_DATA = [
    '3719871 633bf0d d56  618763d7789ed',
    '3061645e9c7347c6  64372bc16440c8ca1',
]

TEST_KEY = 'test_dgh4561['


@pytest.mark.redis
def test_redis_dao():
    if TEST_KEY in redis_cache:
        del redis_cache[TEST_KEY]

    redis_cache[TEST_KEY] = dumps(TEST_DATA[0])
    assert loads(redis_cache[TEST_KEY]) == TEST_DATA[0]

    assert TEST_KEY in redis_cache

    redis_cache[TEST_KEY] = dumps(TEST_DATA[1])
    assert loads(redis_cache[TEST_KEY]) == TEST_DATA[1]

    del redis_cache[TEST_KEY]

    assert TEST_KEY not in redis_cache
