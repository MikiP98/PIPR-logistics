# coding=utf-8
import os.path
import sqlite3
from dataclasses import dataclass, field
from enum import StrEnum

from importlib import resources as impresources
from pathlib import Path

from logistics.io_utils import ask_for_bool, ask_for_choice, ask_for_string, log, error
from logistics import database


# TODO: Move this somewhere else
class TableName(StrEnum):
    WAREHOUSES = "warehouses"
    CONNECTIONS = "connections"
    PRODUCTS = "products"
    STOCK = "stock"
    TRANSPORTS = "transports"
    TRANSPORT_ROUTES = "transport_routes"
    TRANSPORTED_STOCK = "transported_stock"


EXPECTED_TABLES: frozenset[str] = frozenset(t for t in TableName)


@dataclass(slots=True)
class DBStatus:
    # Parent (folder) permissions
    parent_readable: bool = False
    parent_writable: bool = True

    # File
    exists: bool = False
    is_valid_sqlite: bool = False
    read_permission: bool = False
    write_permission: bool = False
    tables_present: set[str] = field(default_factory=set)
    tables_unknown: set[str] = field(default_factory=set)
    row_counts: dict[str, int] = field(default_factory=dict)

    @property
    def tables_missing(self) -> frozenset[str]:
        return EXPECTED_TABLES - self.tables_present

    @property
    def has_data(self) -> bool:
        return any(count > 0 for count in self.row_counts.values())

    @property
    def has_unknown_tables(self) -> bool:
        return len(self.tables_unknown) != 0

    @property
    def is_healthy(self) -> bool:
        return (
            self.exists
            and self.is_valid_sqlite
            and len(self.tables_missing) == 0
            and len(self.tables_unknown) == 0
        )


def get_db_status(db_path: Path) -> DBStatus:
    status = DBStatus()

    # --- 1. Find the "Anchor" (Deepest Existing Directory) ---
    # We start at the file's parent folder
    anchor = db_path.parent

    # Walk up the tree until we find a folder that actually exists
    # e.g. given "A/B/C/db.sqlite":
    # If "C" is missing, check "B". If "B" is missing, check "A".
    while not anchor.exists():
        # If we hit the root/drive root, and it still doesn't exist, we stop to avoid infinite loops.
        if anchor.parent == anchor:
            break
        anchor = anchor.parent

    # --- 2. Check Anchor Permissions ---
    if anchor.exists():
        status.parent_readable = os.access(anchor, os.R_OK | os.X_OK)
        status.parent_writable = os.access(anchor, os.W_OK)
    else:
        # If we climbed all the way to root and nothing existed (invalid path)
        status.parent_readable = False
        status.parent_writable = False

    if not status.parent_readable:
        # If we can't read the anchor, we can't verify the path further
        return status

    # --- 3. Check File Existence & Perms ---
    if not db_path.exists():
        return status

    status.exists = True
    status.file_readable = os.access(db_path, os.R_OK)
    status.file_writable = os.access(db_path, os.W_OK)

    if not status.file_readable:
        return status

        # --- 4. Check SQLite Internal Structure ---
    try:
        # Use Read-Only mode to be safe
        with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
            status.is_valid_sqlite = True
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            found_tables = {row[0] for row in cursor.fetchall()}

            status.tables_present = found_tables.intersection(EXPECTED_TABLES)
            status.tables_unknown = found_tables - EXPECTED_TABLES

            for table in status.tables_present:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                status.row_counts[table] = cursor.fetchone()[0]

    except sqlite3.DatabaseError:
        status.is_valid_sqlite = False

    return status


def setup_new_database(db_path: Path) -> None:
    schema_script = (impresources.files(database) / "database_schema.sql").read_text(encoding="utf-8")

    conn = sqlite3.connect(db_path)

    try:
        conn.executescript(schema_script)
        log("Database initialized successfully.")
    except sqlite3.Error as e:
        error(f"An error occurred: {e}")
        raise e
    finally:
        conn.close()

    raise NotImplemented()


def try_setup_new_database(path: str = "./", db_name: str = "humble_logistics.sqlite") -> bool:
    full_path = Path(path) / db_name

    log(f"🔍 Inspecting database at: {full_path}")
    status = get_db_status(full_path)

    # Check parent folder viability
    if not (status.parent_readable and status.parent_writable):
        permission = "readable" if status.parent_readable else "writable"
        log(
            f"The path given as the database location is not {permission}. " +
            "Please change the path or try running the app as an administrator."
        )
        change_input_path = ask_for_bool("Do you want to provide new DB path?")
        if change_input_path:
            return try_setup_with_new_db_path(db_name)
        else:
            return False

    # If the database does not exist, create it
    if not status.exists:
        setup_new_database(full_path)
        return True

    # From now on the database file does exist

    # The database file is not a database
    if not status.is_valid_sqlite:
        log("File with the given name already exists at the given path.")
        options = [
            "Change database path",
            "Change database filename",
            "Override the file (file will be permanently lost)",
            "Cancel database setup"
        ]
        selection = ask_for_choice(options)
        if selection == 0:
            return try_setup_with_new_db_path(db_name)
        elif selection == 1:
            return try_setup_with_new_db_path(path)
        elif selection == 2:
            os.remove(full_path)
            return try_setup_with_new_db_path(path)
        else:
            return False

    # TODO
    raise DatabaseStateNotHandledError()


class DatabaseStateNotHandledError(NotImplementedError):
    def __init__(self):
        super().__init__("The database state you we encountered is not handled yet.")


def try_setup_with_new_db_path(db_name: str) -> bool:
    path = ask_for_string("Please provide a new DB path")
    return try_setup_new_database(path, db_name)


def try_setup_with_new_db_filename(path: str) -> bool:
    name = ask_for_string("Please provide a new DB filename")
    return try_setup_new_database(name, path)


if __name__ == "__main__":
    try_setup_new_database()
