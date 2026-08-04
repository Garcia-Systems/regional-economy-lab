from dataclasses import dataclass, field
from heapq import heappop, heappush

from regional_economy.events import Event


@dataclass
class DeterministicScheduler:
    """Order integer-time events by time and then insertion sequence."""

    _queue: list[tuple[int, int, Event]] = field(default_factory=list)
    _sequence: int = 0

    def schedule(self, event: Event) -> None:
        heappush(self._queue, (event.time, self._sequence, event))
        self._sequence += 1

    def run(self) -> tuple[Event, ...]:
        ordered: list[Event] = []
        while self._queue:
            ordered.append(heappop(self._queue)[2])
        return tuple(ordered)

