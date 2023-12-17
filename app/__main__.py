"""
This allows usage via `python -m app`
"""
from app.config import settings
from app.dns.main import main


if __name__ == '__main__':
    main(
        port=settings.dns.port,
        upstream=settings.dns.upstream,
        zones_file=settings.dns.zones_file,
        )
