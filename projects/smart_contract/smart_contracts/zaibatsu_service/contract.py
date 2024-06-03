import algopy as ap
from algopy import Global, gtxn, op
from algopy import arc4 as a4

from smart_contracts.zaibatsu_service.types.loan import (
    A4UInt64,
    AddressArray,
    CompleteLoanArgs,
    LoanDetails,
    LoanNftName,
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
        assert (
            op.btoi(loan_details.collateral_asset_amount.bytes) == txn.asset_amount
        ), "The amount of asset transfered must equal the amount specified"
        assert (
            op.btoi(loan_details.payment_completion_timestamp.bytes) > op.Global.latest_timestamp
        ), "The payment completion timestamp must be greater than now"
        self._opt_contract_into_asset(txn.xfer_asset)

        loan_details.collateral_paid = a4.Bool(True)

        op.Box.put(loan_key, loan_details.bytes)

        return loan_details

    @ap.arc4.abimethod()
    def complete_p2p_loan_purchase(
        self, completion_args: CompleteLoanArgs, txn: gtxn.AssetTransferTransaction
    ) -> LoanDetails:
        [loan_bytes, exists] = op.Box.get(completion_args.loan_key.bytes)
        assert exists, "A reccord with the loan_key passed was not found"
        details = LoanDetails.from_bytes(loan_bytes)
        assert details.collateral_paid, "The loan collateral must have been paid by this point"
        assert not details.principal_paid, "The principal must not have been paid"
        assert txn.asset_receiver == details.borrower, "The borrower must be the reciever"
        assert txn.xfer_asset.id == details.principal_asset_id, "The asset transfered must be the same as the principal"

        assert (
            txn.asset_amount == details.lend_asset_amount
        ), "The asset transfered must equal the lend_asset_amount recorded"
        details.principal_paid = a4.Bool(True)
        details.completed_payment_rounds = a4.UInt8(0)
        borrower_nft = self.create_loan_nft(
            completion_args.borrower_nft_image_url, a4.String(f"B{completion_args.loan_number}")
        )
        # Todo: Create a borrower nft on success and store the key as part of the loan details
        # Todo: Create a lender nft and store the key as part of the loan details
        # On succefull transaction, send lender and borrower nft to their respective owners
        return details

    @ap.subroutine
    def create_loan_nft(
        self, image_url: a4.String, short_name: a4.String, logn_name: a4.String, loan_hash: a4.String
    ) -> ap.Asset:
        txn = ap.itxn.AssetConfig(
            unit_name=short_name,
            asset_name=logn_name,
            url=image_url,
            total=1,
            metadata_hash=loan_hash,
            manager=op.Global.current_application_address,
            reserve=op.Global.current_application_address,
            freeze=op.Global.current_application_address,
            clawback=op.Global.current_application_address,
        )
        txn.submit()
        return op.ITxn.created_asset_id()

    @ap.subroutine
    def get_asset_price(self, folks_feed_oracle: ap.Application, asa: ap.Asset) -> ap.UInt64:
        [value, exists] = op.AppGlobal.get_ex_bytes(folks_feed_oracle, op.itob(asa.id))
        assert exists, "This aset is not supported"
        return op.extract_uint64(value, ap.UInt64(0))

    @ap.subroutine
    def percentage(self, amount: A4UInt64, percent: A4UInt64) -> A4UInt64:
        """
        This callculates percentage of a number assuming the percent has been multiplied
        by 100 to account for the lack of decimal precision
        """
        hundered: ap.UInt64 = op.btoi(A4UInt64(100).bytes)
        percent_num = op.btoi(percent.bytes)
        amount_num = op.btoi(amount.bytes)
        results = ((hundered // percent_num) * amount_num) // op.btoi(a4.UInt64(100).bytes)
        return A4UInt64.from_bytes(op.itob(results))

    @ap.subroutine
    def percentage_increase(self, amount: A4UInt64, increase: A4UInt64) -> A4UInt64:
        percentage_val = op.btoi(self.percentage(amount, increase).bytes)
        amount_num = op.btoi(amount.bytes)
        results = percentage_val + amount_num
        return A4UInt64.from_bytes(op.itob(results))

    @ap.subroutine
    def _opt_contract_into_asset(self, asset_id: ap.Asset) -> bool:
        txn = ap.itxn.AssetTransfer(
            xfer_asset=asset_id,
            fee=1000,
            asset_receiver=ap.Global.current_application_address,
        )
        txn.submit()
        return True
