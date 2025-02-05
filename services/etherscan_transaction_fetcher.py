from models.transaction import Transaction
from typing import Optional
import asyncio
import httpx


class EtherscanTransactionFetcher:
    BASE_URL = "https://api.etherscan.io/api"
    RATE_LIMIT_DELAY = 0.2

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient()

    async def fetch_all_transactions(self, address: str, block_limit: Optional[int]) -> list[Transaction]:
        all_txns: list[Transaction] = []
        block_range = 10_000

        # Find latest block
        block_params = {
            "module": "proxy",
            "action": "eth_blockNumber",
            "apikey": self.api_key
        }

        block_response = await self.client.get(self.BASE_URL, params=block_params)
        latest_block = int(block_response.json()['result'], 16)

        # For the sake of time, also give the option to limit the number of blocks fetched. 
        # If block_limit is set, only fetch the number of block_limit latest 
        start_block = latest_block - block_limit if block_limit else 12376729  # First bock on chain in pool

        while start_block < latest_block:
            end_block = min(start_block + block_range, latest_block)
            txn_batch = await self.fetch_transactions_batch(address, start_block, end_block)
            all_txns.extend(txn_batch)
            start_block = end_block + 1

        return all_txns

    async def fetch_transactions_batch(self, address: str, start_block: int, end_block: int) -> list[Transaction]:
        page = 1
        offset = 10_000
        txns_block_batch: list[Transaction] = []

        while True:
            try:
                params = {
                    "module": "account",
                    "action": "tokentx",
                    "address": address,
                    "startblock": start_block,
                    "endblock": end_block,
                    "page": page,
                    "offset": offset,
                    "sort": "asc",
                    "apikey": self.api_key
                }
                async with httpx.AsyncClient() as client:
                    response = await client.get(url=self.BASE_URL, params=params)
                    response.raise_for_status()
                    
                    if response.status_code != 200:
                        print(f"Error: something when wrong: {data['message']}")
                        break

                    data = response.json()
                    txns = data['result']

                    # Break out of while-loop if no more transactions are found
                    if not txns:
                        break

                    # Convert response to Transaction list
                    txns_parsed = [Transaction(
                        block_number=txn["blockNumber"],
                        time_stamp=txn["timeStamp"],
                        hash=txn["hash"],
                        gas_price=txn["gasPrice"],
                        gas_used=txn["gasUsed"]
                        ) for txn in txns]

                    txns_block_batch.extend(txns_parsed)
                    page += 1
                    
                    # Sleep to prevent rate limiting
                    await asyncio.sleep(self.RATE_LIMIT_DELAY)

            except Exception as e:
                raise e

        return txns_block_batch
