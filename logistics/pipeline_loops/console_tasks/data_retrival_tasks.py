from logistics.database.database import Database
from logistics.io_utils import ask_for_int, log, print_table
from logistics.pipeline_loops.virtual_clock import VirtualClock


def show_warehouses_task(database: Database, _: VirtualClock) -> None:
    warehouses = database.get_warehouses()
    print_table(warehouses, ("ID", "NAME", "LOCATION", "CAPACITY", "FILLED_CAPACITY", "RESERVED_CAPACITY"))


def show_warehouse_details(database: Database, _: VirtualClock) -> None:
    warehouse_id = ask_for_int("Provide warehouse ID: ")
    print()
    warehouse_data, stock, incoming_transports, outgoing_transports, passing_transports = (
        database.get_warehouse_details(warehouse_id)
    )
    log("WAREHOUSE METADATA:")
    print_table([warehouse_data], ("ID", "NAME", "LOCATION", "CAPACITY", "FILLED_CAPACITY", "RESERVED_CAPACITY"))
    print()

    if len(stock) > 0:
        log("WAREHOUSE STOCK:")
        print_table(stock, ("ID", "NAME", "BARCODE", "COUNT", "TOTAL_VOLUME"))
    else:
        log("WAREHOUSE IS EMPTY")
    print()

    if len(incoming_transports) > 0:
        log("INCOMING TRANSPORTS:")
        print_table(incoming_transports, ("TRANSPORT ID", "SOURCE ID", "SOURCE NAME", "SOURCE LOCATION"))
    else:
        log("THERE ARE NO INCOMING TRANSPORTS")
    print()

    if len(outgoing_transports) > 0:
        log("OUTGOING TRANSPORTS:")
        print_table(outgoing_transports, ("TRANSPORT ID", "TARGET ID", "TARGET NAME", "TARGET LOCATION"))
    else:
        log("THERE ARE NO OUTGOING TRANSPORTS")
    print()

    if len(passing_transports) > 0:
        log("PASSING TRANSPORTS:")
        print_table(
            passing_transports,
            (
                "TRANSPORT ID",
                "SOURCE ID", "SOURCE NAME", "SOURCE LOCATION",
                "TARGET ID", "TARGET NAME", "TARGET LOCATION"
            )
        )
    else:
        log("THERE ARE NO PASSING TRANSPORTS")


def show_products_task(database: Database, _: VirtualClock) -> None:
    products = database.get_products()
    print_table(products, ("ID", "NAME", "BARCODE", "VOLUME (cm^3)"))
