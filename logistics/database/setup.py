# coding=utf-8
import sqlite3

from importlib import resources as impresources
from pathlib import Path

from logistics import database


def setup_new_database(db_path: Path) -> None:
    schema_script = (impresources.files(database) / "database_schema.sql").read_text(encoding="utf-8")

    conn = sqlite3.connect(db_path)

    try:
        conn.executescript(schema_script)
        print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

    raise NotImplemented()


if __name__ == "__main__":
    setup_new_database(Path("./"))
