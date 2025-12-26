import atexit
import sqlite3
from importlib import resources
from pathlib import Path

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

    # DataManipulationTasks
    def add_warehouse(self, name: str, location: str, capacity: int) -> bool:
        result: bool = self._cursor.execute(
            "INSERT INTO warehouses (name, location, capacity_volume_cm, reserved_capacity_volume_cm)"
            "VALUES (?, ? ,?, 0)",
            (name.lower(), location.lower(), capacity)
        ).fetchone()
        self._conn.commit()
        return result
