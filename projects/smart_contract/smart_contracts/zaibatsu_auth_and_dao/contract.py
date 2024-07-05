# pyright: reportMissingModuleSource=false
import algopy as ap
from algopy import arc4 as a4
from algopy import gtxn, op

from smart_contracts.zaibatsu_auth_and_dao.types.pool import PoolFundResponse
from smart_contracts.zaibatsu_base.contract import ZaibatsuBase


class ZaibatsuAuthAndDao(ZaibatsuBase):
    @a4.abimethod()
    def hello(self, name: a4.String) -> a4.String:
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
    def set_service_contract_address(self, address: a4.Address) -> bool:
        self.authorise_txn()
        self.service_contract_address = address
        return True

    @a4.abimethod()
    def authorize_pool_creation(
        self,
        txn: gtxn.AssetTransferTransaction,
        folks_feed_oracle: ap.Application,
        asset_decimals_multiplier: ap.UInt64,
    ) -> PoolFundResponse:
        assert (
            txn.asset_receiver == self.service_contract_address.native
        ), "The asset_receiver mut be the ZaibatsuService account"
        amount_plus_transaction_fee = self.calculate_amt_plus_fee(txn.asset_amount, ap.UInt64(1))
        fee_amount = amount_plus_transaction_fee - txn.asset_amount
        pool_fund_amount = txn.asset_amount - fee_amount

        asset_dollar_price = self.get_asset_price(folks_feed_oracle, txn.xfer_asset)
        pool_fund_dollar_amount = (asset_dollar_price * pool_fund_amount) // asset_decimals_multiplier
        assert pool_fund_dollar_amount > ap.UInt64(20), "The asset_amount must be worth greater that 20 dollars"
        approval = PoolFundResponse(
            amount=a4.UInt64(pool_fund_amount),
            success=a4.Bool(True),  # noqa: FBT003
        )
        return approval

    @a4.abimethod()
    def fund_pool(
        self,
        txn: gtxn.AssetTransferTransaction,
    ) -> PoolFundResponse:
        assert (
            txn.asset_receiver == self.service_contract_address.native
        ), "The asset_receiver mut be the ZaibatsuService account"
        amount_plus_transaction_fee = self.calculate_amt_plus_fee(txn.asset_amount, ap.UInt64(1))
        fee_amount = amount_plus_transaction_fee - txn.asset_amount
        pool_fund_amount = txn.asset_amount - fee_amount

        approval = PoolFundResponse(
            amount=a4.UInt64(pool_fund_amount),
            success=a4.Bool(True),  # noqa: FBT003
        )
        return approval
