from typing import Literal, TypeAlias

from algopy.arc4 import (  # pyright: ignore
    Address,
    Bool,
    DynamicArray,
    String,
    Struct,
    UFixedNxM,
    UInt8,
    UInt64,
)

Decimal: TypeAlias = UFixedNxM[Literal[64], Literal[8]]
AddressArray: TypeAlias = DynamicArray[Address]
A4UInt64: TypeAlias = UInt64


class PaymentReciepient(Struct, kw_only=True):
    payment_percentage: A4UInt64
    recipient_address: Address


PaymentReciepientArray: TypeAlias = DynamicArray[PaymentReciepient]


class PendingLoanRepayment(Struct, kw_only=True):
    key: String
    loan_key: String
    repayment_amount: A4UInt64
    percentage_paid: A4UInt64


class ExecuteLoanRepaymentResponse(Struct, kw_only=True):
    loan_repayment_complete: Bool
    percentage_paid: A4UInt64


class CleanUpLoanRepaymentResponse(Struct, kw_only=True):
    loan_repayment_complete: Bool


class LoanDetails(Struct, kw_only=True):
    loan_key: String
    loan_type: String  # "P2P" | "DAO" | "ZAIBATSU"
    tenure: UInt8
    principal_asset_id: A4UInt64
    collateral_asset_id: A4UInt64
    interest_asset_amount: A4UInt64
    principal_asset_amount: A4UInt64
    collateral_asset_amount: A4UInt64
    early_payment_penalty_amount: A4UInt64
    payment_rounds: UInt8
    payment_completion_timestamp: A4UInt64
    payment_recipients: PaymentReciepientArray
    collateral_paid: Bool
    principal_paid: Bool
    completed_payment_rounds: UInt8
    borrower: Address
    lender_nft_asser_id: A4UInt64
    borrower_nft_asser_id: A4UInt64


class CompleteLoanArgs(Struct, kw_only=True):
    loan_unit_name: String
    lender_nft_image_url: String
    borrower_nft_image_url: String
    loan_hash: String
