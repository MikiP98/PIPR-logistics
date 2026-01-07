from logistics.database.database import Database
from logistics.pipeline_loops.virtual_clock import VirtualClock


def change_config_task(_: Database, __: VirtualClock) -> None:
    raise NotImplementedError
