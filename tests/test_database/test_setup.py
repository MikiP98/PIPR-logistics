# coding=utf-8
from importlib import resources as impresources

from logistics import database
from logistics.database.setup import EXPECTED_TABLES


def test_code_integrity():
    schema_script = (impresources.files(database) / "database_schema.sql").read_text(encoding="utf-8")
    assert schema_script.count("CREATE TABLE") == len(EXPECTED_TABLES)
