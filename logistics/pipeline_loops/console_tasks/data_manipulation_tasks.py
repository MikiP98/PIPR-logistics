import math

from pipeline_loops.virtual_clock import VirtualClock

from logistics.database.database import Database
from logistics.io_utils import ask_for_bool, ask_for_int, ask_for_string, ask_for_time, warn


def add_warehouses_task(database: Database, _: VirtualClock) -> bool:
    name = ask_for_string("Provide the name of the warehouse")
    print()
    location = ask_for_string("Provide the location of the warehouse")
    print()
    capacity = ask_for_int("Provide the capacity of the warehouse (in cm^3)", maximum=9223372036854775807)
    confirm = ask_for_bool(
        f"Confirm the addition of warehouse: name='{name}', location='{location}', capacity={capacity}'",
    )
    if confirm:
        return database.add_warehouse(name, location, capacity)
    else:
        print()
        warn("Cancelling the addition of the warehouse")
    return False


def add_product_task(database: Database, _: VirtualClock) -> bool:
    name = ask_for_string("Provide the name of the product")
    print()
    volume_cm = ask_for_int("Provide the volume of the product (cm^3)")
    print()
    confirm = ask_for_bool(f"Confirm the addition of product: name='{name}', volume={volume_cm}")
    if confirm:
        return database.add_product(name, volume_cm)
    else:
        print()
        warn("Cancelling the addition of the product")
    return False
