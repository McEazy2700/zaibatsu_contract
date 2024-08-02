import pytest
from algokit_utils import Account, TransactionParameters
from algosdk import atomic_transaction_composer, transaction
from algosdk.v2client.algod import AlgodClient
from folksfeedsdk.constants import TestnetAssetId

from smart_contracts.artifacts.zaibatsu_auth_and_dao.client import (
    ZaibatsuAuthAndDaoClient,
)
from smart_contracts.artifacts.zaibatsu_loan.client import ZaibatsuLoanClient
from tests.utils import calc_amount_plus_fee

FOLKS_FEED_ORACLE_TESTNET_ID = 159512493


# @pytest.mark.skip()
def test_update(zaibatsu_auth_client: ZaibatsuAuthAndDaoClient) -> None:
    zaibatsu_auth_client.update_update()


@pytest.fixture(scope="session")
def zai(zaibatsu_auth_client: ZaibatsuAuthAndDaoClient) -> int:
    result = zaibatsu_auth_client.create_zaibatsu_token(
        transaction_parameters=TransactionParameters(boxes=[(zaibatsu_auth_client.app_id, b"zai")])
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
    zaibatsu_auth_client.set_service_contract_address(address=zaibatsu_loan_client.app_address)


# @pytest.mark.skip()
def test_authorize_pool_creation(
    zaibatsu_auth_client: ZaibatsuAuthAndDaoClient,
    zaibatsu_loan_client: ZaibatsuLoanClient,
    algod_client: AlgodClient,
    creator_account: Account,
) -> None:
    asset_amount = 10000
    amt_plus_fee = calc_amount_plus_fee(asset_amount)

    sp = algod_client.suggested_params()
    txn = transaction.AssetTransferTxn(
        sp=sp,
        amt=amt_plus_fee,
        sender=creator_account.address,
        receiver=zaibatsu_loan_client.app_address,
        index=TestnetAssetId.USDC,
    )
    txn = atomic_transaction_composer.TransactionWithSigner(txn=txn, signer=creator_account.signer)
    result = zaibatsu_auth_client.authorize_pool_creation(
        txn=txn,
        folks_feed_oracle=FOLKS_FEED_ORACLE_TESTNET_ID,
    )


# @pytest.mark.skip()
def test_fund_pool(
    zaibatsu_auth_client: ZaibatsuAuthAndDaoClient,
    zaibatsu_loan_client: ZaibatsuLoanClient,
    algod_client: AlgodClient,
    zai: int,
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
    txn = atomic_transaction_composer.TransactionWithSigner(txn=txn, signer=creator_account.signer)

    result = zaibatsu_auth_client.fund_pool(
        txn=txn,
        zai=zai,
        fund_amount=asset_amount,
        user_account=creator_account.address,
        folks_feed_oracle=FOLKS_FEED_ORACLE_TESTNET_ID,
        transaction_parameters=TransactionParameters(boxes=[(zaibatsu_auth_client.app_id, b"zai")]),
    )
    print(result.return_value)
