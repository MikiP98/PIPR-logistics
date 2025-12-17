import dataclasses
import sys
from dataclasses import dataclass
from pathlib import Path

import toml
from platformdirs import user_config_dir

from logistics.database.setup import try_setup_new_database
from logistics.io_utils import ask_for_bool, ask_for_string, warn
from logistics.pipeline_loops.manager import start_pipeline_loops


@dataclass(frozen=True, slots=True)
class Config:
    database_location: str
    database_name: str

    @property
    def database_path(self):
        return Path(self.database_location, self.database_name)


def save_config(config: Config, config_path: Path):
    with config_path.open("w") as f:
        f.write(toml.dumps(dataclasses.asdict(config)))


def get_config(config_dir, config_file) -> Config | None:
    if not config_file.exists():
        create_config = ask_for_bool("No config file has been found, do you want to setup a new one now?")
        if create_config:
            database_location = ask_for_string(
                "Provide the path database should be in.\n"
                "Leave empty for current directory\n"
                "Provide '%config%' for config file location"
            )
            if len(database_location) == 0:
                database_location = "./"
            else:
                database_location = database_location.replace("%config%", str(config_dir))

            database_filename = ask_for_string(
                "Provide the database name.\n"
                "Leave empty for current directory\n"
                "Provide '%config%' for config file location"
            )
            if len(database_filename) == 0:
                database_filename = "humble_logistics.sqlite"

            config = Config(database_location=database_location, database_name=database_filename)

            config_dir.mkdir(parents=True, exist_ok=True)
            save_config(config, config_file)
        else:
            return None
    else:
        with config_file.open() as f:
            config = Config(**toml.load(f))
    return config


def check_for_database(config: Config, config_path: Path) -> bool:
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
                with config_path.open("w") as f:
                    f.write(toml.dumps(dataclasses.asdict(config)))
        else:
            warn("No database to connect to, existing")
            return False
    return True


def main() -> int:
    config_dir = Path(user_config_dir(appname="logistics", appauthor="pipr", roaming=True))
    config_file = config_dir / "config.toml"

    config = get_config(config_dir, config_file)
    if config is None:
        warn("No config file exists, exiting")
        return 1

    if not check_for_database(config, config_file):
        return 1

    # Start the pipeline loops
    start_pipeline_loops(config.database_path)

    return 0


if __name__ == '__main__':
    sys.exit(main())
