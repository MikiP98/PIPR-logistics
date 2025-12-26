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


def add_stock_task(database: Database, _: VirtualClock) -> bool:
    warehouse_id = ask_for_int("Provide the warehouse ID")
    product_id = ask_for_int("Provide the product ID")
    count = ask_for_int("Provide the number of stock")
    confirm = ask_for_bool(
        f"Confirm the addition of stock '{product_id}' to warehouse '{warehouse_id}' in count '{count}'"
    )
    if confirm:
        return database.add_stock(warehouse_id, product_id, count)
    else:
        warn("Cancelling the addition of the stock")
        return False


def add_transport_route_task(database: Database, _: VirtualClock) -> bool:
    source_warehouse_id = ask_for_int("Provide the source warehouse ID")
    target_warehouse_id = ask_for_int("Provide the target warehouse ID")
    weeks, days, hours, minutes, seconds = ask_for_time("Provide the average travel time")
    is_two_way = ask_for_bool("Is the route two way?")
    minutes = math.ceil(float((((weeks * 7 + days) * 24 + hours) * 60 + minutes) * 60 + seconds) / 60.0)
    confirm = ask_for_bool(
        f"Confirm the addition of {"two way " if is_two_way else ""}transport route "
        f"{"between" if is_two_way else "from"} warehouse '{source_warehouse_id}' "
        f"{"and" if is_two_way else "to"} warehouse '{target_warehouse_id}' taking '{minutes}' minutes"
    )
    if confirm:
        return database.add_transport_route(source_warehouse_id, target_warehouse_id, minutes, is_two_way)
