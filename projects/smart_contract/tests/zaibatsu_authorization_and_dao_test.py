from algokit_utils import Account
from algosdk import atomic_transaction_composer, transaction
from algosdk.v2client.algod import AlgodClient
from artifacts.zaibatsu_service.client import ZaibatsuServiceClient
from folksfeedsdk.constants import TestnetAssetId

from smart_contracts.artifacts.zaibatsu_authorization_and_dao.client import (
    ZaibatsuAuthorizationAndDaoClient as ZaibatsuAuthClient,
)
from tests.utils import calc_amount_plus_fee, get_multiplier_for_decimal_places

FOLKS_FEED_ORACLE_TESTNET_ID = 159512493


# @pytest.mark.skip()
def test_update(zaibatsu_auth_client: ZaibatsuAuthClient) -> None:
    zaibatsu_auth_client.update_update()


def test_opt_contract_into_asset(zaibatsu_auth_client: ZaibatsuAuthClient):
    result1 = zaibatsu_auth_client.opt_contract_into_asset(asset=TestnetAssetId.USDC)
    result2 = zaibatsu_auth_client.opt_contract_into_asset(asset=TestnetAssetId.USDt)
    assert result1.return_value and result2.return_value


def test_set_service_contract_address(
    zaibatsu_auth_client: ZaibatsuAuthClient,
    zaibatsu_service_client: ZaibatsuServiceClient,
):
    zaibatsu_auth_client.set_service_contract_address(address=zaibatsu_service_client.app_address)


# @pytest.mark.skip()
def test_authorize_pool_creation(
    zaibatsu_auth_client: ZaibatsuAuthClient,
    zaibatsu_service_client: ZaibatsuServiceClient,
    algod_client: AlgodClient,
    creator_account: Account,
    # ffo_client: FolksFeedClient,
):
    # asset_info = ffo_client.get_asset_info(TestnetAssetId.USDC)
    # asset_amount = math.ceil((1 * get_multiplier_for_decimal_places(6)) / asset_info.price)
    asset_amount = 10000
    amt_plus_fee = calc_amount_plus_fee(asset_amount)

    sp = algod_client.suggested_params()
    txn = transaction.AssetTransferTxn(
        sp=sp,
        amt=amt_plus_fee,
        sender=creator_account.address,
        receiver=zaibatsu_service_client.app_address,
        index=TestnetAssetId.USDC,
    )
    txn = atomic_transaction_composer.TransactionWithSigner(txn=txn, signer=creator_account.signer)
    result = zaibatsu_auth_client.authorize_pool_creation(
        txn=txn,
        folks_feed_oracle=FOLKS_FEED_ORACLE_TESTNET_ID,
        asset_decimals_multiplier=get_multiplier_for_decimal_places(6),
    )
    assert amt_plus_fee > result.return_value.amount


# @pytest.mark.skip()
def test_fund_pool(
    zaibatsu_auth_client: ZaibatsuAuthClient,
    zaibatsu_service_client: ZaibatsuServiceClient,
    algod_client: AlgodClient,
    creator_account: Account,
):
    sp = algod_client.suggested_params()
    txn = transaction.AssetTransferTxn(
        sp=sp,
        amt=2000,
        sender=creator_account.address,
        receiver=zaibatsu_service_client.app_address,
        index=TestnetAssetId.USDC,
    )
    txn = atomic_transaction_composer.TransactionWithSigner(txn=txn, signer=creator_account.signer)
    result = zaibatsu_auth_client.fund_pool(txn=txn)
    print(result.return_value)
