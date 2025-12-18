import sys

from config import check_for_database, get_config

from logistics.io_utils import warn
from logistics.pipeline_loops.manager import start_pipeline_loops


def main() -> int:
    config = get_config()
    if config is None:
        warn("No config file exists, exiting")
        return 1

    if not check_for_database(config):
        return 1

    # Start the pipeline loops
    start_pipeline_loops(config.database_path)

    return 0


if __name__ == '__main__':
    sys.exit(main())
