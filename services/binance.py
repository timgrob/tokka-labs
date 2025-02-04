from models.transaction import Transaction
from config import BINANCE_API_URL, ETH_USDT_SYMBOL
import httpx


async def fetch_ethusdt_price_at_timestamp(timestamp: int) -> float:
    params = {
        "symbol": ETH_USDT_SYMBOL,
        "interval": "1m",
        "startTime": int(timestamp * 1000),  # Convert seconds to milliseconds
        "limit": 1
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url=BINANCE_API_URL, params=params)
        data = response.json()
        price = float(data[0][4])  # Closing price of ETH/USDT
        return price


async def fetch_ethusdt_prices_at_timestamps(timestamps: list[int]) -> list[float]:
    prices = []
    for ts in timestamps:
        price = await fetch_ethusdt_price_at_timestamp(ts)
        prices.append(price)

    return prices







async def convert_fees_to_usdt(txns: list[Transaction]) -> list[float]:
    fees_in_usdt: list[float] = []
    for txn in txns:
        eth_price = await fetch_ethusdt_price_at_timestamp(txn.time_stamp)
        fees_in_usdt.append(txn.gas_fee * eth_price)

    return fees_in_usdt


# async def fetch_latest_price(symbol: str) -> float:
#     params = {
#         "symbol": symbol,
#         "limit": 1
#     }
#     res_klines = await httpx.get(url=BINANCE_API_URL, params=params)
#     price_data = res_klines.json()
#     print(price)


# async def fetch_price_at_timestamp(symbol: str, timestamp: int) -> float:
#     params = {
#         "symbol": symbol, 
#         "startTime": timestamp,
#         "limit": 1
#     }
#     res_klines = await httpx.get(url=BINANCE_API_URL, params=params)
#     print(price)

