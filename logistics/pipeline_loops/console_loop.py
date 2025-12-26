from collections.abc import Callable
from enum import Enum, auto
from pathlib import Path
from typing import Any

from logistics.database.database import Database
from logistics.io_utils import (
    ask_for_choice,
    get_input,
    log,
)
from logistics.pipeline_loops.console_tasks.data_manipulation_tasks import (
    add_product_task,
    add_warehouses_task,
)
from logistics.pipeline_loops.console_tasks.data_retrival_tasks import (
    show_products_task,
    show_warehouse_details,
    show_warehouses_task,
)
from logistics.pipeline_loops.console_tasks.debug_and_simulation_tasks import (
    change_time_simulation_scale_task,
    offset_simulation_time_task,
)
from logistics.pipeline_loops.virtual_clock import VirtualClock


class TaskEnum(Enum):
    pass


class DataRetrivalTasks(TaskEnum):
    SHOW_WAREHOUSES = auto()
    SHOW_WAREHOUSE_DETAILS = auto()

    SHOW_WAREHOUSE_CONNECTIONS = auto()

    SHOW_ACTIVE_TRANSPORTS = auto()
    SHOW_FINISHED_TRANSPORTS = auto()
    SHOW_ALL_TRANSPORTS = auto()
    SHOW_TRANSPORT_DETAILS = auto()

    SHOW_PRODUCTS = auto()
    SHOW_PRODUCT_DETAILS = auto()


class DataManipulationTasks(TaskEnum):
    ADD_WAREHOUSE = auto()
    ADD_PRODUCT = auto()
    ADD_STOCK = auto()
    ADD_WAREHOUSE_CONNECTION = auto()

    INITIALISE_TRANSPORT = auto()
    CANCEL_TRANSPORT = auto()

    REMOVE_WAREHOUSE = auto()
    REMOVE_PRODUCT = auto()
    REMOVE_STOCK = auto()
    REMOVE_WAREHOUSE_CONNECTION = auto()

    EDIT_WAREHOUSE = auto()
    EDIT_PRODUCT = auto()
    EDIT_WAREHOUSE_CONNECTION = auto()


class DebugTasks(TaskEnum):
    CHANGE_TIME_SIMULATION_SCALE = auto()
    OFFSET_SIMULATION_TIME = auto()


class ConfigTasks(TaskEnum):
    CHANGE_CONFIG = auto()
    DELETE_CONFIG = auto()
    DELETE_DATABASE = auto()


COMMAND_HANDLER_MAP: dict[TaskEnum, Callable[[Database, VirtualClock], Any] | Callable[[VirtualClock], Any]] = {
    # DataRetrivalTasks
    DataRetrivalTasks.SHOW_WAREHOUSES: show_warehouses_task,
    DataRetrivalTasks.SHOW_WAREHOUSE_DETAILS: show_warehouse_details,
    DataRetrivalTasks.SHOW_PRODUCTS: show_products_task,

    # DataManipulationTasks
    DataManipulationTasks.ADD_WAREHOUSE: add_warehouses_task,
    DataManipulationTasks.ADD_PRODUCT: add_product_task,

    # DebugTasks
    DebugTasks.CHANGE_TIME_SIMULATION_SCALE: change_time_simulation_scale_task,
    DebugTasks.OFFSET_SIMULATION_TIME: offset_simulation_time_task,
}


def run_console_loop(db_path: Path, clock: VirtualClock) -> None:
    database = Database(db_path)
    user_choices: list[list[str]] = [
        ["data_retrival_tasks", *parse_options(DataRetrivalTasks)],
        ["data_manipulation_tasks", *parse_options(DataManipulationTasks)],
        ["debug, configuration & exit", *parse_options(DebugTasks), None, *parse_options(ConfigTasks), None, "Exit"]
    ]
    enum_indexer: list[TaskEnum] = (
        list(DataRetrivalTasks) +
        list(DataManipulationTasks) +
        list(DebugTasks) + list(ConfigTasks)
    )

    print()
    user_choice: int = 0
    while user_choice < len(enum_indexer):
        user_choice = ask_for_choice(user_choices, headers=True)
        if user_choice < len(enum_indexer):
            task = enum_indexer[user_choice]
            log(f"\nExecuting '{task.name}' task...\n")
            handler = COMMAND_HANDLER_MAP[task]
            handler(database, clock)
            get_input(message="\nPress Enter to continue...", end="")

    log("\nClosing the app...")


def parse_options(enum: type[TaskEnum]) -> list[str]:
    return [e.name.replace('_', ' ').capitalize() for e in enum]


if __name__ == '__main__':
    run_console_loop(Path("../../humble_logistics.sqlite"), VirtualClock())
