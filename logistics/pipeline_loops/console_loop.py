from collections.abc import Callable
from enum import Enum, auto
from pathlib import Path

from logistics.database.database import Database
from logistics.io_utils import (
    ask_for_choice,
    get_input,
    log, error,
)
from logistics.pipeline_loops.console_tasks.data_manipulation_tasks import (
    add_product_task,
    add_stock_task,
    add_transport_route_task,
    add_warehouses_task,
    edit_product_task,
    edit_warehouse_connection_task,
    edit_warehouse_task,
    initialize_transport_task,
    remove_product_task,
    remove_stock_task,
    remove_transport_route_task,
    remove_warehouse_task, cancel_transport_task,
)
from logistics.pipeline_loops.console_tasks.data_retrival_tasks import (
    show_active_transports_task,
    show_finished_transports_task,
    show_products_task,
    show_transport_details_task,
    show_warehouse_connections_task,
    show_warehouse_details_task,
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
    SHOW_TRANSPORT_DETAILS = auto()

    SHOW_PRODUCTS = auto()
    SHOW_PRODUCT_DETAILS = auto()


class DataManipulationTasks(TaskEnum):
    ADD_WAREHOUSE = auto()
    ADD_PRODUCT = auto()
    ADD_STOCK = auto()
    ADD_WAREHOUSE_CONNECTION = auto()

    INITIALIZE_TRANSPORT = auto()
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


# Config tasks:
# - edit db connection config
# - export config
# - import config
# - delete config
# - export database
# - import database
# - delete database

class ConfigTasks(TaskEnum):
    CHANGE_CONFIG = auto()
    EXPORT_CONFIG = auto()
    IMPORT_CONFIG = auto()
    DELETE_CONFIG = auto()

    EXPORT_DATABASE = auto()
    IMPORT_DATABASE = auto()
    DELETE_DATABASE = auto()


COMMAND_HANDLER_MAP: dict[TaskEnum, Callable[[Database, VirtualClock], None]] = {
    # DataRetrivalTasks
    DataRetrivalTasks.SHOW_WAREHOUSES: show_warehouses_task,
    DataRetrivalTasks.SHOW_WAREHOUSE_DETAILS: show_warehouse_details_task,
    DataRetrivalTasks.SHOW_WAREHOUSE_CONNECTIONS: show_warehouse_connections_task,
    DataRetrivalTasks.SHOW_PRODUCTS: show_products_task,
    DataRetrivalTasks.SHOW_ACTIVE_TRANSPORTS: show_active_transports_task,
    DataRetrivalTasks.SHOW_FINISHED_TRANSPORTS: show_finished_transports_task,
    DataRetrivalTasks.SHOW_TRANSPORT_DETAILS: show_transport_details_task,

    # DataManipulationTasks
    DataManipulationTasks.ADD_WAREHOUSE: add_warehouses_task,
    DataManipulationTasks.ADD_PRODUCT: add_product_task,
    DataManipulationTasks.ADD_STOCK: add_stock_task,
    DataManipulationTasks.ADD_WAREHOUSE_CONNECTION: add_transport_route_task,

    DataManipulationTasks.INITIALIZE_TRANSPORT: initialize_transport_task,

    DataManipulationTasks.REMOVE_WAREHOUSE: remove_warehouse_task,
    DataManipulationTasks.REMOVE_PRODUCT: remove_product_task,
    DataManipulationTasks.REMOVE_WAREHOUSE_CONNECTION: remove_transport_route_task,
    DataManipulationTasks.REMOVE_STOCK: remove_stock_task,

    DataManipulationTasks.EDIT_WAREHOUSE: edit_warehouse_task,
    DataManipulationTasks.EDIT_PRODUCT: edit_product_task,
    DataManipulationTasks.EDIT_WAREHOUSE_CONNECTION: edit_warehouse_connection_task,
    DataManipulationTasks.CANCEL_TRANSPORT: cancel_transport_task,

    # DebugTasks
    DebugTasks.CHANGE_TIME_SIMULATION_SCALE: change_time_simulation_scale_task,
    DebugTasks.OFFSET_SIMULATION_TIME: offset_simulation_time_task,

    # ConfigTasks
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
            handler = COMMAND_HANDLER_MAP.get(task)
            if handler is not None:
                handler(database, clock)
                get_input(message="\nPress Enter to continue...", end="")
            else:
                error("SELECTED TASK IS NOT YET IMPLEMENTED")

    log("\nClosing the app...")


def parse_options(enum: type[TaskEnum]) -> list[str]:
    return [e.name.replace('_', ' ').capitalize() for e in enum]


if __name__ == '__main__':
    run_console_loop(Path("../../humble_logistics.sqlite"), VirtualClock())
