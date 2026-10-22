import math
from threading import Event, Thread
from time import monotonic

from app.state import ApplicationState


class SimulationWorker:
    """Advance the shared simulation on a background thread."""

    def __init__(
        self,
        state: ApplicationState,
        interval: float = 0.1,
    ) -> None:
        if not math.isfinite(interval) or interval <= 0:
            raise ValueError("Worker interval must be positive and finite.")

        self.state = state
        self.interval = interval
        self._stop_event = Event()
        self._thread: Thread | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = Thread(
            target=self._run,
            name="simulation-worker",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()
            self._thread = None

    def _run(self) -> None:
        previous_time = monotonic()

        while not self._stop_event.wait(self.interval):
            current_time = monotonic()
            elapsed = current_time - previous_time
            previous_time = current_time

            with self.state.lock:
                self.state.driver.update(elapsed)
