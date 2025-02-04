from models.transaction import Transaction
from config import ETHERSCAN_API_URL, POOL_ADDRESS
from dotenv import load_dotenv
import httpx
import os


load_dotenv()


API_KEY = os.getenv('ETHERSCAN_API_KEY')


async def fetch_all_transactions() -> list[Transaction]:
    start_block = 0
    end_block = 99_999_999
    transactions: list[Transaction] = []

    params = {
        "module": "account",
        "action": "tokentx",
        "address": POOL_ADDRESS,
        "startblock": start_block,
        "endblock": end_block,
        "sort": "asc",
        "apikey": API_KEY
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url=ETHERSCAN_API_URL, params=params)
        txns = response.json()["result"]
        transactions.extend([
            Transaction(
                block_number=txn["blockNumber"], 
                time_stamp=txn["timeStamp"], 
                hash=txn["hash"], 
                gas_price=txn["gasPrice"], 
                gas_used=txn["gasUsed"]) 
                for txn in txns]
            )

        return transactions


# async def fetch_single_transaction(txn_hash: str) -> Transaction:
#     params = {
#         "module": "proxy",
#         "action": "eth_getTransactionByHash",
#         "txhash": txn_hash,
#         "apikey": API_KEY
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.get(url=ETHERSCAN_API_URL, params=params)
#         return response.json()


# async def fetch_transactions_in_timeperiod(start_timestamp: int, end_timestamp: int) -> list[Transaction]:
#     params = {
#         "module": "account",
#         "action": "tokentx",
#         "address": POOL_ADDRESS,
#         "startblock": 0, 
#         "endblock": 99999999,
#         "sort": "asc",
#         "apikey": API_KEY
#     }
    
#     async with httpx.AsyncClient() as client:
#         response = await client.get(url=ETHERSCAN_API_URL, params=params)
#         txns = response.json()["result"]
#         transactions = [Transaction(**txn) for txn in json.loads(txns)]
#         return transactions


# @app.get("/api/v1/txns")
# async def fetch_all_transactions():
#     start_block = 0
#     end_block = 99_999_999
#     transactions: list[Transaction] = []
#     params = {
#         "module": "account",
#         "action": "tokentx",
#         "address": POOL_ADDRESS,
#         "startblock": start_block, 
#         "endblock": end_block,
#         "sort": "asc",
#         "apikey": API_KEY
#     }
    
#     while start_block < end_block:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(url=ETHERSCAN_API_URL, params=params)

#         if response.status_code != status.HTTP_200_OK:
#             raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No more transactions found")

#         txns = response.json()["result"]
#         transactions.extend([
#             Transaction(
#                 block_number=txn["blockNumber"], 
#                 time_stamp=txn["timeStamp"], 
#                 hash=txn["hash"], 
#                 gas=txn["gas"], 
#                 gas_price=txn["gasPrice"], 
#                 gas_used=txn["gasUsed"]) 
#                 for txn in txns])
#         start_block = transactions[-1].block_number + 1
#         print(f"Fetched {len(transactions)} transactions, continuing from block {start_block}...")
#         print(params)
