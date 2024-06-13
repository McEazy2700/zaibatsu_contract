import algopy as ap
from algopy import Global, gtxn, op
from algopy import arc4 as a4

from smart_contracts.zaibatsu_service.types.loan import (
    A4UInt64,
    AddressArray,
    CompleteLoanArgs,
    LoanDetails,
)


class ZaibatsuService(ap.ARC4Contract):
    """
    ATTENTIONS!!!! THIS IS NOT A DRILL
    * All percentages comming into the smart contract must have been multiple
      by 100. This is to account for the lack of support for floats on the AVM
    """

    def __init__(self) -> None:
        self.admins: AddressArray = AddressArray()

    @ap.arc4.abimethod()
    def hello(self, name: a4.String) -> ap.arc4.String:
        return "Hello, " + name

    @a4.abimethod(create="allow")
    def create(self) -> bool:
        self.admins.append(a4.Address(ap.Txn.sender))
        return True

    @a4.abimethod(allow_actions=["UpdateApplication"])
    def update(self) -> bool:
        if ap.Txn.sender == op.Global.creator_address:
            return True
        for index in ap.urange(self.admins.length):
            if self.admins[index] == ap.Txn.sender:
                return True
        return False

    @a4.abimethod(allow_actions=["DeleteApplication"])
    def delete(self) -> bool:
        if ap.Txn.sender == op.Global.creator_address:
            return True
        return False

    @a4.abimethod()
    def opt_contract_into_asset(self, asset: ap.Asset) -> bool:
        txn = ap.itxn.AssetTransfer(
            asset_amount=0,
            fee=1000,
            xfer_asset=asset,
            asset_receiver=ap.Global.current_application_address,
        )
        txn.submit()
        return True

    @a4.abimethod()
    def iniate_p2p_loan_purchase(
        self,
        loan_key: ap.Bytes,
        folks_feed_oracle: ap.Application,
        loan_details: LoanDetails,
        txn: gtxn.AssetTransferTransaction,
    ) -> LoanDetails:
        assert (
            txn.asset_receiver == Global.current_application_address
        ), "The recipient must be the ZaibatsuService address"

        val = op.Box.get(loan_key)
        assert not val[1], "A Loan purchase with this key has already been initiated"

        collateral_price = self.get_asset_price(folks_feed_oracle, txn.xfer_asset)
        assert collateral_price > 0, "The asa is of no value or is not supported"

        assert loan_details.loan_type == a4.String("P2P"), "The loan must be a P2P loan"
        assert not loan_details.collateral_paid, "The loan collateral must not be paid"
        assert not loan_details.principal_paid, "The loan principal must not be paid"
        assert loan_details.payment_recipients.length == ap.UInt64(1), "Only one recipient is allowed in a P2P loan"
        assert loan_details.borrower == txn.sender, "The sender must also be the borrower"

        assert (
            loan_details.collateral_asset_id == txn.xfer_asset.id
        ), "The asset being transfered must be the collateral asset"

        assert txn.asset_amount >= self.calculate_amt_plus_fee(
            loan_details.collateral_asset_amount.native
        ), "Insufficient txn asset_amount! Amount must be equal to collateral_asset_amount plus fees"

        assert (
            loan_details.payment_completion_timestamp.native > op.Global.latest_timestamp
        ), "The payment completion timestamp must be greater than now"

        loan_details.collateral_paid = a4.Bool(True)  # noqa: FBT003

        op.Box.put(loan_key, loan_details.bytes)

        return loan_details

    @ap.arc4.abimethod()
    def complete_p2p_loan_purchase(
        self,
        loan_key: ap.Bytes,
        completion_args: CompleteLoanArgs,
        principal_asset: ap.Asset,
        borrower: ap.Account,
        txn: gtxn.AssetTransferTransaction,
    ) -> LoanDetails:
        assert (
            txn.asset_receiver == Global.current_application_address
        ), "The recipient must be the ZaibatsuService address"

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

        assert txn.asset_amount >= self.calculate_amt_plus_fee(
            details.principal_asset_amount.native
        ), "Insufficient txn asset_amount! Amount must be equal to principal_asset_amount plus fees"

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
            op.concat(ap.Bytes(b"B-"), completion_args.loan_unit_name.bytes),
            op.concat(ap.Bytes(b"#B-"), completion_args.loan_unit_name.bytes),
            completion_args.loan_hash,
        )
        lender_nft = self.create_loan_nft(
            completion_args.lender_nft_image_url,
            op.concat(ap.Bytes(b"L-"), completion_args.loan_unit_name.bytes),
            op.concat(ap.Bytes(b"#L-"), completion_args.loan_unit_name.bytes),
            completion_args.loan_hash,
        )
        details.borrower_nft_asser_id = A4UInt64(borrower_nft.id)
        details.lender_nft_asser_id = A4UInt64(lender_nft.id)
        op.Box.put(loan_key, details.bytes)
        return details

    @ap.subroutine
    def create_loan_nft(
        self, image_url: a4.String, short_name: ap.Bytes, logn_name: ap.Bytes, loan_hash: a4.String
    ) -> ap.Asset:
        txn = ap.itxn.AssetConfig(
            total=1,
            url=image_url.native,
            unit_name=short_name,
            asset_name=logn_name,
            fee=1000,
            metadata_hash=loan_hash.native.bytes,
            manager=op.Global.current_application_address,
            reserve=op.Global.current_application_address,
            freeze=op.Global.current_application_address,
            clawback=op.Global.current_application_address,
        )
        txn.submit()
        return op.ITxn.created_asset_id()

    @ap.subroutine
    def calculate_amt_plus_fee(self, amt: ap.UInt64) -> ap.UInt64:
        fee_percentage = ap.UInt64(5)
        amt_adjusted_for_decimal = amt * ap.UInt64(10)
        approx_fee_plus_amt = self.percentage_increase(A4UInt64(amt_adjusted_for_decimal), A4UInt64(fee_percentage))
        corrected_approx_fee_plus_amt = approx_fee_plus_amt.native // ap.UInt64(10)
        return corrected_approx_fee_plus_amt

    @ap.subroutine
    def get_asset_price(self, folks_feed_oracle: ap.Application, asa: ap.Asset) -> ap.UInt64:
        [value, exists] = op.AppGlobal.get_ex_bytes(folks_feed_oracle, op.itob(asa.id))
        assert exists, "This aset is not supported"
        return op.extract_uint64(value, ap.UInt64(0))

    @ap.subroutine
    def percentage(self, amount: A4UInt64, percent: A4UInt64) -> A4UInt64:
        result = (percent.native * amount.native) // ap.UInt64(100)
        return A4UInt64(result)

    @ap.subroutine
    def percentage_increase(self, amount: A4UInt64, increase: A4UInt64) -> A4UInt64:
        percentage = self.percentage(amount, increase)
        results = percentage.native + amount.native
        return A4UInt64(results)
