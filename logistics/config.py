import dataclasses
from dataclasses import dataclass
from pathlib import Path

import toml
from platformdirs import user_config_dir

from logistics.database.setup import try_setup_new_database
from logistics.io_utils import ask_for_bool, ask_for_string, warn

_config_path: Path = Path(user_config_dir(appname="logistics", appauthor="pipr", roaming=True)) / "config.toml"


@dataclass(slots=True)
class Config:
    database_location: str = "./"
    database_name: str = "humble_logistics.sqlite"

    @property
    def database_path(self) -> Path:
        return Path(self.database_location, self.database_name)

    def save(self) -> None:
        with _config_path.open("w") as f:
            f.write(toml.dumps(dataclasses.asdict(self)))


def read() -> Config:
    with _config_path.open() as f:
        return Config(**toml.load(f))


def get_config() -> Config | None:
    if not _config_path.exists():
        create_config = ask_for_bool("No config file has been found, do you want to setup a new one now?")
        if create_config:
            config = Config()

            database_location = ask_for_string(
                "Provide the path database should be in.\n"
                "Leave empty for current directory\n"
                "Provide '%config%' for config file location"
            ).strip()
            if len(database_location) != 0:
                config.database_location = parse_config_path(database_location)

            database_filename = ask_for_string(
                "Provide the database name.\n"
                "Leave empty for current directory\n"
                "Provide '%config%' for config file location"
            ).strip()
            if len(database_filename) != 0:
                config.database_filename = parse_config_path(database_filename)

            _config_path.mkdir(parents=True, exist_ok=True)
            config.save()
            return config
        else:
            return None
    return read()


def parse_config_path(path: str) -> str:
    return path.replace("%config%", str(_config_path.parent))


def check_for_database(config: Config) -> bool:
    if not config.database_path.exists():
        create_db = ask_for_bool("No database has been found, do you want to setup a new one now?")
        if create_db:
            success, (database_location, database_filename) = try_setup_new_database(
                config.database_location, config.database_name
            )
            if not success:
                warn("Database could not be created, exiting")
                return False
            if config.database_location != database_location or config.database_name != database_filename:
                config = Config(database_location=database_location, database_name=database_filename)
                config.save()
        else:
            warn("No database to connect to, existing")
            return False
    return True
