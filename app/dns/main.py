from __future__ import annotations as _annotations

from os import getpid
from pathlib import Path
from signal import signal, Signals, SIGTERM, SIGINT
from time import sleep

from app.dns.server import DNSServer
from app.config import logger


def handle_sig(signum, frame): # noqa
    logger.info(f'pid={getpid()}, '
                f'got signal: {Signals(signum).name}, '
                f'stopping...')

    raise KeyboardInterrupt


def main(
        port: int,
        upstream: str,
        zones_file: str | Path,
):
    signal(SIGTERM, handle_sig)
    signal(SIGINT, handle_sig)

    server = DNSServer.from_file(
        port=port,
        upstream=upstream,
        zones_file=zones_file,
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
