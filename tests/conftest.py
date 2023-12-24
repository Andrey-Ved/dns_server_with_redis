import pytest

from dns.resolver import Resolver as RawResolver
from typing import Any, Dict, List

from app.config import add_path
from app.dns.server import DNSServer


def convert_answer(answer) -> Dict[str, Any]:
    rd_type = answer.rdtype.name
    d = {'type': rd_type}
    if rd_type == 'MX':
        d.update(
            preference=answer.preference,
            value=answer.exchange.to_text(),
        )
    elif rd_type == 'SOA':
        d.update(
            rname=str(answer.rname.choose_relativity()),
            mname=str(answer.mname.choose_relativity()),
            serial=answer.serial,
            refresh=answer.refresh,
            retry=answer.retry,
            expire=answer.expire,
            minimum=answer.minimum,
        )
    else:
        d['value'] = answer.to_text()
    return d


@pytest.fixture(scope="session")
def zones_file():
    return add_path('test_zones.json', 'tests')


@pytest.fixture(scope='session')
def dns_server(zones_file):
    port = 5053
    upstream = '8.8.8.8'
    cache = {}

    server = DNSServer.from_file(
        port=port,
        upstream=upstream,
        cache=cache,
        zones_file=zones_file,
    )
    server.start()
    assert server.is_running
    yield server
    server.stop()


@pytest.fixture(scope='session')
def dns_resolver(dns_server: DNSServer):
    resolver = RawResolver()
    resolver.nameservers = ['127.0.0.1']
    resolver.port = dns_server.port

    def resolve(name: str, type_: str) -> List[Dict[str, Any]]:
        answers = resolver.resolve(name, type_)
        return [convert_answer(answer) for answer in answers]

    yield resolve
