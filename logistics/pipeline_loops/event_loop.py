# coding=utf-8
import math
import sqlite3
import time
from pathlib import Path

from logistics.pipeline_loops.virtual_clock import VirtualClock


def run_event_loop(db_path: Path, clock: VirtualClock):
    conn = sqlite3.connect(db_path, timeout=10)
    cursor = conn.cursor()

    # We track the last virtual minute we successfully processed
    # We round down to the nearest minute to align cleanly
    last_processed_virtual = math.floor(clock.get_time() / 60) * 60

    while True:
        time.sleep(60 / clock.scale)
        # TODO: Sync to the end of a minute
