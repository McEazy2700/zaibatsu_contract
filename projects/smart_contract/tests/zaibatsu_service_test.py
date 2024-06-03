import secrets
from datetime import datetime, timedelta

import pytest
from algokit_utils import Account, TransactionParameters
from algokit_utils.config import config
from algosdk import atomic_transaction_composer, transaction
from algosdk.v2client.algod import AlgodClient
from folksfeedsdk.constants import TestnetAssetId

from smart_contracts.artifacts.zaibatsu_service.client import (
    LoanDetails,
    ZaibatsuServiceClient,
)

FOLKS_FEED_ORACLE_TESTNET_ID = 159512493


@pytest.fixture(scope="session")
def zaibatsu_service_client(algod_client: AlgodClient, creator_account: Account) -> ZaibatsuServiceClient:
    config.configure(
        debug=True,
        # trace_all=True,
    )

    client = ZaibatsuServiceClient(
        algod_client,
        app_id=672950882,
        signer=creator_account.signer,
    )

    # client.deploy(
    #     version="0.2",
    #     signer=creator_account.signer,
    #     on_schema_break=algokit_utils.OnSchemaBreak.ReplaceApp,
    #     on_update=algokit_utils.OnUpdate.ReplaceApp,
    #     create_args=DeployCreate[CreateArgs](args=CreateArgs()),
    #     update_args=Deploy[UpdateArgs](args=UpdateArgs()),
    #     delete_args=Deploy[DeleteArgs](args=DeleteArgs()),
    # )
    return client


# @pytest.mark.skip()
def test_update(zaibatsu_service_client: ZaibatsuServiceClient) -> None:
    zaibatsu_service_client.update_update()


# @pytest.mark.skip()
def test_says_hello(zaibatsu_service_client: ZaibatsuServiceClient) -> None:
    result = zaibatsu_service_client.hello(name="World")

    assert result.return_value == "Hello, World"


# @pytest.mark.skip()
def test_iniate_p2p_loan_purchase(
    zaibatsu_service_client: ZaibatsuServiceClient,
    algod_client: AlgodClient,
    creator_account: Account,
    test_account: Account,
) -> None:
    loan_key = secrets.token_hex(4)
    completion_timestamp = round((datetime.now() + timedelta(weeks=52)).timestamp())
    collateral_amt = 16000

    loan_details = LoanDetails(
        loan_type="P2P",
        tenure=6,
        principal_asset_id=TestnetAssetId.USDC,
        collateral_asset_id=TestnetAssetId.USDt,
        interest_asset_amount=200,
        lend_asset_amount=500,
        collateral_asset_amount=collateral_amt,
        early_payment_penalty_amount=20,
        payment_rounds=2,
        payment_completion_timestamp=completion_timestamp,
        borrower=creator_account.address,
        principal_paid=False,
        collateral_paid=False,
        payment_recipients=[(100 * 100, test_account.address)],
        image_url="",
    )

    sp = algod_client.suggested_params()
    txn = transaction.AssetTransferTxn(
        sender=creator_account.address,
        sp=sp,
        index=TestnetAssetId.USDt,
        receiver=zaibatsu_service_client.app_address,
        amt=collateral_amt,
    )
    txn = atomic_transaction_composer.TransactionWithSigner(txn=txn, signer=creator_account.signer)
    zaibatsu_service_client.iniate_p2p_loan_purchase(
        loan_key=loan_key.encode(),
        folks_feed_oracle=FOLKS_FEED_ORACLE_TESTNET_ID,
        loan_details=loan_details,
        txn=txn,
        transaction_parameters=TransactionParameters(boxes=[(zaibatsu_service_client.app_id, loan_key.encode())]),
    )


# @pytest.mark.skip()
def test_simulate_says_hello_with_correct_budget_consumed(
    zaibatsu_service_client: ZaibatsuServiceClient,
) -> None:
    result = zaibatsu_service_client.compose().hello(name="World").hello(name="Jane").simulate()

    assert result.abi_results[0].return_value == "Hello, World"
    assert result.abi_results[1].return_value == "Hello, Jane"
    assert result.simulate_response["txn-groups"][0]["app-budget-consumed"] < 100


@pytest.mark.skip()
def test_delete(zaibatsu_service_client: ZaibatsuServiceClient) -> None:
    zaibatsu_service_client.delete_delete()
