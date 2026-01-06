import math

from pipeline_loops.virtual_clock import VirtualClock

from logistics.database.database import Database
from logistics.io_utils import (
    ask_for_bool,
    ask_for_choice,
    ask_for_int,
    ask_for_string,
    ask_for_time,
    print_table,
    warn,
)


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
    else:
        warn("Cancelling the addition of the transport route/warehouse connection")
        return False


def initialize_transport_task(database: Database, _: VirtualClock) -> bool:
    source_warehouse_id = ask_for_int("Provide the source warehouse ID")
    target_warehouse_id = ask_for_int("Provide the target warehouse ID")

    transport_stock: dict[int, int] = {}
    product_id: int | None = -1
    while product_id is not None:
        product_id = ask_for_int("Provide the product ID (leave empty to stop)", allow_none=True)
        if product_id is not None:
            count = ask_for_int("Provide the amount of product to transfer", minimum=1)
            confirm = ask_for_bool(f"Confirm the addition of product '{product_id}' in count '{count}' to teh transfer")
            if confirm:
                transport_stock[product_id] = count

    msg = [
        "Confirm the initialization of the transport from warehouse '{source_warehouse_id}' "
        "to warehouse '{target_warehouse_id}' "
        "with stock:"
    ]
    for key, value in transport_stock.items():
        msg.append(f"- {key}: {value}x")
    confirm = ask_for_bool('\n'.join(msg))
    if confirm:
        database.initialize_transport(source_warehouse_id, target_warehouse_id, transport_stock)
        return True
    else:
        warn("Cancelling the initialization of the transport")
        return False


def remove_warehouse_task(database: Database, _: VirtualClock) -> bool:
    warehouse_id = ask_for_int("Provide the warehouse ID")
    confirm = ask_for_bool(f"Confirm the removal of the warehouse with id '{warehouse_id}'")
    if confirm:
        # Handle existing stock
        stock = database.get_stock(warehouse_id)
        if len(stock) > 0:
            warn("Warehouse selected for deletion is not empty")
            confirm = False
            while not confirm:
                choice = ask_for_choice(
                    ["Remove stock", "Transport stock"],
                    "What do you want to do with existing stock?"
                )
                if choice == 0:
                    confirm = ask_for_bool(f"Confirm the removal of all stock from warehouse '{warehouse_id}'")
                    if confirm:
                        for entry in stock:
                            database.remove_stock(warehouse_id, entry[0], None)
                else:  # choice == 1
                    target_warehouse_id = ask_for_int("Provide the target warehouse ID")
                    confirm = ask_for_bool(
                        f"Confirm the transport of all stock from warehouse '{warehouse_id}' "
                        f"to warehouse '{target_warehouse_id}'"
                    )
                    if confirm:
                        transport_stock = {}
                        for entry in stock:
                            transport_stock[entry[0]] = entry[1]
                        database.initialize_transport(warehouse_id, target_warehouse_id, transport_stock)
        # Handle incoming transports
        incoming_transports = database.get_incoming_transports(warehouse_id)
        if len(incoming_transports) > 0:
            warn("Incoming transports found")
            for transport_id, target_warehouse_id in incoming_transports:
                choice = ask_for_choice(
                    ["Cancel", "Reroute"],
                    f"What do you want to do with transport '{transport_id}' '"
                )
                if choice == 1:
                    target_warehouse_id = ask_for_int("Provide the new target warehouse ID")
                database.reroute_transport(transport_id, target_warehouse_id)

        database.remove_warehouse(warehouse_id)


def remove_product_task(database: Database, _: VirtualClock) -> None:
    product_id = ask_for_int("Provide the product ID")
    confirm = ask_for_bool(f"Confirm the removal of the product '{product_id}'")
    if confirm:
        stock = database.get_product_stock(product_id)
        if len(stock) > 0:
            warn(f"Product selected for deletion is located in '{len(stock)}' warehouses")
            print_table(stock, ("WAREHOUSE ID", "COUNT"))
            confirm = ask_for_bool("Confirm the removal of this stock alongside the product")
            if confirm:
                for warehouse_id, _ in stock:
                    database.remove_stock(warehouse_id, product_id, None)
        if confirm:
            database.remove_product(product_id)


def remove_transport_route_task(database: Database, _: VirtualClock) -> None:
    source_warehouse_id = ask_for_int("Provide the source warehouse ID")
    target_warehouse_id = ask_for_int("Provide the target warehouse ID")
    is_two_way = ask_for_bool("Is the route a two-way route?")
    database.remove_transport_route(source_warehouse_id, target_warehouse_id, is_two_way)


def remove_stock_task(database: Database, _: VirtualClock) -> bool:
    warehouse_id = ask_for_int("Provide the warehouse ID")
    product_id = ask_for_int("Provide the product ID")
    count = ask_for_int("Provide the number of stock", allow_none=True)
    confirm = ask_for_bool(
        f"Confirm the removal of stock '{product_id}' "
        f"to warehouse '{warehouse_id}' "
        f"in count '{count if count is not None else "all"}'"
    )
    if confirm:
        return database.remove_stock(warehouse_id, product_id, count)
    else:
        warn("Cancelling the removal of the stock")
        return False
