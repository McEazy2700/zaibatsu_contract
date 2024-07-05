# pyright: reportMissingModuleSource=false
import algopy as ap
from algopy import arc4 as a4
from algopy import gtxn, op

from smart_contracts.zaibatsu_base.contract import ZaibatsuBase
from smart_contracts.zaibatsu_loan.types.loan import (
    CleanUpLoanRepaymentResponse,
    CompleteLoanArgs,
    ExecuteLoanRepaymentResponse,
    LoanDetails,
    PaymentReciepient,
    PendingLoanRoundPayment,
)


class ZaibatsuLoan(ZaibatsuBase):
    """
    ATTENTIONS!!!! THIS IS NOT A DRILL
    * All percentages comming into the smart contract must have been multiple
      by 100. This is to account for the lack of support for floats on the AVM
    """

    @a4.abimethod()
    def initiate_loan_purchase(
        self,
        loan_key: ap.Bytes,
        folks_feed_oracle: ap.Application,
        loan_details: LoanDetails,
        txn: gtxn.AssetTransferTransaction,
    ) -> LoanDetails:
        self.ensure_app_reciever(txn)

        val = op.Box.get(loan_key)
        assert not val[1], "A Loan purchase with this key has already been initiated"

        collateral_price = self.get_asset_price(folks_feed_oracle, txn.xfer_asset)
        assert collateral_price > 0, "The asa is of no value or is not supported"

        assert (
            loan_details.loan_type == a4.String("P2P")
            or loan_details.loan_type == a4.String("DAO")
            or loan_details.loan_type == a4.String("ZAIBATSU")
        ), "The loan must be either P2P, DAO or ZAIBATSU"

        if loan_details.loan_type == a4.String("P2P"):
            assert loan_details.payment_recipients.length == ap.UInt64(1), "Only one recipient is allowed in a P2P loan"

        assert not loan_details.collateral_paid, "The loan collateral must not be paid"
        assert not loan_details.principal_paid, "The loan principal must not be paid"
        assert loan_details.borrower == txn.sender, "The sender must also be the borrower"

        assert (
            loan_details.collateral_asset_id == txn.xfer_asset.id
        ), "The asset being transfered must be the collateral asset"

        assert txn.asset_amount >= self.calculate_amt_plus_fee(
            loan_details.collateral_asset_amount.native, ap.UInt64(1)
        ), "Insufficient txn asset_amount! Amount must be equal to collateral_asset_amount plus fees"

        assert (
            loan_details.payment_completion_timestamp.native > op.Global.latest_timestamp
        ), "The payment completion timestamp must be greater than now"

        loan_details.collateral_paid = a4.Bool(True)  # noqa: FBT003

        op.Box.put(loan_key, loan_details.bytes)

        return loan_details

    @ap.arc4.abimethod()
    def complete_non_p2p_loan_purchase(
        self,
        loan_key: ap.Bytes,
        completion_args: CompleteLoanArgs,
        principal_asset: ap.Asset,
        borrower: ap.Account,
    ) -> LoanDetails:
        [loan_bytes, exists] = op.Box.get(loan_key)
        assert exists, "A reccord with the loan_key passed was not found"
        details = LoanDetails.from_bytes(loan_bytes)
        assert details.collateral_paid, "The loan collateral must have been paid by this point"
        assert not details.principal_paid, "The principal must not have been paid"
        assert borrower == details.borrower.native, "The borrower must be the borrower in the loan details"
        assert (
            principal_asset.id == details.principal_asset_id.native
        ), "The asset passed must be the same as the principal"

        completion_txn = ap.itxn.AssetTransfer(
            fee=1000,
            xfer_asset=details.principal_asset_id.native,
            asset_receiver=details.borrower.native,
            asset_amount=details.principal_asset_amount.native,
        )
        completion_txn.submit()

        details.principal_paid = a4.Bool(True)  # noqa: FBT003
        details.completed_payment_rounds = a4.UInt8(0)
        borrower_nft = self.create_loan_nft(
            completion_args.borrower_nft_image_url,
            op.concat(ap.Bytes(b"B"), completion_args.loan_unit_name.bytes),
            op.concat(ap.Bytes(b"#B-"), completion_args.loan_unit_name.bytes),
            completion_args.loan_hash,
        )
        lender_nft = self.create_loan_nft(
            completion_args.lender_nft_image_url,
            op.concat(ap.Bytes(b"L"), completion_args.loan_unit_name.bytes),
            op.concat(ap.Bytes(b"#L-"), completion_args.loan_unit_name.bytes),
            completion_args.loan_hash,
        )
        details.borrower_nft_asser_id = a4.UInt64(borrower_nft.id)
        details.lender_nft_asser_id = a4.UInt64(lender_nft.id)
        op.Box.put(loan_key, details.bytes)
        return details

    @ap.arc4.abimethod()
    def complete_p2p_loan_purchase(
        self,
        loan_key: ap.Bytes,
        completion_args: CompleteLoanArgs,
        principal_asset: ap.Asset,
        borrower: ap.Account,
        txn: gtxn.AssetTransferTransaction,
    ) -> LoanDetails:
        self.ensure_app_reciever(txn)

        [loan_bytes, exists] = op.Box.get(loan_key)
        assert exists, "A reccord with the loan_key passed was not found"
        details = LoanDetails.from_bytes(loan_bytes)
        assert details.collateral_paid, "The loan collateral must have been paid by this point"
        assert not details.principal_paid, "The principal must not have been paid"
        assert (
            txn.xfer_asset.id == details.principal_asset_id.native
        ), "The asset transfered must be the same as the principal"
        assert borrower == details.borrower.native, "The borrower must be the borrower in the loan details"
        assert (
            principal_asset.id == details.principal_asset_id.native
        ), "The asset passed must be the same as the principal"

        self.ensure_transaction_fee_on_amount(txn, details.principal_asset_amount.native, ap.UInt64(1))
        completion_txn = ap.itxn.AssetTransfer(
            fee=1000,
            xfer_asset=details.principal_asset_id.native,
            asset_receiver=details.borrower.native,
            asset_amount=details.principal_asset_amount.native,
        )
        completion_txn.submit()

        details.principal_paid = a4.Bool(True)  # noqa: FBT003
        details.completed_payment_rounds = a4.UInt8(0)
        borrower_nft = self.create_loan_nft(
            completion_args.borrower_nft_image_url,
            op.concat(ap.Bytes(b"B"), completion_args.loan_unit_name.bytes),
            op.concat(ap.Bytes(b"#B-"), completion_args.loan_unit_name.bytes),
            completion_args.loan_hash,
        )
        lender_nft = self.create_loan_nft(
            completion_args.lender_nft_image_url,
            op.concat(ap.Bytes(b"L"), completion_args.loan_unit_name.bytes),
            op.concat(ap.Bytes(b"#L-"), completion_args.loan_unit_name.bytes),
            completion_args.loan_hash,
        )
        details.borrower_nft_asser_id = a4.UInt64(borrower_nft.id)
        details.lender_nft_asser_id = a4.UInt64(lender_nft.id)
        op.Box.put(loan_key, details.bytes)
        return details

    @ap.arc4.abimethod()
    def initiate_loan_repayment(
        self,
        loan_key: ap.Bytes,
        repayment_key: ap.String,
        txn: gtxn.AssetTransferTransaction,
    ) -> None:
        self.ensure_app_reciever(txn)

        [loan_bytes, exists] = op.Box.get(loan_key)
        assert exists, "A reccord with the loan_key passed was not found"

        details = LoanDetails.from_bytes(loan_bytes)
        principal_plus_interest = details.principal_asset_amount.native + details.interest_asset_amount.native
        payment_amount = principal_plus_interest // details.payment_rounds.native
        self.ensure_transaction_fee_on_amount(txn, payment_amount, details.payment_recipients.length)

        round_payment = PendingLoanRoundPayment(
            repayment_key=a4.String(repayment_key),
            loan_key=a4.String.from_bytes(loan_key),
            repayment_amount=a4.UInt64(payment_amount),
            percentage_paid=a4.UInt64(0),
            recipients=details.payment_recipients.copy(),
        )
        op.Box.put(repayment_key.bytes, round_payment.bytes)

    @ap.arc4.abimethod()
    def execute_loan_repayment(
        self,
        repayment_key: ap.String,
        recipient_account: ap.Account,
        payment_recipient: PaymentReciepient,
        principal_asset: ap.Asset,
    ) -> ExecuteLoanRepaymentResponse:
        [repayment_bytes, exists] = op.Box.get(repayment_key.bytes)
        assert exists, "A PendingLoanRoundPayment with this repayment_key was not found"
        repayment = PendingLoanRoundPayment.from_bytes(repayment_bytes)

        [loan_bytes, loan_exists] = op.Box.get(repayment.loan_key.bytes)
        assert loan_exists, "A loan with this key was not found"
        loan = LoanDetails.from_bytes(loan_bytes)
        assert (
            payment_recipient.recipient_address.native == recipient_account
        ), "The recipient_account does not match the payment_recipient"

        assert principal_asset.id == loan.principal_asset_id.native, "The principal_asset passed is invalid"

        recipient_is_valid = a4.Bool()

        for index in ap.urange(repayment.recipients.length):
            recipient = repayment.recipients[index].copy()
            if recipient.recipient_address == payment_recipient.recipient_address:
                assert (
                    recipient.payment_percentage.native == payment_recipient.payment_percentage.native
                ), "payment_recipient.payment_percentage is incorrect"
                recipient_is_valid = a4.Bool(True)  # noqa: FBT003
                break

        assert recipient_is_valid, "payment_recipient passed is not a valid payment_recipient of the specified loan"

        new_percentage_paid = payment_recipient.payment_percentage.native + repayment.percentage_paid.native

        assert new_percentage_paid <= ap.UInt64(
            10000
        ), "PendingLoanRe.percentage_paid + PaymentReciepient.payment_percentage will exceed 100%"

        repayment_txn = ap.itxn.AssetTransfer(
            fee=1000,
            xfer_asset=loan.principal_asset_id.native,
            asset_receiver=recipient_account,
            asset_amount=self.percentage(
                repayment.repayment_amount,
                payment_recipient.payment_percentage,
            ).native,
        )
        repayment_txn.submit()
        repayment.percentage_paid = a4.UInt64(new_percentage_paid)

        op.Box.put(repayment_key.bytes, repayment.bytes)
        repayment_response = ExecuteLoanRepaymentResponse(
            loan_repayment_complete=a4.Bool(new_percentage_paid == ap.UInt64(10000)),
            percentage_paid=a4.UInt64(new_percentage_paid),
        )
        return repayment_response

    @ap.arc4.abimethod()
    def clean_up_loan_repayment(
        self,
        repayment_key: ap.String,
        borrower_account: ap.Account,
    ) -> CleanUpLoanRepaymentResponse:
        [repayment_bytes, exists] = op.Box.get(repayment_key.bytes)
        assert exists, "A PendingLoanRoundPayment with this repayment_key was not found"
        repayment = PendingLoanRoundPayment.from_bytes(repayment_bytes)

        [loan_bytes, loan_exists] = op.Box.get(repayment.loan_key.bytes)
        assert loan_exists, "A loan with this key was not found"
        loan = LoanDetails.from_bytes(loan_bytes)

        assert loan.borrower.native == borrower_account, "The borrower_account provided is incorrect"

        clean_up_response = CleanUpLoanRepaymentResponse(loan_repayment_complete=a4.Bool())

        loan.completed_payment_rounds = a4.UInt8(loan.completed_payment_rounds.native + ap.UInt64(1))
        if loan.payment_rounds.native == loan.completed_payment_rounds.native:
            complete_loan_repaymet_txn = ap.itxn.AssetTransfer(
                fee=100,
                xfer_asset=loan.collateral_asset_id.native,
                asset_receiver=borrower_account,
                asset_amount=loan.collateral_asset_amount.native,
                note="Collateral repayment on completed loan",
            )
            complete_loan_repaymet_txn.submit()
            op.Box.delete(repayment.loan_key.bytes)
            clean_up_response.loan_repayment_complete = a4.Bool(True)  # noqa: FBT003
        else:
            op.Box.put(repayment.loan_key.bytes, loan.bytes)

        op.Box.delete(repayment_key.bytes)

        return clean_up_response
