from regional_economy.clock import DeterministicScheduler
from regional_economy.events import Event


def test_events_at_same_time_keep_insertion_order() -> None:
    scheduler = DeterministicScheduler()
    scheduler.schedule(Event(2, "first"))
    scheduler.schedule(Event(1, "earlier"))
    scheduler.schedule(Event(2, "second"))
    assert [event.detail for event in scheduler.run()] == ["earlier", "first", "second"]

