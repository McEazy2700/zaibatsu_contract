from pathlib import Path

import pytest
from algokit_utils import (
    Account,
    get_algod_client,
    get_indexer_client,
)
from algokit_utils.config import config
from algosdk import mnemonic
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from artifacts.zaibatsu_loan.client import ZaibatsuLoanClient
from dotenv import load_dotenv
from folksfeedsdk.folks_feed_client import FolksFeedClient

from smart_contracts.artifacts.zaibatsu_auth_and_dao.client import (
    ZaibatsuAuthAndDaoClient,
)
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


@pytest.fixture(scope="session")
def ffo_client(algod_client: AlgodClient, indexer_client: IndexerClient) -> FolksFeedClient:
    return FolksFeedClient(algod_client=algod_client, indexer_client=indexer_client, app_id=159512493)


@pytest.fixture(scope="session")
def zaibatsu_loan_client(algod_client: AlgodClient, creator_account: Account) -> ZaibatsuLoanClient:
    config.configure(
        debug=True,
        # trace_all=True,
    )

    client = ZaibatsuLoanClient(
        algod_client,
        app_id=672950882,
        signer=creator_account.signer,
    )
    return client


@pytest.fixture(scope="session")
def zaibatsu_auth_client(
    algod_client: AlgodClient,
    creator_account: Account,
) -> ZaibatsuAuthAndDaoClient:
    config.configure(
        debug=True,
        # trace_all=True,
    )

    client = ZaibatsuAuthAndDaoClient(
        algod_client,
        app_id=694505037,
        signer=creator_account.signer,
    )

    # client.deploy(
    #     version="0.1",
    #     signer=creator_account.signer,
    #     on_schema_break=algokit_utils.OnSchemaBreak.ReplaceApp,
    #     on_update=algokit_utils.OnUpdate.ReplaceApp,
    #     create_args=DeployCreate[CreateArgs](args=CreateArgs()),
    #     update_args=Deploy[UpdateArgs](args=UpdateArgs()),
    #     delete_args=Deploy[DeleteArgs](args=DeleteArgs()),
    # )
    return client
