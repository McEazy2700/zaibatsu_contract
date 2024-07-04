import random
import secrets
from datetime import datetime, timedelta
from typing import Literal

import pytest
from algokit_utils import Account, TransactionParameters
from algosdk import atomic_transaction_composer, transaction
from algosdk.v2client.algod import AlgodClient
from folksfeedsdk.constants import TestnetAssetId

# from folksfeedsdk.folks_feed_client import FolksFeedClient
from smart_contracts.artifacts.zaibatsu_service.client import (
    CompleteLoanArgs,
    LoanDetails,
    ZaibatsuServiceClient,
)

from .utils import (
    calc_amount_plus_fee,
    encode_id_to_base64,
)

FOLKS_FEED_ORACLE_TESTNET_ID = 159512493


def generate_loan_details(creator_account: Account) -> LoanDetails:
    loan_key = secrets.token_hex(4)
    completion_timestamp = round((datetime.now() + timedelta(weeks=52)).timestamp())
    collateral_amt = 16000

    loan_details = LoanDetails(
        loan_key=loan_key,
        loan_type="",
        principal_asset_id=TestnetAssetId.USDC,
        collateral_asset_id=TestnetAssetId.USDt,
        tenure=6,
        interest_asset_amount=200,
        principal_asset_amount=500,
        collateral_asset_amount=collateral_amt,
        early_payment_penalty_amount=20,
        payment_rounds=2,
        payment_completion_timestamp=completion_timestamp,
        borrower=creator_account.address,
        payment_recipients=[],
        principal_paid=False,
        collateral_paid=False,
        completed_payment_rounds=0,
        lender_nft_asser_id=0,
        borrower_nft_asser_id=0,
    )
    return loan_details


@pytest.fixture(scope="session")
def loan_details(
    creator_account: Account,
) -> LoanDetails:
    return generate_loan_details(creator_account=creator_account)


@pytest.fixture(scope="session")
def pool_loan_details(
    creator_account: Account,
) -> LoanDetails:
    return generate_loan_details(creator_account=creator_account)


# @pytest.mark.skip()
def test_update(zaibatsu_service_client: ZaibatsuServiceClient) -> None:
    zaibatsu_service_client.update_update()


# @pytest.mark.skip()
def test_opt_contract_into_asset(zaibatsu_service_client: ZaibatsuServiceClient):
    result1 = zaibatsu_service_client.opt_contract_into_asset(asset=TestnetAssetId.USDC)
    result2 = zaibatsu_service_client.opt_contract_into_asset(asset=TestnetAssetId.USDt)
    assert result1.return_value and result2.return_value


def initiate_loan_purchase(
    zaibatsu_service_client: ZaibatsuServiceClient,
    algod_client: AlgodClient,
    creator_account: Account,
    loan_details: LoanDetails,
    loan_type: Literal["P2P", "DAO"],
    payment_recipients: list[tuple[int, str]],
):
    loan_details.loan_type = loan_type
    loan_details.payment_recipients = payment_recipients
    txn_amt = calc_amount_plus_fee(16000)

    sp = algod_client.suggested_params()
    txn = transaction.AssetTransferTxn(
        sender=creator_account.address,
        sp=sp,
        index=TestnetAssetId.USDt,
        receiver=zaibatsu_service_client.app_address,
        amt=txn_amt,
    )
    txn = atomic_transaction_composer.TransactionWithSigner(
        txn=txn, signer=creator_account.signer
    )
    zaibatsu_service_client.initiate_loan_purchase(
        loan_key=loan_details.loan_key.encode(),
        folks_feed_oracle=FOLKS_FEED_ORACLE_TESTNET_ID,
        loan_details=loan_details,
        txn=txn,
        transaction_parameters=TransactionParameters(
            boxes=[(zaibatsu_service_client.app_id, loan_details.loan_key.encode())]
        ),
    )


# @pytest.mark.skip()
def test_initiate_p2p_loan_purchase(
    zaibatsu_service_client: ZaibatsuServiceClient,
    algod_client: AlgodClient,
    creator_account: Account,
    test_account: Account,
    loan_details: LoanDetails,
) -> None:
    initiate_loan_purchase(
        zaibatsu_service_client=zaibatsu_service_client,
        algod_client=algod_client,
        creator_account=creator_account,
        loan_details=loan_details,
        loan_type="P2P",
        payment_recipients=[(100 * 100, test_account.address)],
    )


