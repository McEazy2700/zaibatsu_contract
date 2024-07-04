# pyright: reportMissingModuleSource=false
from typing import TypeAlias

import algopy as ap
from algopy import Global, gtxn, op
from algopy import arc4 as a4

AddressArray: TypeAlias = a4.DynamicArray[a4.Address]


class ZaibatsuBase(ap.ARC4Contract):
    def __init__(self) -> None:
        self.admins: AddressArray = AddressArray()
        self.service_contract: a4.Address = a4.Address()

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
        self.opt_app_into_asset(asset)
        return True

    ################################################################
    #####################   Subroutines    #########################
    ################################################################
    @ap.subroutine
    def opt_app_into_asset(self, asset: ap.Asset) -> None:
        txn = ap.itxn.AssetTransfer(
            asset_amount=0,
            fee=1000,
            xfer_asset=asset,
            asset_receiver=ap.Global.current_application_address,
        )
        txn.submit()

    @ap.subroutine
    def authorise_txn(self) -> None:
        is_authorised = a4.Bool()
        if ap.Txn.sender == op.Global.creator_address:
            is_authorised = a4.Bool(True)  # noqa: FBT003
        else:
            for index in ap.urange(self.admins.length):
                if self.admins[index] == ap.Txn.sender:
                    is_authorised = a4.Bool(True)  # noqa: FBT003
        assert is_authorised, "You are not authorised to perform this action"

    @ap.subroutine
    def create_loan_nft(
        self,
        image_url: a4.String,
        short_name: ap.Bytes,
        logn_name: ap.Bytes,
        loan_hash: a4.String,
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
    def ensure_transaction_fee_on_amount(
        self,
        txn: gtxn.AssetTransferTransaction,
        amount: ap.UInt64,
        multiples: ap.UInt64,
    ) -> None:
        assert txn.asset_amount >= self.calculate_amt_plus_fee(
            amount, multiples
        ), "Insufficient txn asset_amount! Amount must be equal to principal_asset_amount plus fees"

    @ap.subroutine
    def calculate_amt_plus_fee(self, amt: ap.UInt64, multiples: ap.UInt64) -> ap.UInt64:
        fee_percentage = ap.UInt64(5) * multiples
        amt_adjusted_for_decimal = amt * ap.UInt64(10)
        approx_fee_plus_amt = self.percentage_increase(a4.UInt64(amt_adjusted_for_decimal), a4.UInt64(fee_percentage))
        corrected_approx_fee_plus_amt = approx_fee_plus_amt.native // ap.UInt64(10)
        return corrected_approx_fee_plus_amt

    @ap.subroutine
    def get_asset_price(self, folks_feed_oracle: ap.Application, asa: ap.Asset) -> ap.UInt64:
        [value, exists] = op.AppGlobal.get_ex_bytes(folks_feed_oracle, op.itob(asa.id))
        assert exists, "This aset is not supported"
        return op.extract_uint64(value, ap.UInt64(0))

    @ap.subroutine
    def percentage(self, amount: a4.UInt64, percent: a4.UInt64) -> a4.UInt64:
        result = (percent.native * amount.native) // ap.UInt64(100)
        return a4.UInt64(result)

    @ap.subroutine
    def percentage_increase(self, amount: a4.UInt64, increase: a4.UInt64) -> a4.UInt64:
        percentage = self.percentage(amount, increase)
        results = percentage.native + amount.native
        return a4.UInt64(results)

    @ap.subroutine
    def ensure_app_reciever(self, txn: gtxn.AssetTransferTransaction) -> None:
        assert (
            txn.asset_receiver == Global.current_application_address
        ), "The recipient must be the current_application_address address"

    @ap.subroutine
    def ensure_service_reciever(self, txn: gtxn.AssetTransferTransaction) -> None:
        assert txn.asset_receiver == self.service_contract.native, "The recipient must be the ZaibatsuService address"
