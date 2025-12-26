# import math
import time
from pathlib import Path

# from database.database import Database
from logistics.pipeline_loops.virtual_clock import VirtualClock


def run_event_loop(db_path: Path, clock: VirtualClock) -> None:
    # database = Database(db_path)
    # Track the last virtual minute we successfully processed
    # Round down to the nearest minute to align cleanly
    # last_processed_virtual = math.floor(clock.get_time() / 60) * 60

    while True:
        # TODO: Implement logic

        time.sleep(60 / clock.get_scale())
        # TODO: Sync to the end of a minute
