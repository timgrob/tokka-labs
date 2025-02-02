from fastapi import FastAPI, HTTPException, status
from dotenv import load_dotenv
from models.transaction import Transaction
from models.time_period import TimePeriod

load_dotenv()


app = FastAPI(title="Uniswap Transactions API")


@app.get("/api/v1/txns/{txn_hash_key}")
def fetch_transaction(txn_hash_key: str):
    if txn_hash_key not in []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction hash key not found")

    # TODO: implement transaction get logic for fetching a single transaction
    return {}

@app.get("/api/v1/txns/")
def fetch_all_transactions():

    # TODO: implement transaction get logic for fetching all stored transactions
    return {}


@app.post("/api/v1/txns/")
def create_transaction(txn: Transaction):
    # TODO: Check if transaction already exisists
    if txn.id in []: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Transaction already exisits")
    
    # TODO: implement transaction logic to create new transaction
    return {}


@app.post("/api/v1/txns/")
def fetch_transactions_in_time_period(time_period: TimePeriod):
    
    # TODO: implement transaction post logic to fetch transactions in time period
    return {}


@app.get("/api/v1/txn-fees/{txn_hash_key}")
def fetch_transaction_fee(txn_hash_key: str):
    txn = fetch_transaction(txn_hash_key)
    
    # TODO: implement logic to fetch transaction fee of single transaction
    return {}


@app.post("/api/v1/txn-fees/")
def fetch_transaction_fee_in_time_period(time_period: TimePeriod):
    
    # TODO: implement transaction post logic to fetch transactions in time period
    return {}
