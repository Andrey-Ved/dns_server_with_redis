import logging

from cryptography.fernet import Fernet  # noqa
from dynaconf import Dynaconf
from os import path as os_path
from pathlib import Path


CONFIG_FILE = 'config.json'
DOTENV_FILE = '.env'
CONFIGS_DIR = 'configs'


def add_path(
        path: str | Path,
        file_name: str | Path
) -> str:
    root_path = os_path.dirname(
        os_path.dirname(
            os_path.abspath(__file__)
        )
    )
    return root_path + os_path.sep + path + os_path.sep + file_name


def settings_init(
        config_file: str | Path,
        dotenv_file: str | Path,
        configs_dir: str | Path,
):
    dynaconf = Dynaconf(
        settings_files=[add_path(configs_dir, config_file), ],
        load_dotenv=True,
        envvar_prefix=False,
        dotenv_path=add_path(configs_dir, dotenv_file)
    )

    dynaconf.dns.zones_file = add_path(configs_dir, dynaconf.dns.zones_file)
    dynaconf.dns.cache_expiration_time_s = dynaconf.dns.cache_expiration_time_m * 60

    dynaconf.redis.secret = dynaconf.redis_secret
    dynaconf.redis.connection_kwargs = {
        "host": dynaconf.redis.host,
        "port": dynaconf.redis.port,
        "db": dynaconf.redis.db,
        "password": dynaconf.redis_password,
    }

    return dynaconf


settings = settings_init(
    config_file=CONFIG_FILE,
    dotenv_file=DOTENV_FILE,
    configs_dir=CONFIGS_DIR,
)


handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(
    logging.Formatter('%(asctime)s: %(message)s', datefmt='%H:%M:%S')  # noqa
)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
