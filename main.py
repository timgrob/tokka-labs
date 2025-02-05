from fastapi import FastAPI, HTTPException, status
from sqlmodel import SQLModel, Session, create_engine, select
from config import DATABASE_URL
from models.time_period import TimePeriod
from models.transaction import Transaction
from services.etherscan import fetch_all_transactions
from services.binance import fetch_ethusdt_price_at_timestamp, fetch_ethusdt_prices_at_timestamps
import numpy as np


# FastAPI App
app = FastAPI(title="Uniswap Transactions API", description="Tokka Labs Coding Challenge")

# Database
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})


@app.on_event("startup")
async def startup_event():
    SQLModel.metadata.create_all(engine)

    txns = await fetch_all_transactions()
    unique_txns = set(txns)
    with Session(engine) as session:
        session.add_all(unique_txns)
        session.commit()

    # TODO: Continuously fetch new transactions


@app.on_event("shutdown")
async def shutdown_event():
    SQLModel.metadata.drop_all(engine)


@app.get("/")
def index():
    # This is a helper endpoint to verify that the server is running
    return {"status": "server is running"}


@app.get("/api/v1/txns")
async def all_transactions():
    with Session(engine) as session:
        query = select(Transaction)
        results = session.exec(query)
        txns = results.all()

    return {
        "status": status.HTTP_200_OK,
        "message": "OK",
        "number_of_transactions": len(txns),
        "result": txns
        }


@app.get("/api/v1/txns/{txn_hash}")
async def transactions_by_hash(txn_hash: str):
    try: 
        with Session(engine) as session:
            query = select(Transaction).where(Transaction.hash == txn_hash)
            results = session.exec(query)
            txn = results.one()
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Multiple transactions found with hash={txn_hash}")

    return {
        "status": status.HTTP_200_OK,
        "message": "OK",
        "number_of_transactions": 1,
        "result": txn
        }


@app.post("/api/v1/txns")
async def transactions_in_time_period(time_period: TimePeriod):
    with Session(engine) as session:
        query = select(Transaction).where(Transaction.time_stamp >= time_period.start_timestamp, Transaction.time_stamp <= time_period.end_timestamp)
        results = session.exec(query)
        txns = results.all()

    return {
        "status": status.HTTP_200_OK,
        "message": "OK",
        "number_of_transactions": len(txns),
        "result": txns
    }


@app.get("/api/v1/txns-fees/{txn_hash}")
async def transaction_fees_by_hash(txn_hash: str):
    try: 
        with Session(engine) as session:
            query = select(Transaction).where(Transaction.hash == txn_hash)
            results = session.exec(query)
            txn = results.one()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction not found with hash={txn_hash}")

    try:
        price_ethusdt = await fetch_ethusdt_price_at_timestamp(txn.time_stamp)
        gas_fee_usdt = txn.gas_fee * price_ethusdt
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Price information for ETH/USDT could not be fetched")

    return {
        "status": status.HTTP_200_OK,
        "message": "OK",
        "gas_fee_usdt": gas_fee_usdt,
    }


@app.post("/api/v1/txns-fees")
async def transaction_fees_in_time_period(time_period: TimePeriod):
    with Session(engine) as session:
        query = select(Transaction).where(Transaction.time_stamp >= time_period.start_timestamp, Transaction.time_stamp <= time_period.end_timestamp)
        results = session.exec(query)
        txns = results.all()

    if len(txns) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No txns found in time span")

    timestamps = [txn.time_stamp for txn in txns]
    gas_fees = [txn.gas_fee for txn in txns]
    prices_ethusdt = await fetch_ethusdt_prices_at_timestamps(timestamps)
    gas = np.array(gas_fees)
    prices = np.array(prices_ethusdt)
    gas_fee_usdt = np.sum(gas * prices)

    return {
        "status": status.HTTP_200_OK,
        "message": "OK",
        "gas_fee_usdt": gas_fee_usdt,
    }
