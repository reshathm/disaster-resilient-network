from app.network.event_log import EventLog


def test_record_event():
    log = EventLog()

    log.record("NODE_FAILED", "R02 went offline")

    events = log.get_events()

    assert len(events) == 1
    assert events[0].event_type == "NODE_FAILED"
    assert events[0].message == "R02 went offline"


def test_events_are_stored_in_order():
    log = EventLog()

    log.record("NODE_FAILED", "R02 went offline")
    log.record("ROUTE_RECOVERED", "R01 -> R04 -> R03")
    log.record("MESSAGE_DELIVERED", "M001 delivered")

    events = log.get_events()

    assert [event.event_type for event in events] == [
        "NODE_FAILED",
        "ROUTE_RECOVERED",
        "MESSAGE_DELIVERED",
    ]


def test_clear_events():
    log = EventLog()

    log.record("NODE_FAILED", "R02 went offline")
    assert len(log.get_events()) == 1

    log.clear()

    assert log.get_events() == []


def test_get_events_returns_copy():
    log = EventLog()

    log.record("NODE_FAILED", "R02 went offline")

    events = log.get_events()
    events.clear()

    assert len(log.get_events()) == 1