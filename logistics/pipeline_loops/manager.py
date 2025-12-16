# coding=utf-8
import threading
import time

from logistics.io_utils import log
from logistics.pipeline_loops import console_loop, event_loop


# --- 1. Your "Accumulator" Clock ---
class VirtualClock:
    def __init__(self):
        self.lock = threading.Lock()
        self.scale = 1.0
        self.virtual_time = 0.0  # The "Accumulated" virtual time
        self.last_real_time = time.time()

        # Initialize virtual time to now (optional, or start at 0 for a fresh sim)
        self.virtual_time = time.time()

    def get_time(self):
        """
        Updates and returns the current virtual time.
        """
        with self.lock:
            now_real = time.time()
            dt_real = now_real - self.last_real_time

            # Add the progress since last check, scaled
            self.virtual_time += dt_real * self.scale

            # Update the marker for next time
            self.last_real_time = now_real

            return self.virtual_time

    def set_scale(self, new_scale):
        with self.lock:
            # IMPORTANT: Force an update before changing scale,
            # so the time passed SO FAR is calculated with the OLD scale.
            self.get_time()  # This updates virtual_time using the current scale

            self.scale = new_scale
            print(f"[Clock] Scale changed to {self.scale}x")

    def jump(self, seconds):
        with self.lock:
            # Force update first
            self.get_time()
            self.virtual_time += seconds
            print(f"[Clock] Jumped {seconds}s")


clock = VirtualClock()


def start_pipeline_loops() -> None:
    log("Starting event loop")
    event_thread = threading.Thread(target=event_loop.run_event_loop, daemon=True)
    event_thread.start()

    log("Starting terminal loop")
    console_loop.run_console_loop()

    # TODO: Pass the DB path to both loops
