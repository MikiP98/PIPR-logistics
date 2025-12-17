# --- Atomic "Accumulator" Clock ---
import threading
import time


class VirtualClock:
    def __init__(self):
        self.lock = threading.Lock()
        self.scale = 1.0
        self.last_real_time = time.time()
        self.virtual_time = self.last_real_time

    def get_time(self) -> float:
        """
        Updates and returns the current virtual time.
        """
        with self.lock:
            now_real = time.time()
            delta_real = now_real - self.last_real_time

            # Add the progress since last check, scaled
            self.virtual_time += delta_real * self.scale

            # Update the marker for next time
            self.last_real_time = now_real

            return self.virtual_time

    def set_scale(self, new_scale: float) -> None:
        with self.lock:
            # IMPORTANT: Force an update before changing scale,
            # so the time passed SO FAR is calculated with the OLD scale.
            self.get_time()  # This updates virtual_time using the current scale

            self.scale = new_scale
            print(f"[Clock] Scale changed to {self.scale}x")

    def jump(self, seconds: int) -> None:
        with self.lock:
            # Force update first
            self.get_time()
            self.virtual_time += seconds
            print(f"[Clock] Jumped {seconds}s")
