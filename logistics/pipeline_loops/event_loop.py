import math
import time
from pathlib import Path

from database.database import Database
from logistics.pipeline_loops.virtual_clock import VirtualClock


def run_event_loop(db_path: Path, clock: VirtualClock) -> None:
    database = Database(db_path)

    # 0. Calculate the NEXT distinct minute index
    start_time = clock.get_time()
    next_virtual_minute = math.floor(start_time / 60) + 1

    while True:
        current_virtual = clock.get_time()

        # 1. Convert current time to a "minute progress"
        # We process while the current time is past our target minute mark
        while current_virtual >= (next_virtual_minute * 60):
            # Pass the precise timestamp (minute * 60) to the update
            _run_update(database, next_virtual_minute * 60)

            # Increment by exactly 1 minute
            next_virtual_minute += 1

        # 3. Drift-Correcting Sleep
        # Recalculate time because run_update took execution time
        current_virtual = clock.get_time()

        # Target time in seconds is simply the minute integer * 60
        target_seconds = next_virtual_minute * 60
        virtual_seconds_until_next = target_seconds - current_virtual

        if virtual_seconds_until_next > 0:
            scale = clock.get_scale()
            # Avoid division by zero if scale is somehow 0
            if scale > 0:
                time.sleep(min(virtual_seconds_until_next / scale, 5))
                # Cap the sleep to 5s to make the app more responsive to time scale changes and time jumps
            else:
                time.sleep(5)
        # Else we are behind schedule (lagging)! Loop immediately to catch up.


def _run_update(database: Database, timestamp: int) -> None:
    epoch = timestamp * 60

    # TODO: Implement logic
    # Get all the transport routes with a null arrival time
    # Get the final destination of those transports
    # Find the shortest path and start the next transport route
    ...
