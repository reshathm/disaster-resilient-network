import math

from app.simulation.engine import SimulationEngine


class SimulationDriver:
    """Convert elapsed time into fixed simulation steps."""

    def __init__(
        self,
        engine: SimulationEngine,
        fixed_dt: float = 0.1,
        max_steps_per_update: int = 10,
    ) -> None:
        if not math.isfinite(fixed_dt) or fixed_dt <= 0:
            raise ValueError("Fixed timestep must be positive and finite.")
        if type(max_steps_per_update) is not int or max_steps_per_update <= 0:
            raise ValueError("Maximum steps must be a positive integer.")

        self.engine = engine
        self.fixed_dt = fixed_dt
        self.max_steps_per_update = max_steps_per_update
        self.accumulator = 0.0
        self.paused = False
        self.speed = 1.0

    def update(self, elapsed: float) -> int:
        """Advance fixed steps and return the number executed."""
        if not math.isfinite(elapsed) or elapsed < 0:
            raise ValueError("Elapsed time must be finite and nonnegative.")

        if self.paused:
            return 0

        self.accumulator += elapsed * self.speed
        steps = 0

        while (
            self.accumulator + 1e-12 >= self.fixed_dt
            and steps < self.max_steps_per_update
        ):
            self.engine.step(self.fixed_dt)
            self.accumulator = max(0.0, self.accumulator - self.fixed_dt)
            steps += 1

        # Bound catch-up work after long stalls.
        max_backlog = self.fixed_dt * self.max_steps_per_update
        self.accumulator = min(self.accumulator, max_backlog)

        return steps

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False

    def set_speed(self, speed: float) -> None:
        if not math.isfinite(speed) or speed <= 0:
            raise ValueError("Speed must be positive and finite.")
        self.speed = speed
