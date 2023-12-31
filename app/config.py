from cryptography.fernet import Fernet  # noqa
from dynaconf import Dynaconf
from os.path import dirname, sep, abspath
from pathlib import Path


CONFIG_FILE = 'config.json'
DOTENV_FILE = '.env'
CONFIGS_DIR = 'configs'


def add_path(
        file_name: str | Path,
        additional_path: str | Path | None = None,
) -> str:
    root_path = dirname(
        dirname(
            abspath(__file__)
        )
    )
    if additional_path:
        return root_path + sep + additional_path + sep + file_name

    return root_path + sep + file_name


def settings_init(
        config_file: str | Path,
        dotenv_file: str | Path,
        configs_dir: str | Path,
):
    dynaconf = Dynaconf(
        settings_files=[add_path(config_file, configs_dir), ],
        load_dotenv=True,
        envvar_prefix=False,
        dotenv_path=add_path(dotenv_file, configs_dir)
    )

    dynaconf.dns.zones_file = add_path(dynaconf.dns.zones_file, configs_dir)
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
