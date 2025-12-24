# --- Atomic "Accumulator" Clock ---
import threading
import time

from logistics.io_utils import log


class VirtualClock:
    __slots__ = ("_last_real_time", "_lock", "_scale", "_virtual_time")

    def __init__(self):
        self._lock = threading.Lock()
        self._scale = 1.0
        self._last_real_time = time.time()
        self._virtual_time = self._last_real_time

    def get_time(self) -> float:
        """
        Updates and returns the current virtual time.
        """
        with self._lock:
            now_real = time.time()
            delta_real = now_real - self._last_real_time

            # Add the progress since last check, scaled
            self._virtual_time += delta_real * self._scale

            # Update the marker for next time
            self._last_real_time = now_real

            return self._virtual_time

    def set_scale(self, new_scale: float) -> None:
        # IMPORTANT: Force an update before changing scale,
        # so the time passed SO FAR is calculated with the OLD scale.
        self.get_time()  # This updates virtual_time using the current scale

        with self._lock:
            self._scale = new_scale
            log(f"[Clock] Scale changed to {self._scale}x")

    def get_scale(self) -> float:
        return self._scale

    def jump(self, seconds: int) -> None:
        with self._lock:
            self._virtual_time += seconds
            log(f"[Clock] Jumped {seconds}s")
