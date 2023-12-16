import logging

from cryptography.fernet import Fernet  # noqa
from dynaconf import Dynaconf
from os import path as os_path
from pathlib import Path


handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(
    logging.Formatter('%(asctime)s: %(message)s', datefmt='%H:%M:%S')  # noqa
)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


ROOT_PATH = os_path.dirname(
    os_path.dirname(
        os_path.abspath(__file__)
    )
)


def add_path(file_name: str | Path) -> str:

    fail_with_path = ROOT_PATH + os_path.sep + file_name

    if os_path.exists(fail_with_path):
        return fail_with_path

    fail_with_path = ROOT_PATH + os_path.sep + 'app' + os_path.sep + file_name

    if os_path.exists(fail_with_path):
        return fail_with_path

    raise FileNotFoundError(f'File {file_name} not found')


config_file = add_path("config.json")

settings = Dynaconf(
    settings_files=[config_file, ],
    load_dotenv=True,
    envvar_prefix=False,
)

settings.dns.zones_file = add_path(settings.dns.zones_file)
settings.dns.cache_expiration_time_s = settings.dns.cache_expiration_time_m * 60

settings.redis_connection_kwargs = {
    "host": settings.redis.host,
    "port": settings.redis.port,
    "db": settings.redis.db,
    "password": settings.redis_password,
}
