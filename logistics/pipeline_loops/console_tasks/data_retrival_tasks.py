from logistics.database.database import Database
from logistics.io_utils import ask_for_int, log, print_table
from logistics.pipeline_loops.virtual_clock import VirtualClock


def show_warehouses_task(database: Database, _: VirtualClock) -> None:
    warehouses = database.get_warehouses()
    print_table(warehouses, ("ID", "NAME", "LOCATION", "CAPACITY", "FILLED_CAPACITY", "RESERVED_CAPACITY"))


def show_warehouse_details_task(database: Database, _: VirtualClock) -> None:
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


def show_warehouse_connections_task(database: Database, _: VirtualClock) -> None:
    connections = database.get_warehouse_connections()
    print_table(
        connections,
        (
            "ID",
            "SOURCE WAREHOUSE ID", "SOURCE WAREHOUSE NAME", "SOURCE WAREHOUSE LOCATION",
            "TARGET WAREHOUSE ID", "TARGET WAREHOUSE NAME", "TARGET WAREHOUSE LOCATION",
            "TRANSPORTATION TIME"
        )
    )


def show_products_task(database: Database, _: VirtualClock) -> None:
    products = database.get_products()
    print_table(products, ("ID", "NAME", "BARCODE", "VOLUME (cm^3)"))


def show_active_transports_task(database: Database, _: VirtualClock) -> None:
    active_transports = database.get_active_transports()
    print_table(
        active_transports,
        (
            "ID",
            "SOURCE WAREHOUSE ID", "SOURCE WAREHOUSE NAME", "SOURCE WAREHOUSE LOCATION",
            "TARGET WAREHOUSE ID", "TARGET WAREHOUSE NAME", "TARGET WAREHOUSE LOCATION",
            "TRANSPORT START TIME",
            "LAST STOP WAREHOUSE ID", "LAST STOP WAREHOUSE NAME", "LAST STOP WAREHOUSE LOCATION", "LAST STOP TIME",
            "NEXT STOP WAREHOUSE ID", "NEXT STOP WAREHOUSE NAME", "NEXT STOP WAREHOUSE LOCATION",
        )  # TODO: Next stop and finish ETA?
    )


def show_finished_transports_task(database: Database, _: VirtualClock) -> None:
    finished_transports = database.get_finished_transports()
    print_table(
        finished_transports,
        (
            "ID",
            "SOURCE WAREHOUSE ID", "SOURCE WAREHOUSE NAME", "SOURCE WAREHOUSE LOCATION",
            "TARGET WAREHOUSE ID", "TARGET WAREHOUSE NAME", "TARGET WAREHOUSE LOCATION",
            "STOP COUNT",
            "TRANSPORT START TIME", "TRANSPORT END TIME", "TOTAL TRANSPORT TIME"
        )
    )


def show_transport_details_task(database: Database, _: VirtualClock) -> None:
    transport_id = ask_for_int("Provide the id of the transport")

    is_active = database.is_transport_active(transport_id)

    if is_active:
        transport_details, stops, cargo = database.get_active_transport_details(transport_id)
        eta = None
        # TODO: eta!
        print_table(
            [(*transport_details[:-3], eta)],
            (
                "ID",
                "SOURCE WAREHOUSE ID", "SOURCE WAREHOUSE NAME", "SOURCE WAREHOUSE LOCATION",
                "TARGET WAREHOUSE ID", "TARGET WAREHOUSE NAME", "TARGET WAREHOUSE LOCATION",
                "START TIME", "ETA"
            )
        )
        # TODO: Percentage progress?

    else:
        transport_details, stops, cargo = database.get_finished_transport_details(transport_id)
        print_table(
            [transport_details],
            (
                "ID",
                "SOURCE WAREHOUSE ID", "SOURCE WAREHOUSE NAME", "SOURCE WAREHOUSE LOCATION",
                "TARGET WAREHOUSE ID", "TARGET WAREHOUSE NAME", "TARGET WAREHOUSE LOCATION",
                "START TIME", "END TIME"
            )
        )

    print_table(
        stops,
        (
            "ROUTE ID",
            "SOURCE WAREHOUSE ID", "SOURCE WAREHOUSE NAME", "SOURCE WAREHOUSE LOCATION",
            "TARGET WAREHOUSE ID", "TARGET WAREHOUSE NAME", "TARGET WAREHOUSE LOCATION",
            "START TIME", "END TIME"
        )
    )
    print_table(
        cargo,
        (
            "PRODUCT ID",
            "PRODUCT NAME",
            "PRODUCT BARCODE",
            "PRODUCT COUNT",
            "TOTAL VOLUME (cm^3)",
        )
    )

    # TODO: eta?
    raise NotImplementedError
