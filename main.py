from fastapi import FastAPI, HTTPException, status
from models.transaction import Transaction
from models.time_period import TimePeriod
from controllers.transactions import find_transactions_by_hash, find_transactions_in_time_period
from controllers.fees import convert_fees_to_usdt
from config import ETHERSCAN_API_URL, POOL_ADDRESS
from dotenv import load_dotenv
import httpx
import os


load_dotenv()
API_KEY = os.getenv('ETHERSCAN_API_KEY')

app = FastAPI(title="Uniswap Transactions API")

database = {} # TODO: In memory database for testing only


@app.get("/")
def index():
    # This is a helper endpoint to verify that the server is running
    return {"status": "server is running"}


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

@app.get("/api/v1/txns")
async def fetch_all_transactions():
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
        transactions = [
            Transaction(
                block_number=txn["blockNumber"], 
                time_stamp=txn["timeStamp"], 
                hash=txn["hash"], 
                gas=txn["gas"], 
                gas_price=txn["gasPrice"], 
                gas_used=txn["gasUsed"]) 
                for txn in txns]
        
        return transactions


@app.get("/api/v1/txns/{txn_hash}")
async def fetch_transactions_by_hash(txn_hash: str):
    txns = await fetch_all_transactions()
    txns_with_hash = find_transactions_by_hash(txns, txn_hash)

    if len(txns_with_hash) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction not found for hash={txn_hash}")

    return txns_with_hash

@app.post("/api/v1/txns")
async def fetch_transactions_in_time_period(time_period: TimePeriod):
    txns = await fetch_all_transactions()
    txns_in_time_period = find_transactions_in_time_period(txns, time_period)

    if len(txns_in_time_period) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No transactions found in time period; {time_period.start_timestamp=} and {time_period.end_timestamp=}")
    
    return txns_in_time_period


@app.get("/api/v1/gas-fees/{txn_hash_key}")
async def fetch_gas_fees_by_hash(txn_hash_key: str):
    txns_with_hash = await fetch_transactions_by_hash(txn_hash_key)
    gas_fee_usdt = await convert_fees_to_usdt(txns_with_hash)
    total_gas_fee_usdt = sum(gas_fee_usdt)
    
    return {"gas_fee_usdt": total_gas_fee_usdt}


@app.post("/api/v1/gas-fees")
async def fetch_gas_fees_in_time_period(time_period: TimePeriod):
    txns_in_time_period = await fetch_transactions_in_time_period(time_period)
    gas_fee_eth = await convert_fees_to_usdt(txns_in_time_period)
    total_gas_fee_usdt = sum(gas_fee_eth)
    
    return {"gas_fee_usdt": total_gas_fee_usdt}
