import pytest
from services.binance import fetch_ethusdt_price_at_timestamp, fetch_ethusdt_prices_at_timestamps


@pytest.mark.asyncio
async def test_fetch_ethusdt_price_at_timestamp():
    timestamp = 1738672600
    response = await fetch_ethusdt_price_at_timestamp(timestamp)

    assert isinstance(response, float)
    assert response == 2808.47000000
    

@pytest.mark.asyncio
async def test_fetch_ethusdt_prices_at_timestamps():
    timestamps = [1738672400, 1738672500, 1738672600]
    response = await fetch_ethusdt_prices_at_timestamps(timestamps)

    assert isinstance(response, list)
    assert len(response) == 3
    assert isinstance(response[0], float)

    assert response[0] == 2812.81
    assert response[1] == 2817.6
    assert response[2] == 2808.47


@pytest.mark.asyncio
async def test_fetch_ethusdt_prices_at_timestamps_empyt():
    timestamps = []
    response = await fetch_ethusdt_prices_at_timestamps(timestamps)

    assert isinstance(response, list)
    assert len(response) == 0
