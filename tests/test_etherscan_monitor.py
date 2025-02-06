from models.transaction import Transaction
from services.etherscan_monitor import EtherscanMonitor
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
from main import get_session
from config import POOL_ADDRESS
from main import app, get_session
import pytest
import os


load_dotenv()

        
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, echo=True, connect_args={"check_same_thread": False}, poolclass=StaticPool)


def get_test_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = get_test_session


@pytest.fixture
def api_key() -> str:
    return os.getenv('ETHERSCAN_API_KEY')


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.mark.asyncio
async def test_retrieve_transactions(api_key: str):
    monitor = EtherscanMonitor(api_key, engine)
    response = await monitor.retrieve_transactions(POOL_ADDRESS, block_limit=5)

    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], Transaction)


@pytest.mark.asyncio
async def test_fetch_transactions_block_batch(api_key: str):
    start_block = 12376729
    end_block = 12376891
    monitor = EtherscanMonitor(api_key, engine)
    response = await monitor.fetch_transactions_batch(POOL_ADDRESS, start_block, end_block)

    assert isinstance(response, list)
    assert len(response) > 0
    assert len(response) == 4
    assert isinstance(response[0], Transaction)
