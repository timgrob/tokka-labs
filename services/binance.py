from models.transaction import Transaction
from config import BINANCE_API_URL, ETH_USDT_SYMBOL
import httpx


async def fetch_ethusdt_price_at_timestamp(timestamp: int) -> float:
    params = {
        "symbol": ETH_USDT_SYMBOL,
        "interval": "1m",
        "startTime": int(timestamp * 1000),     # Convert seconds to milliseconds
        "limit": 1
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url=BINANCE_API_URL, params=params)
        data = response.json()
        price = float(data[0][4])   # Closing price of ETH/USDT
        return price


async def fetch_ethusdt_prices_at_timestamps(timestamps: list[int]) -> list[float]:
    prices = []
    for ts in timestamps:
        price = await fetch_ethusdt_price_at_timestamp(ts)
        prices.append(price)

    return prices
