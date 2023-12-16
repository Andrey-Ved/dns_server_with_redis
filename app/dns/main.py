from __future__ import annotations as _annotations

import os
import signal
from time import sleep

from app.dns.server import DNSServer
from app.config import logger, settings


def handle_sig(signum, frame): # noqa
    logger.info(f'pid={os.getpid()}, '
                f'got signal: {signal.Signals(signum).name}, '
                f'stopping...')

    raise KeyboardInterrupt


def main():
    signal.signal(signal.SIGTERM, handle_sig)
    signal.signal(signal.SIGINT, handle_sig)

    server = DNSServer.from_file(
        port=settings.dns.port,
        upstream=settings.dns.upstream,
        zones_file=settings.dns.zones_file,
    )
    server.start()

    try:
        while server.is_running:
            sleep(0.1)

    except KeyboardInterrupt:
        pass

    finally:
        logger.info('stopping DNS server')
        server.stop()
