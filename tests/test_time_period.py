from models.time_period import TimePeriod
import pytest


def test_instantiate_time_period():
    time_period_info = {
        "start_timestamp": 1704067200,
        "end_timestamp": 1706745600
    }
    tp = TimePeriod(**time_period_info)

    assert isinstance(tp, TimePeriod)
    assert tp.start_timestamp == 1704067200
    assert tp.end_timestamp == 1706745600


def test_instantiate_time_period_failure():
    with pytest.raises(ValueError, match="end_timestamp must be after start_timestamp"):
        time_period_info = {
            "start_timestamp": 1706745600,
            "end_timestamp": 1704067200
            }
        tp = TimePeriod(**time_period_info)
