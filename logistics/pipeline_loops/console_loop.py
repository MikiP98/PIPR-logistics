# coding=utf-8
from enum import Enum
from pathlib import Path

from logistics.pipeline_loops.virtual_clock import VirtualClock


class Commands(Enum):
    DELETE_CONFIG = None


def run_console_loop(db_path: Path, clock: VirtualClock):
    ...
