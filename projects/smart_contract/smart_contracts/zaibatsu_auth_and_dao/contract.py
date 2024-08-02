# pyright: reportMissingModuleSource=false
import algopy as ap
from algopy import arc4 as a4
from algopy import gtxn, op

from smart_contracts.zaibatsu_auth_and_dao.types.pool import (
    PoolFundResponse,
    PoolVoteApprovalResponse,
)
from smart_contracts.zaibatsu_base.contract import ZaibatsuBase


class ZaibatsuAuthAndDao(ZaibatsuBase):
    def __init__(self) -> None:
        self.zai_token_asset_id: a4.UInt64 = a4.UInt64()

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
    def create_zaibatsu_token(self) -> a4.UInt64:
        self.handle_create_zai_token()
        return self.get_zai_token()

    @a4.abimethod()
    def authorize_pool_creation(
        self,
        txn: gtxn.AssetTransferTransaction,
        folks_feed_oracle: ap.Application,
    ) -> bool:
        assert (
            txn.asset_receiver == self.service_contract_address.native
        ), "The asset_receiver mut be the ZaibatsuLoan account"

        asset_dollar_price = self.get_asset_price(folks_feed_oracle, txn.xfer_asset)
        creation_fee = asset_dollar_price * txn.asset_amount
        assert creation_fee >= ap.UInt64(20), "The asset_amount must be worth at least 20 dollars"
        return True

    @a4.abimethod()
    def fund_pool(
        self,
        fund_amount: ap.UInt64,
        user_account: ap.Account,
        folks_feed_oracle: ap.Application,
        zai: ap.Asset,
        txn: gtxn.AssetTransferTransaction,
    ) -> PoolFundResponse:
        zai_asset_id = self.get_zai_token()

        assert zai.id == zai_asset_id.native, "The asset passed must be the zaibatsu asset"
        assert user_account == txn.sender, "The user account must be the same as the txn sender"

        asset_dollar_price = self.get_asset_price(folks_feed_oracle, txn.xfer_asset)
        asset_amount = txn.asset_amount
        asset_value_in_usd = asset_amount // asset_dollar_price
        reward_txn = ap.itxn.AssetTransfer(
            fee=1000,
            note="Pool fund reward",
            asset_receiver=user_account,
            asset_amount=asset_value_in_usd,
            xfer_asset=zai,
        )
        reward_txn.submit()

        assert (
            txn.asset_receiver == self.service_contract_address.native
        ), "The asset_receiver mut be the ZaibatsuService account"

        amount_plus_transaction_fee = self.calculate_amt_plus_fee(fund_amount, ap.UInt64(1))
        assert txn.asset_amount >= amount_plus_transaction_fee, "The txn amount is insufficient"

        response = PoolFundResponse(
            amount=a4.UInt64(fund_amount),
            success=a4.Bool(True),  # noqa: FBT003
            asset_price=a4.UInt64(asset_dollar_price),
        )
        return response

    @a4.abimethod()
    def approve_pool_vote(
        self,
        txn: gtxn.AssetTransferTransaction,
    ) -> PoolVoteApprovalResponse:
        zai_asset_id = self.get_zai_token()
        assert txn.xfer_asset.id == zai_asset_id.native, "The asset transfered must be the pool token"

        response = PoolVoteApprovalResponse(
            multiplier=a4.UInt64(txn.asset_amount),
            txn_id=a4.String.from_bytes(txn.txn_id),
        )
        return response

    @ap.subroutine
    def handle_create_zai_token(self) -> None:
        box = op.Box.get(b"zai")
        if not box[1]:
            asset_txn = ap.itxn.AssetConfig(
                fee=1000,
                total=10000000000000000,
                url="https://res.cloudinary.com/dev-media/image/upload/v1722011867/Zaibatsu_z_1234_Circle_yjt49c.png",
                unit_name="ZAI",
                asset_name="ZAI",
                manager=ap.Global.current_application_address,
                reserve=ap.Global.current_application_address,
                freeze=ap.Global.current_application_address,
                clawback=ap.Global.current_application_address,
            )
            asset_txn.submit()
            asset_id = op.ITxn.created_asset_id().id
            op.Box.put(b"zai", a4.UInt64(asset_id).bytes)

    @ap.subroutine
    def get_zai_token(self) -> a4.UInt64:
        box_data, exists = op.Box.get(b"zai")
        zai_asset_id = a4.UInt64()
        if not exists:
            self.handle_create_zai_token()
            box_data, exists = op.Box.get(b"zai")
            zai_asset_id = a4.UInt64.from_bytes(box_data)
        else:
            zai_asset_id = a4.UInt64.from_bytes(box_data)
        return zai_asset_id
