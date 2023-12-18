from dnslib import QTYPE
from dnslib.proxy import ProxyResolver as LibProxyResolver
from functools import wraps
from pickle import loads, dumps

from app.cache.redis_DAO import RedisCache
from app.dns.load_records import Records
from app.dns.record import Record
from app.logger import logger


def resolve(request, handler, records):  # noqa
    records = [Record(zone) for zone in records.zones]
    type_name = QTYPE[request.q.qtype]
    reply = request.reply()

    for record in records:
        if record.match(request.q):
            reply.add_answer(record.rr)

    if reply.rr:
        logger.info(f'found zone for {request.q.qname} [type_name],'
                    f' {len(reply.rr)} replies')

        return reply

    # no direct zone so look for an SOA record for a higher level zone
    for record in records:
        if record.sub_match(request.q):
            reply.add_answer(record.rr)

    if reply.rr:
        logger.info(f'found higher level SOA resource for '
                    f'{request.q.qname} [{type_name}]')

        return reply


class ProxyResolver(LibProxyResolver):
    def __init__(
            self,
            records: Records,
            upstream: str,
            cache: dict | RedisCache,
    ):
        self.records = records
        self.cache = cache
        super().__init__(address=upstream, port=53, timeout=5)

    @staticmethod
    def cache_for_resolve(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]

            request = kwargs['request'] if 'request' in kwargs else args[1]
            key = repr(request)

            if key in self.cache:
                logger.info(f'request found in cache, {request.q.qname}')
                result = loads(self.cache[key])

                return result

            result = func(*args, **kwargs)
            self.cache[key] = dumps(result)

            return result

        return wrapper

    @cache_for_resolve
    def resolve(self, request, handler):  # noqa
        answer = resolve(request, handler, self.records)

        if answer:
            logger.info(f'local zone found, '
                        f'{request.q.qname}')

            return answer

        type_name = QTYPE[request.q.qtype]

        logger.info(f'no local zone found, '
                    f'proxying {request.q.qname}[{type_name}]')

        return super().resolve(request, handler)
