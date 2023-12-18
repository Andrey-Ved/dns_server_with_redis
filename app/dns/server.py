from __future__ import annotations as _annotations

from pathlib import Path
from typing import List
from dnslib.server import DNSServer as LibDNSServer

from app.cache.redis_DAO import RedisCache
from app.dns.load_records import Records, Zone, load_records
from app.logger import logger
from app.dns.resolver import ProxyResolver


class DNSServer:
    def __init__(
        self,
        port: int,
        upstream: str,
        cache: dict | RedisCache,
        records: Records | None = None,
    ):
        self.port: int = port
        self.upstream: str = upstream
        self.cache: dict | RedisCache = cache

        self.udp_server: LibDNSServer | None = None
        self.tcp_server: LibDNSServer | None = None

        self.records: Records = records if records else Records(zones=[])

    @classmethod
    def from_file(
            cls,
            port: int,
            upstream: str,
            cache: dict | RedisCache,
            zones_file: str | Path,
    ) -> 'DNSServer':
        records = load_records(zones_file)

        logger.info(f'loaded {len(records.zones)} zone record from {zones_file}')
        logger.info(f'proxy upstream configured on {upstream}')

        return DNSServer(
            port=port,
            upstream=upstream,
            cache=cache,
            records=records,
        )

    def start(self):
        logger.info(f'starting DNS server on port {self.port}, '
                    f'upstream DNS server {self.upstream}')

        resolver = ProxyResolver(
            records=self.records,
            upstream=self.upstream,
            cache=self.cache)

        self.udp_server = LibDNSServer(
            resolver,
            port=self.port,
        )
        self.tcp_server = LibDNSServer(
            resolver,
            port=self.port,
            tcp=True,
        )
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
