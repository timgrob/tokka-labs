from models.transaction import Transaction
from models.time_period import TimePeriod
from collections import defaultdict
from datetime import datetime as dt
from itertools import chain
import bisect


class InMemoryDB:
    def __init__(self) -> None:
        self._hash_to_transaction: dict[str, Transaction] = {}
        self._timestamp_to_transaction: dict[int, list[Transaction]] = defaultdict(list)
        self._sorted_timestamps: list[int] = []

    async def add_txn(self, txn: Transaction) -> bool:
        if txn.hash in self._hash_to_transaction:
            # If transaction hash has already been added, do not take any actions
            return False

        self._hash_to_transaction[txn.hash] = txn

        # In case two transactions happen at the same time, append them to list
        self._timestamp_to_transaction[txn.time_stamp].append(txn)

        # The transactions should come in in order
        self._sorted_timestamps.append(txn.time_stamp)

        return True

    async def add_txns(self, txns: list[Transaction]) -> bool:
        for txn in txns:
            await self.add_txn(txn)

    async def find_all_transactions(self) -> list[Transaction]:
        return list(chain(*[self._timestamp_to_transaction[ts] for ts in self._sorted_timestamps]))

    async def find_txn_by_hash(self, txn_hash: str) -> Transaction:
        if txn_hash not in self._hash_to_transaction:
            raise KeyError(f"Transaction with hash={txn_hash} not found")

        return self._hash_to_transaction[txn_hash]

    async def find_txn_in_time_period(self, time_period: TimePeriod) -> list[Transaction]:
        if time_period.start_timestamp > max(self._sorted_timestamps):
            raise ValueError("No transaction in time period found")

        start_timestamp = time_period.start_timestamp
        if time_period.end_timestamp is None:
            end_timestamp = int(dt.now().timestamp())

        left_index = bisect.bisect_left(self._sorted_timestamps, start_timestamp)
        right_index = bisect.bisect_right(self._sorted_timestamps, end_timestamp)

        time_span = self._sorted_timestamps[left_index:right_index]
        txns = list(chain(*[self._timestamp_to_transaction[ts] for ts in time_span]))

        return txns

    async def clear(self):
        self._hash_to_transaction = {}
        self._timestamp_to_transaction = defaultdict(list)
        self._sorted_timestamps = []

    def has_txn_hash(self, txn_hash: str) -> bool:
        return txn_hash in self._hash_to_transaction

