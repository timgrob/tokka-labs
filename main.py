from fastapi import FastAPI, HTTPException, status
from models.time_period import TimePeriod
from databases.in_memory_db import InMemoryDB
from services.etherscan import fetch_all_transactions
from services.binance import fetch_ethusdt_price_at_timestamp, fetch_ethusdt_prices_at_timestamps
import numpy as np


app = FastAPI(title="Uniswap Transactions API", description="Tokka Labs Coding Challenge")
db = InMemoryDB()


@app.on_event("startup")
async def startup_event():
    txns = await fetch_all_transactions()
    await db.add_txns(txns)
    # TODO: Continuously fetch new transactions


@app.on_event("shutdown")
async def shutdown_event():
    await db.clear()


@app.get("/")
def index():
    # This is a helper endpoint to verify that the server is running
    return {"status": "server is running"}


@app.get("/api/v1/txns")
async def all_transactions():
    try: 
        txns = await db.find_all_transactions()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Transactions could not be fetched")

    return {
        "status": status.HTTP_200_OK,
        "message": "OK",
        "number_of_transactions": len(txns),
        "result": txns
        }


@app.get("/api/v1/txns/{txn_hash}")
async def transactions_by_hash(txn_hash: str):
    if not db.has_txn_hash(txn_hash):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    try:
        txn = await db.find_txn_by_hash(txn_hash)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Transaction could not be fetched")

    return {
        "status": status.HTTP_200_OK,
        "message": "OK",
        "number_of_transactions": 1,
        "result": txn
        }


@app.post("/api/v1/txns")
async def transactions_in_time_period(time_period: TimePeriod):
    try:
        txns = await db.find_txn_in_time_period(time_period)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Start timestamp must be before end timestamp")
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Transactions in {time_period=} could not be fetched")

    return {
        "status": status.HTTP_200_OK,
        "message": "OK",
        "number_of_transactions": len(txns),
        "result": txns
    }


@app.get("/api/v1/txns-fees/{txn_hash}")
async def transaction_fees_by_hash(txn_hash: str):
    try:
        txn = await db.find_txn_by_hash(txn_hash)
        price_ethusdt = await fetch_ethusdt_price_at_timestamp(txn.time_stamp)
        gas_fee_usdt = txn.gas_fee * price_ethusdt
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Gas price in USDT could not be calculated")

    
    return {
        "status": status.HTTP_200_OK,
        "message": "OK",
        "gas_fee_usdt": gas_fee_usdt,
    }


@app.post("/api/v1/txns-fees")
async def transaction_fees_in_time_period(time_period: TimePeriod):
    try:
        txns = await db.find_txn_in_time_period(time_period)
        timestamps = [txn.time_stamp for txn in txns]
        gas_fees = [txn.gas_fee for txn in txns]
        prices_ethusdt = await fetch_ethusdt_prices_at_timestamps(timestamps)
        gas = np.array(gas_fees)
        prices = np.array(prices_ethusdt)
        gas_fee_usdt = np.sum(gas * prices)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Gas price in USDT for timespan could not be calculated")


    return {
        "status": status.HTTP_200_OK,
        "message": "OK",
        "gas_fee_usdt": gas_fee_usdt,
    }
