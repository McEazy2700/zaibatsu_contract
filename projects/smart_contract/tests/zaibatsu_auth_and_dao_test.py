import pytest
from algokit_utils import Account, TransactionParameters
from algosdk import atomic_transaction_composer, transaction
from algosdk.v2client.algod import AlgodClient
from folksfeedsdk.constants import TestnetAssetId

from smart_contracts.artifacts.zaibatsu_auth_and_dao.client import (
    ZaibatsuAuthAndDaoClient,
)
from smart_contracts.artifacts.zaibatsu_loan.client import ZaibatsuLoanClient

FOLKS_FEED_ORACLE_TESTNET_ID = 159512493


# @pytest.mark.skip()
def test_update(zaibatsu_auth_client: ZaibatsuAuthAndDaoClient) -> None:
    zaibatsu_auth_client.update_update()


@pytest.fixture(scope="session")
def zai(zaibatsu_auth_client: ZaibatsuAuthAndDaoClient) -> int:
    result = zaibatsu_auth_client.create_zaibatsu_token(
        transaction_parameters=TransactionParameters(
            boxes=[(zaibatsu_auth_client.app_id, b"ZAI")]
        )
    )
    return result.return_value


# @pytest.mark.skip()
def test_opt_contract_into_asset(zaibatsu_auth_client: ZaibatsuAuthAndDaoClient):
    result1 = zaibatsu_auth_client.opt_contract_into_asset(asset=TestnetAssetId.USDC)
    result2 = zaibatsu_auth_client.opt_contract_into_asset(asset=TestnetAssetId.USDt)
    assert result1.return_value and result2.return_value


# @pytest.mark.skip()
def test_set_service_contract_address(
    zaibatsu_auth_client: ZaibatsuAuthAndDaoClient,
    zaibatsu_loan_client: ZaibatsuLoanClient,
):
    zaibatsu_auth_client.set_service_contract_address(
        address=zaibatsu_loan_client.app_address
    )


# @pytest.mark.skip()
def test_fund_pool(
    zaibatsu_auth_client: ZaibatsuAuthAndDaoClient,
    zaibatsu_loan_client: ZaibatsuLoanClient,
    algod_client: AlgodClient,
    creator_account: Account,
):
    sp = algod_client.suggested_params()
    asset_amount = 2000
    txn = transaction.AssetTransferTxn(
        sp=sp,
        amt=asset_amount,
        sender=creator_account.address,
        receiver=zaibatsu_loan_client.app_address,
        index=TestnetAssetId.USDC,
    )
    txn = atomic_transaction_composer.TransactionWithSigner(
        txn=txn, signer=creator_account.signer
    )

    result = zaibatsu_auth_client.fund_pool(
        txn=txn,
        fund_amount=asset_amount,
        folks_feed_oracle=FOLKS_FEED_ORACLE_TESTNET_ID,
        transaction_parameters=TransactionParameters(
            boxes=[(zaibatsu_auth_client.app_id, b"ZAI")]
        ),
    )
    print(result.return_value)
