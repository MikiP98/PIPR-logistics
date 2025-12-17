# coding=utf-8
import os
from pathlib import Path

from logistics.io_utils import ask_for_bool, warn
from logistics.database.setup import try_setup_new_database
from logistics.pipeline_loops.manager import start_pipeline_loops


def main() -> None:
    # Check if config exists, if not, create it
    # Read config and check for database, if it does not exist, create it

    # TODO: Consider moving config and database checks to separate functions

    config_location = "./"
    # TODO: Change the config location to the correct Windows and Linux path
    config_filename = "config.toml"

    if not os.path.exists(config_location + config_filename):
        # create_config = ask_for_bool("No config file has been found, do you want to setup a new one now?")
        # TODO
        ...

    # TODO: Read the config from the database
    database_location = "./"
    database_filename = "humble_logistics.sqlite"

    if not os.path.exists(database_location + database_filename):
        create_db = ask_for_bool("No database has been found, do you want to setup a new one now?")
        if create_db:
            try_setup_new_database(database_location, database_filename)
            # TODO: Return db_path and db_filename back from the setup function
            #  in case the location changed and config file has to be updated
            # TODO: Handle config setup returning False
        else:
            warn("No database to connect to, existing")
            return

    # Start the pipeline loops
    start_pipeline_loops(Path(database_location) / database_filename)


if __name__ == '__main__':
    main()
