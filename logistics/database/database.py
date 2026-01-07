import atexit
import sqlite3
from importlib import resources
from pathlib import Path

from io_utils import error

from logistics import database


def fetch_sql(path: str) -> str:
    return (resources.files(database) / f"sql/{path}").read_text(encoding="utf-8")


class Database:
    __slots__ = ("_conn", "_cursor")

    def __init__(self, db_path: Path):
        self._conn = sqlite3.connect(db_path, timeout=10)
        self._conn.execute("PRAGMA foreign_keys = ON")  # Ensure foreign key validation
        self._cursor = self._conn.cursor()

        # Safe connection closing on application exit
        atexit.register(self._conn.close)

    # --------- DATA RETRIVAL TASKS ------------------------------------------------------------------------------------
    def get_warehouses(self) -> list[tuple[int, str, str, int, int, int]]:
        return self._cursor.execute(fetch_sql("warehouses.sql")).fetchall()

    def get_warehouse_details(
            self, warehouse_id: int
    ) -> tuple[
        tuple[int, str, str, int, int, int],
        list[tuple[int, str, int, int, int]],
        list[tuple[int, int, str, str]],
        list[tuple[int, int, str, str]],
        list[tuple[int, str, str]],
    ]:
        warehouse_id_str = str(warehouse_id)

        def get_sql(path: str) -> str:
            return fetch_sql("warehouse_details/" + path + ".sql")

        query = get_sql("warehouse_details")
        warehouse = self._cursor.execute(query, warehouse_id_str).fetchone()

        query = get_sql("stock")
        stock = self._cursor.execute(query, warehouse_id_str).fetchall()

        query = get_sql("incoming_transports")
        incoming_transports = self._cursor.execute(query, warehouse_id_str).fetchall()

        query = get_sql("outgoing_transports")
        outgoing_transports = self._cursor.execute(query, warehouse_id_str).fetchall()

        query = get_sql("passing_transports")
        passing_transports = self._cursor.execute(query, (warehouse_id, warehouse_id)).fetchall()

        return warehouse, stock, incoming_transports, outgoing_transports, passing_transports

    def get_warehouse_connections(self) -> list[tuple[int, int, str, str, int, str, str, bool]]:
        return self._cursor.execute(fetch_sql("warehouse_connections.sql")).fetchall()

    def get_products(self) -> list[tuple[int, str, int, int]]:
        return self._cursor.execute("SELECT * FROM products").fetchall()

    def get_stock(self, warehouse_id: int) -> list[tuple[int, int]]:
        return self._cursor.execute(
            "SELECT product_id, count FROM stock WHERE warehouse_id=?",
            (warehouse_id,)
        ).fetchall()

    def get_product_stock(self, warehouse_id: int) -> list[tuple[int, int]]:
        return self._cursor.execute(
            "SELECT warehouse_id, count FROM stock WHERE product_id=?",
            (warehouse_id,)
        ).fetchall()

    def get_incoming_transports(self, warehouse_id: int) -> list[tuple[int, int]]:
        return self._cursor.execute(
            "SELECT id, source_warehouse_id FROM transports WHERE target_warehouse_id=?",
            (warehouse_id,)
        ).fetchall()

    def get_active_transports(self) -> list[tuple[int, int]]:
        return self._cursor.execute(fetch_sql("get_active_transports.sql")).fetchall()

    def get_finished_transports(self) -> list[tuple[int, int]]:
        return self._cursor.execute(fetch_sql("get_finished_transports.sql")).fetchall()

    def get_active_transport_details(self, warehouse_id: int) -> tuple[
        tuple[int, int, str, str, int, str, str, int, int, int, int],
        list[tuple[int, int, str, str, int, str, str, int, int | None]],
        list[tuple[int, str, int, int, int]]
    ]:
        details = self._cursor.execute(
            fetch_sql("get_active_transport_details.sql"),
            (warehouse_id,)
        ).fetchone()
        stops, cargo = self._get_common_transport_details(warehouse_id)
        return details, stops, cargo

    def get_finished_transport_details(self, warehouse_id: int) -> tuple[
        tuple[int, int, str, str, int, str, str, int, int],
        list[tuple[int, int, str, str, int, str, str, int, int | None]],
        list[tuple[int, str, int, int, int]]
    ]:
        details = self._cursor.execute(
            fetch_sql("get_finished_transport_details.sql"),
            (warehouse_id,)
        ).fetchone()
        stops, cargo = self._get_common_transport_details(warehouse_id)
        return details, stops, cargo

    def _get_common_transport_details(self, warehouse_id: int) -> tuple[
        list[tuple[int, int, str, str, int, str, str, int, int | None]],
        list[tuple[int, str, int, int, int]]
    ]:
        stops = self._cursor.execute(fetch_sql("get_stops.sql"), (warehouse_id,)).fetchall()
        cargo = self._cursor.execute(fetch_sql("get_cargo.sql"), (warehouse_id,)).fetchall()
        return stops, cargo

    def is_transport_active(self, warehouse_id: int) -> bool:
        return bool(self._cursor.execute(fetch_sql("is_transport_active.sql"), (warehouse_id,)).fetchone())

    def get_warehouse_name(self, warehouse_id: int) -> str:
        return self._cursor.execute("SELECT name FROM warehouses WHERE id=?", (warehouse_id,)).fetchone()

    def get_warehouse_location(self, warehouse_id: int) -> str:
        return self._cursor.execute("SELECT location FROM warehouses WHERE id=?", (warehouse_id,)).fetchone()

    def get_warehouse_capacity(self, warehouse_id: int) -> int:
        return self._cursor.execute("SELECT capacity_volume_cm FROM warehouses WHERE id=?", (warehouse_id,)).fetchone()

    def get_product_name(self, product_id: int) -> str:
        return self._cursor.execute("SELECT name FROM products WHERE id=?", (product_id,)).fetchone()

    def get_product_volume(self, product_id: int) -> int:
        return self._cursor.execute("SELECT volume_cm FROM products WHERE id=?", (product_id,)).fetchone()

    def get_warehouse_connection_transportation_time(
            self, source_warehouse_id: int, target_warehouse_id: int, is_two_way: bool
    ) -> int:
        return self._cursor.execute(
            "SELECT transportation_time_minutes FROM connections "
            "WHERE source_warehouse_id=? AND target_warehouse_id=? AND is_two_way=?",
            (source_warehouse_id, target_warehouse_id, is_two_way)
        ).fetchone()

    def get_transport_source(self, transport_id: int) -> int:
        return self._cursor.execute("SELECT target_warehouse_id FROM transports WHERE id=?", (transport_id,)).fetchone()

    # --------- DATA MANIPULATION TASKS --------------------------------------------------------------------------------
    def add_warehouse(self, name: str, location: str, capacity: int) -> None:
        self._cursor.execute(
            "INSERT INTO warehouses (name, location, capacity_volume_cm)"
            "VALUES (?, ? ,?)",
            (name.lower(), location.lower(), capacity)
        ).fetchone()
        self._conn.commit()

    def add_product(self, name: str, volume_cm: int) -> None:
        name = name.strip().lower()
        self._cursor.execute(
            "INSERT INTO products (name, barcode, volume_cm) VALUES (?, ?, ?)",
            (name, hash(name), volume_cm)  # hash() is enough of a barcode approximation
        ).fetchone()
        self._conn.commit()

    def add_stock(self, warehouse_id: int, product_id: int, count: int) -> None:
        if count < 0:
            raise ValueError("count must be positive")

        query = fetch_sql("add_stock.sql")
        try:
            self._cursor.execute(query, (product_id, warehouse_id, count))
            self._conn.commit()
        except sqlite3.IntegrityError as e:
            # Catches foreign key violations (e.g., product/warehouse doesn't exist)
            error(f"Error adding stock: {e}")
            raise

    def add_transport_route(
            self, source_warehouse_id: int, destination_warehouse_id: int, minutes: int, is_two_way: bool
    ) -> None:
        self._cursor.execute(
            "INSERT INTO connections VALUES (?, ? ,? ,?)",
            (source_warehouse_id, destination_warehouse_id, minutes, is_two_way)
        ).fetchone()
        self._conn.commit()

    def initialize_transport(
            self, source_warehouse_id: int, target_warehouse_id: int, transport_stock: dict[int, int]
    ) -> bool:
        self._cursor.execute(
            "INSERT INTO transports (source_warehouse_id, target_warehouse_id) VALUES (?, ?)",
            (source_warehouse_id, target_warehouse_id)
        )
        transport_id: int = self._cursor.lastrowid
        for product_id, count in transport_stock.items():
            self._cursor.execute(
                "INSERT INTO transported_stock (transport_id, product_id, count) VALUES (?, ?, ?)",
                (transport_id, product_id, count)
            )
        self._conn.commit()
        return True

    def remove_stock(self, warehouse_id: int, product_id: int, count: int | None) -> None:
        if count is not None and count < 0:
            raise ValueError("count must be positive")

        query_check = "SELECT count FROM stock WHERE product_id = ? AND warehouse_id = ?"
        current_row = self._cursor.execute(query_check, (product_id, warehouse_id)).fetchone()

        if not current_row:
            raise ValueError("stock does not exist")

        current_count = current_row[0]

        if count is None or current_count - count == 0:
            query_action = "DELETE FROM stock WHERE product_id = ? AND warehouse_id = ?"
            self._cursor.execute(query_action, (product_id, warehouse_id))

        elif current_count - count > 0:
            query_action = "UPDATE stock SET count = count - ? WHERE product_id = ? AND warehouse_id = ?"
            self._cursor.execute(query_action, (count, product_id, warehouse_id))

        else:  # current_count - count < 0
            raise ValueError("You can't remove more that what's there to remove")

        self._conn.commit()

    def remove_warehouse(self, warehouse_id: int) -> None:
        self._cursor.execute("DELETE FROM warehouses WHERE id=?", (warehouse_id,)).fetchone()
        self._conn.commit()

    def remove_product(self, product_id: int) -> None:
        self._cursor.execute("DELETE FROM products WHERE id=?", (product_id,)).fetchone()
        self._conn.commit()

    def remove_transport_route(self, source_warehouse_id: int, destination_warehouse_id: int, is_two_way: bool) -> None:
        self._cursor.execute(
            "DELETE FROM connections WHERE source_warehouse_id=? AND target_warehouse_id=? AND is_two_way=?",
            (source_warehouse_id, destination_warehouse_id, is_two_way)
        )
        self._conn.commit()

    def reroute_transport(self, transport_id: int, new_target_warehouse_id: int) -> None:
        self._cursor.execute(
            "UPDATE transports SET target_warehouse_id = ? WHERE id = ?",
            (new_target_warehouse_id, transport_id)
        ).fetchone()
        self._conn.commit()

    def change_warehouse_name(self, warehouse_id: int, new_name: str) -> None:
        self._cursor.execute("UPDATE warehouses SET name = ? WHERE id = ?", (new_name, warehouse_id))
        self._conn.commit()

    def change_warehouse_location(self, warehouse_id: int, new_location: str) -> None:
        self._cursor.execute("UPDATE warehouses SET location = ? WHERE id = ?", (new_location, warehouse_id))
        self._conn.commit()

    def change_warehouse_capacity(self, warehouse_id: int, new_capacity: int) -> None:
        self._cursor.execute("UPDATE warehouses SET capacity_volume_cm = ? WHERE id = ?", (new_capacity, warehouse_id))
        self._conn.commit()

    def change_product_name(self, product_id: int, new_name: str) -> None:
        self._cursor.execute(
            "UPDATE products SET name = ?, barcode = ? WHERE id = ?",
            (new_name, hash(new_name), product_id)
        )
        self._conn.commit()

    def change_product_volume(self, product_id: int, new_volume: int) -> None:
        self._cursor.execute("UPDATE products SET volume_cm = ? WHERE id = ?", (new_volume, product_id))
        self._conn.commit()

    def change_warehouse_connection_source(
            self, source_warehouse_id: int, target_warehouse_id: int, is_two_way: bool, new_source_warehouse_id: int
    ) -> None:
        self._cursor.execute(
            "UPDATE connections SET source_warehouse_id = ? "
            "WHERE source_warehouse_id = ? AND target_warehouse_id = ? AND is_two_way=?",
            (new_source_warehouse_id, source_warehouse_id, target_warehouse_id, is_two_way)
        )
        self._conn.commit()

    def change_warehouse_connection_target(
            self, source_warehouse_id: int, target_warehouse_id: int, is_two_way: bool, new_target_warehouse_id: int
    ) -> None:
        self._cursor.execute(
            "UPDATE connections SET target_warehouse_id = ? "
            "WHERE source_warehouse_id = ? AND target_warehouse_id = ? AND is_two_way=?",
            (new_target_warehouse_id, source_warehouse_id, target_warehouse_id, is_two_way)
        )
        self._conn.commit()

    def change_warehouse_connection_transportation_target(
            self, source_warehouse_id: int, target_warehouse_id: int, is_two_way: bool, new_transportation_time: int
    ) -> None:
        self._cursor.execute(
            "UPDATE connections SET transportation_time_minutes = ? "
            "WHERE source_warehouse_id = ? AND target_warehouse_id = ? AND is_two_way=?",
            (new_transportation_time, source_warehouse_id, target_warehouse_id, is_two_way)
        )
