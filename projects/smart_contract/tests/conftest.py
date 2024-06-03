from pathlib import Path

import pytest
from algokit_utils import (
    Account,
    AlgoClientConfig,
    get_algod_client,
    get_indexer_client,
)
from algosdk import mnemonic
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from dotenv import load_dotenv

from tests.utils import unwrap_env_var


@pytest.fixture(autouse=True, scope="session")
def environment_fixture() -> None:
    env_path = Path(__file__).parent.parent / ".env.testnet"
    load_dotenv(env_path)


@pytest.fixture(scope="session")
def algod_client() -> AlgodClient:
    client = get_algod_client()
    return client


@pytest.fixture(scope="session")
def indexer_client() -> IndexerClient:
    return get_indexer_client()


@pytest.fixture(scope="session")
def creator_account() -> Account:
    account_mnemonics = unwrap_env_var("DEPLOYER_MNEMONIC")
    return Account(private_key=mnemonic.to_private_key(account_mnemonics))


@pytest.fixture(scope="session")
def test_account() -> Account:
    test_account_mnemonics = unwrap_env_var("TEST_DEPLOYER_MNEMONIC")
    return Account(private_key=mnemonic.to_private_key(test_account_mnemonics))
