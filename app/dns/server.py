from __future__ import annotations as _annotations

from pathlib import Path
from typing import List
from dnslib import QTYPE
from dnslib.proxy import ProxyResolver as LibProxyResolver
from dnslib.server import DNSServer as LibDNSServer

from app.config import logger
from app.dns.load_records import Records, Zone, load_records
from app.dns.record import Record
from app.cache.cache import cache_for_resolve


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
    ):
        self.records = records
        super().__init__(address=upstream, port=53, timeout=5)

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


class DNSServer:
    def __init__(
        self,
        port: int,
        upstream: str,
        records: Records | None = None,
    ):
        self.port: int = port
        self.upstream: str = upstream
        self.udp_server: LibDNSServer | None = None
        self.tcp_server: LibDNSServer | None = None
        self.records: Records = records if records else Records(zones=[])

    @classmethod
    def from_file(
            cls,
            port: int,
            upstream: str,
            zones_file: str | Path,
    ) -> 'DNSServer':
        records = load_records(zones_file)

        logger.info(f'loaded {len(records.zones)} zone record from {zones_file}')
        logger.info(f'proxy upstream configured on {upstream}')

        return DNSServer(
            port=port,
            upstream=upstream,
            records=records,
        )

    def start(self):
        logger.info(f'starting DNS server on port {self.port}, '
                    f'upstream DNS server {self.upstream}')
        resolver = ProxyResolver(self.records, self.upstream)

        self.udp_server = LibDNSServer(resolver, port=self.port)
        self.tcp_server = LibDNSServer(resolver, port=self.port, tcp=True)
        self.udp_server.start_thread()
        self.tcp_server.start_thread()

    def stop(self):
        self.udp_server.stop()
        self.udp_server.server.server_close()
        self.tcp_server.stop()
        self.tcp_server.server.server_close()

    @property
    def is_running(self):
        return (
                self.udp_server and self.udp_server.isAlive()
        ) or (
                self.tcp_server and self.tcp_server.isAlive()
        )

    def add_record(self, zone: Zone):
        self.records.zones.append(zone)

    def set_records(self, zones: List[Zone]):
        self.records.zones = zones
