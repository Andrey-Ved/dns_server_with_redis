import pytest

from dirty_equals import IsIP, IsPositive
from dns.resolver import NXDOMAIN
from typing import Any, Callable, Dict, List

from app.dns.load_records import Zone
from app.dns.server import DNSServer


Resolver = Callable[[str, str], List[Dict[str, Any]]]


def test_a_record(dns_resolver: Resolver):
    assert dns_resolver('example.com', 'A') == [
        {
            'type': 'A',
            'value': '1.2.3.4',
        },
    ]


def test_cname_record(dns_resolver: Resolver):
    assert dns_resolver('example.com', 'CNAME') == [
        {
            'type': 'CNAME',
            'value': 'whatever.com.',
        },
    ]


def test_mx_record(dns_resolver: Resolver):
    assert dns_resolver('example.com', 'MX') == [
        {
            'type': 'MX',
            'preference': 5,
            'value': 'whatever.com.',
        },
        {
            'type': 'MX',
            'preference': 10,
            'value': 'mx2.whatever.com.',
        },
        {
            'type': 'MX',
            'preference': 20,
            'value': 'mx3.whatever.com.',
        },
    ]


def test_proxy(dns_resolver: Resolver):
    assert dns_resolver('example.org', 'A') == [
        {
            'type': 'A',
            'value': IsIP(version=4),
        },
    ]


def test_soa(dns_resolver: Resolver):
    assert dns_resolver('example.com', 'SOA') == [
        {
            'type': 'SOA',
            'rname': 'dns.example.com.',
            'mname': 'ns1.example.com.',  # noqa
            'serial': IsPositive(),
            'refresh': 3600,
            'retry': 10800,
            'expire': 86400,
            'minimum': 3600,
        }
    ]


def test_dynamic_zone_update(dns_server: DNSServer, dns_resolver: Resolver):
    assert dns_resolver('example.com', 'A') == [
        {
            'type': 'A',
            'value': '1.2.3.4',
        },
    ]
    with pytest.raises(NXDOMAIN):
        dns_resolver('another-example.org', 'A')

    dns_server.add_record(Zone(host='another-example.com', type='A', answer='2.3.4.5'))

    assert dns_resolver('example.com', 'A') == [
        {
            'type': 'A',
            'value': '1.2.3.4',
        },
    ]
    assert dns_resolver('another-example.com', 'A') == [
        {
            'type': 'A',
            'value': '2.3.4.5',
        },
    ]

    dns_server.set_records([Zone(host='example.com', type='A', answer='4.5.6.7')])

    assert dns_resolver('example.com', 'A') == [
        {
            'type': 'A',
            'value': '4.5.6.7',
        },
    ]
    with pytest.raises(NXDOMAIN):
        dns_resolver('another-example.org', 'A')
