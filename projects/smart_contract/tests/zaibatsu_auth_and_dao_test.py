import random
import secrets
from dataclasses import dataclass

import pytest
from algokit_utils import Account, TransactionParameters
from algosdk import atomic_transaction_composer, transaction
from algosdk.v2client.algod import AlgodClient
from folksfeedsdk.constants import TestnetAssetId

from smart_contracts.artifacts.zaibatsu_auth_and_dao.client import (
    PoolInfo,
    ZaibatsuAuthAndDaoClient,
)
from smart_contracts.artifacts.zaibatsu_loan.client import ZaibatsuLoanClient
from tests.utils import calc_amount_plus_fee, get_multiplier_for_decimal_places

FOLKS_FEED_ORACLE_TESTNET_ID = 159512493


@dataclass()
class PoolArgs:
    pool_key: str
    image_url: str
    token_unit_name: str
    token_asset_name: str
    max_contributors: int


@pytest.fixture(scope="session")
def pool_args() -> PoolArgs:
    return PoolArgs(
        image_url="",
        pool_key=secrets.token_hex(5),
        token_unit_name=secrets.token_hex(2),
        token_asset_name=secrets.token_hex(4),
        max_contributors=random.randint(1, 100),
    )


# @pytest.mark.skip()
def test_update(zaibatsu_auth_client: ZaibatsuAuthAndDaoClient) -> None:
    zaibatsu_auth_client.update_update()


def test_opt_contract_into_asset(zaibatsu_auth_client: ZaibatsuAuthAndDaoClient):
    result1 = zaibatsu_auth_client.opt_contract_into_asset(asset=TestnetAssetId.USDC)
    result2 = zaibatsu_auth_client.opt_contract_into_asset(asset=TestnetAssetId.USDt)
    assert result1.return_value and result2.return_value


def test_set_service_contract_address(
    zaibatsu_auth_client: ZaibatsuAuthAndDaoClient,
    zaibatsu_loan_client: ZaibatsuLoanClient,
):
    zaibatsu_auth_client.set_service_contract_address(
        address=zaibatsu_loan_client.app_address
    )


# @pytest.mark.skip()
@pytest.fixture(scope="session")
def test_authorize_pool_creation(
    zaibatsu_auth_client: ZaibatsuAuthAndDaoClient,
    zaibatsu_loan_client: ZaibatsuLoanClient,
    algod_client: AlgodClient,
    creator_account: Account,
    pool_args: PoolArgs,
    # ffo_client: FolksFeedClient,
) -> PoolInfo:
    # asset_info = ffo_client.get_asset_info(TestnetAssetId.USDC)
    # asset_amount = math.ceil((1 * get_multiplier_for_decimal_places(6)) / asset_info.price)
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
    txn = atomic_transaction_composer.TransactionWithSigner(
        txn=txn, signer=creator_account.signer
    )
    result = zaibatsu_auth_client.authorize_pool_creation(
        txn=txn,
        pool_key=pool_args.pool_key,
        image_url=pool_args.image_url,
        token_unit_name=pool_args.token_unit_name,
        max_contributors=pool_args.max_contributors,
        token_asset_name=pool_args.token_asset_name,
        folks_feed_oracle=FOLKS_FEED_ORACLE_TESTNET_ID,
        asset_decimals_multiplier=get_multiplier_for_decimal_places(6),
        transaction_parameters=TransactionParameters(
            boxes=[(zaibatsu_auth_client.app_id, pool_args.pool_key)]
        ),
    )
    print(result.return_value)
    return result.return_value


def test_optin_pool_asset(
    zaibatsu_auth_client: ZaibatsuAuthAndDaoClient,
    algod_client: AlgodClient,
    creator_account: Account,
    test_authorize_pool_creation: PoolInfo,
):
    sp = algod_client.suggested_params()
    optin_txn = transaction.AssetTransferTxn(
        sp=sp,
        amt=0,
        sender=creator_account.address,
        receiver=creator_account.address,
        index=test_authorize_pool_creation.pool_asset_id,
    )
    optin_txn = atomic_transaction_composer.TransactionWithSigner(
        txn=optin_txn, signer=creator_account.signer
    )
    zaibatsu_auth_client.optin_pool_asset(
        optin_txn=optin_txn,
        pool_key=test_authorize_pool_creation.pool_key,
        transaction_parameters=TransactionParameters(
            boxes=[(zaibatsu_auth_client.app_id, test_authorize_pool_creation.pool_key)]
        ),
    )


# @pytest.mark.skip()
def test_fund_pool(
    zaibatsu_auth_client: ZaibatsuAuthAndDaoClient,
    zaibatsu_loan_client: ZaibatsuLoanClient,
    algod_client: AlgodClient,
    creator_account: Account,
    pool_args: PoolArgs,
    test_authorize_pool_creation: PoolInfo,
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

    zaibatsu_auth_client.fund_pool(
        txn=txn,
        pool_asset=test_authorize_pool_creation.pool_asset_id,
        pool_key=pool_args.pool_key,
        fund_amount=asset_amount,
        user_account=creator_account.address,
        folks_feed_oracle=FOLKS_FEED_ORACLE_TESTNET_ID,
        asset_decimals_multiplier=get_multiplier_for_decimal_places(6),
        transaction_parameters=TransactionParameters(
            boxes=[(zaibatsu_auth_client.app_id, pool_args.pool_key)]
        ),
    )
