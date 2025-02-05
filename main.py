from fastapi import FastAPI, HTTPException, status, Depends
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

# Dependency
def get_session():
    with Session(engine) as session:
        yield session


@app.on_event("startup")
async def startup_event():
    SQLModel.metadata.create_all(engine)

    txns = await fetch_all_transactions()

    with Session(engine) as session:
        session.add_all(txns)
        session.commit()

    # TODO: Continuously fetch new transactions


@app.on_event("shutdown")
async def shutdown_event():
    SQLModel.metadata.drop_all(engine)


@app.get("/")
def index():
    # This is a helper endpoint to verify that the server is running
    return {"status": "server is running"}


@app.post("/api/v1/txn/")
async def create_transaction(txn: Transaction, session: Session = Depends(get_session)) -> Transaction:
    session.add(txn)
    session.commit()
    session.refresh()

    return {
        "status": status.HTTP_200_OK,
        "message": "OK",
        "result": txn
        }


@app.get("/api/v1/txns")
async def all_transactions(session: Session = Depends(get_session)):
    try:
        query = select(Transaction)
        results = session.exec(query)
        txns = results.all()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Transactions could not be fetched from database")

    return {
        "status": status.HTTP_200_OK,
        "message": "OK",
        "number_of_transactions": len(txns),
        "result": txns
        }


@app.get("/api/v1/txns/{txn_hash}")
async def transactions_by_hash(txn_hash: str, session: Session = Depends(get_session)):
    try:
        query = select(Transaction).where(Transaction.hash == txn_hash)
        results = session.exec(query)
        txns = results.all()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Transactions could not be fetched from database")

    if not txns:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction not found")

    return {
        "status": status.HTTP_200_OK,
        "message": "OK",
        "number_of_transactions": len(txns),
        "result": txns
        }


@app.post("/api/v1/txns")
async def transactions_in_time_span(time_period: TimePeriod, session: Session = Depends(get_session)):
    try: 
        query = select(Transaction).where(Transaction.time_stamp >= time_period.start_timestamp, Transaction.time_stamp <= time_period.end_timestamp)
        results = session.exec(query)
        txns = results.all()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Transactions could not be fetched from database")

    if not txns:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No transactions found in time span")

    return {
        "status": status.HTTP_200_OK,
        "message": "OK",
        "number_of_transactions": len(txns),
        "result": txns
    }


@app.get("/api/v1/txn-fees/{txn_hash}")
async def transaction_fees_by_hash(txn_hash: str, session: Session = Depends(get_session)):
    try: 
        query = select(Transaction).where(Transaction.hash == txn_hash)
        results = session.exec(query)
        txns = results.all()
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Multiple transactions found")

    if not txns:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No transaction found")

    # Some transactions have the same hash and thus multiple transactions can be returned. 
    # Yet, the transaction fees are the same. Thus, take the first found transaction only
    if len(txns) > 0:
        txn = txns[0]

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


@app.post("/api/v1/txn-fees")
async def transaction_fees_in_time_period(time_period: TimePeriod, session: Session = Depends(get_session)):
    query = select(Transaction).where(Transaction.time_stamp >= time_period.start_timestamp, Transaction.time_stamp <= time_period.end_timestamp)
    results = session.exec(query)
    txns = results.all()

    if not txns:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No transactions found in time span")

    # Remove duplicate transactions with the same hash key
    if len(txns) > 0:
        txns_unique: set[Transaction] = set(txns)

    print(f"======== length: {len(txns)}")
    print(f"======== length: {len(txns_unique)}")

    timestamps = [txn.time_stamp for txn in txns_unique]
    gas_fees = [txn.gas_fee for txn in txns_unique]
    prices_ethusdt = await fetch_ethusdt_prices_at_timestamps(timestamps)
    gas = np.array(gas_fees)
    prices = np.array(prices_ethusdt)
    gas_fee_usdt = np.sum(gas * prices)

    return {
        "status": status.HTTP_200_OK,
        "message": "OK",
        "gas_fee_usdt": gas_fee_usdt,
    }
