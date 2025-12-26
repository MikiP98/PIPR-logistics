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

    # DataManipulationTasks
    def add_warehouse(self, name: str, location: str, capacity: int) -> bool:
        result: bool = self._cursor.execute(
            "INSERT INTO warehouses (name, location, capacity_volume_cm, reserved_capacity_volume_cm)"
            "VALUES (?, ? ,?, 0)",
            (name.lower(), location.lower(), capacity)
        ).fetchone()
        self._conn.commit()
        return result
