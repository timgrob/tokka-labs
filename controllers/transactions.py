from models.transaction import Transaction
from models.time_period import TimePeriod
from datetime import datetime as dt


def find_transactions_by_hash(txns: list[Transaction], txn_hash: str) -> list[Transaction]:
    return [txn for txn in txns if txn.hash == txn_hash]


def find_transactions_in_time_period(txns: list[Transaction], time_period: TimePeriod) -> list[Transaction]:
    if not time_period.end_timestamp:
        end_timestamp = int(dt.now().timestamp()*1E3)   # convert to miliseconds
    start_timestamp = time_period.start_timestamp

    return [txn for txn in txns if txn.time_stamp >= start_timestamp and txn.time_stamp <= end_timestamp]

