import pytest
from models.transaction import Transaction
from services.etherscan_transaction_fetcher import EtherscanTransactionFetcher
from config import POOL_ADDRESS
from dotenv import load_dotenv
import os


load_dotenv()


@pytest.fixture
def api_key() -> str:
    return os.getenv('ETHERSCAN_API_KEY')


@pytest.mark.asyncio
async def test_fetch_all_transactions(api_key: str):
    fetcher = EtherscanTransactionFetcher(api_key)
    response = await fetcher.fetch_all_transactions(POOL_ADDRESS, block_limit=2)

    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], Transaction)


@pytest.mark.asyncio
async def test_fetch_transactions_block_batch(api_key: str):
    start_block = 12376729
    end_block = 12376891
    fetcher = EtherscanTransactionFetcher(api_key)
    response = await fetcher.fetch_transactions_batch(POOL_ADDRESS, start_block, end_block)

    assert isinstance(response, list)
    assert len(response) > 0
    assert len(response) == 4
    assert isinstance(response[0], Transaction)
