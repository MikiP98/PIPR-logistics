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

    # DataRetrivalTasks
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

    # DataManipulationTasks
    def add_warehouse(self, name: str, location: str, capacity: int) -> bool:
        result: bool = self._cursor.execute(
            "INSERT INTO warehouses (name, location, capacity_volume_cm, reserved_capacity_volume_cm)"
            "VALUES (?, ? ,?, 0)",
            (name.lower(), location.lower(), capacity)
        ).fetchone()
        self._conn.commit()
        return result

    def add_product(self, name: str, volume_cm: int) -> bool:
        name = name.strip().lower()
        result: bool = self._cursor.execute(
            "INSERT INTO products (name, barcode, volume_cm) VALUES (?, ?, ?)",
            (name, hash(name), volume_cm)  # hash() is enough of a barcode approximation
        ).fetchone()
        self._conn.commit()
        return result

    def add_stock(self, warehouse_id: int, product_id: int, count: int) -> bool:
        if count < 0:
            raise ValueError("count must be positive")

        query = fetch_sql("add_stock.sql")
        try:
            self._cursor.execute(query, (product_id, warehouse_id, count))
            self._conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            # Catches foreign key violations (e.g., product/warehouse doesn't exist)
            print()
            error(f"Error adding stock: {e}")
            return False

    def add_transport_route(
            self, source_warehouse_id: int, destination_warehouse_id: int, minutes: int, is_two_way: bool
    ) -> bool:
        return self._cursor.execute(
            "INSERT INTO connections VALUES (?, ? ,? ,?)",
            (source_warehouse_id, destination_warehouse_id, minutes, is_two_way)
        ).fetchone()

    def remove_stock(self, warehouse_id: int, product_id: int, count: int) -> bool:
        if count is not None and count < 0:
            raise ValueError("count must be positive")

        query_check = "SELECT count FROM stock WHERE product_id = ? AND warehouse_id = ?"
        current_row = self._cursor.execute(query_check, (product_id, warehouse_id)).fetchone()

        if not current_row:
            raise ValueError("stock does not exist")

        current_count = current_row[0]

        if current_count - count < 0:
            raise ValueError("You can't remove more that what's already there")

        if current_count - count == 0:
            query_action = "DELETE FROM stock WHERE product_id = ? AND warehouse_id = ?"
            self._cursor.execute(query_action, (product_id, warehouse_id))

        else:
            query_action = "UPDATE stock SET count = count - ? WHERE product_id = ? AND warehouse_id = ?"
            self._cursor.execute(query_action, (current_count - count, product_id, warehouse_id))

        self._conn.commit()
        return True
