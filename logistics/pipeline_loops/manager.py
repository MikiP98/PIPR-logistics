# coding=utf-8
import threading

from logistics.io_utils import log
from logistics.pipeline_loops import console_loop, event_loop
from logistics.pipeline_loops.virtual_clock import VirtualClock


def start_pipeline_loops(db_path: str) -> None:
    clock = VirtualClock()

    log("Starting event loop")
    event_thread = threading.Thread(target=lambda: event_loop.run_event_loop(db_path, clock), daemon=True)
    event_thread.start()

    log("Starting terminal loop")
    console_loop.run_console_loop(db_path, clock)

    # TODO: Pass the DB path to both loops