# @pytest.mark.skip()
def test_initiate_non_p2p_loan_purchase(
    zaibatsu_service_client: ZaibatsuServiceClient,
    algod_client: AlgodClient,
    creator_account: Account,
    test_account: Account,
    pool_loan_details: LoanDetails,
) -> None:
    initiate_loan_purchase(
        zaibatsu_service_client=zaibatsu_service_client,
        algod_client=algod_client,
        creator_account=creator_account,
        loan_details=pool_loan_details,
        loan_type="DAO",
        payment_recipients=[
            (100 * 50, test_account.address),
            (100 * 50, creator_account.address),
        ],
    )


# @pytest.mark.skip()
def test_complete_p2p_loan_purchase(
    algod_client: AlgodClient,
    zaibatsu_service_client: ZaibatsuServiceClient,
    test_account: Account,
    creator_account: Account,
    loan_details: LoanDetails,
) -> None:
    sp = algod_client.suggested_params()
    principal_amt = 500
    txn_amt = calc_amount_plus_fee(principal_amt)

    txn = transaction.AssetTransferTxn(
        sender=test_account.address,
        sp=sp,
        index=TestnetAssetId.USDC,
        receiver=zaibatsu_service_client.app_address,
        amt=txn_amt,
    )
    txn = atomic_transaction_composer.TransactionWithSigner(
        txn=txn, signer=test_account.signer
    )

    loan_unit_id = random.randint(1, 1000000)
    encoded_loan_unit_id = encode_id_to_base64(loan_unit_id)

    complete_args = CompleteLoanArgs(
        loan_unit_name=encoded_loan_unit_id,
        lender_nft_image_url="",
        borrower_nft_image_url="",
        loan_hash=secrets.token_hex(16),
    )
    zaibatsu_service_client.complete_p2p_loan_purchase(
        loan_key=loan_details.loan_key.encode(),
        completion_args=complete_args,
        txn=txn,
        principal_asset=TestnetAssetId.USDC,
        borrower=creator_account.address,
        transaction_parameters=TransactionParameters(
            boxes=[(zaibatsu_service_client.app_id, loan_details.loan_key.encode())]
        ),
    )


# @pytest.mark.skip()
def test_complete_non_p2p_loan_purchase(
    zaibatsu_service_client: ZaibatsuServiceClient,
    creator_account: Account,
    pool_loan_details: LoanDetails,
) -> None:
    loan_unit_id = random.randint(1, 1000000)
    encoded_loan_unit_id = encode_id_to_base64(loan_unit_id)

    complete_args = CompleteLoanArgs(
        loan_unit_name=encoded_loan_unit_id,
        lender_nft_image_url="",
        borrower_nft_image_url="",
        loan_hash=secrets.token_hex(16),
    )
    zaibatsu_service_client.complete_non_p2p_loan_purchase(
        loan_key=pool_loan_details.loan_key.encode(),
        completion_args=complete_args,
        principal_asset=TestnetAssetId.USDC,
        borrower=creator_account.address,
        transaction_parameters=TransactionParameters(
            boxes=[
                (zaibatsu_service_client.app_id, pool_loan_details.loan_key.encode())
            ]
        ),
    )


@pytest.fixture(scope="session")
def repayment_key() -> str:
    loan_key = secrets.token_hex(4)
    return loan_key


# @pytest.mark.skip()
def test_initiate_p2p_loan_repayment(
    zaibatsu_service_client: ZaibatsuServiceClient,
    creator_account: Account,
    algod_client: AlgodClient,
    loan_details: LoanDetails,
    repayment_key: str,
) -> None:
    payment_amount = (
        loan_details.interest_asset_amount + loan_details.principal_asset_amount
    ) // loan_details.payment_rounds
    amount_plus_fee = calc_amount_plus_fee(payment_amount)

    sp = algod_client.suggested_params()
    txn = transaction.AssetTransferTxn(
        sender=creator_account.address,
        sp=sp,
        index=loan_details.principal_asset_id,
        receiver=zaibatsu_service_client.app_address,
        amt=amount_plus_fee,
    )
    txn = atomic_transaction_composer.TransactionWithSigner(
        txn=txn, signer=creator_account.signer
    )
    zaibatsu_service_client.initiate_loan_repayment(
        loan_key=loan_details.loan_key.encode(),
        repayment_key=repayment_key,
        txn=txn,
        transaction_parameters=TransactionParameters(
            boxes=[
                (zaibatsu_service_client.app_id, loan_details.loan_key.encode()),
                (zaibatsu_service_client.app_id, repayment_key.encode()),
            ]
        ),
    )


# @pytest.mark.skip()
# def test_delete(zaibatsu_service_client: ZaibatsuServiceClient) -> None:
#     zaibatsu_service_client.delete_delete()
