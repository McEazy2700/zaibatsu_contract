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
    def transfer_zai(
        self, to: a4.Address, asset_amount: a4.UInt64, note: a4.String
    ) -> bool:
        self.authorise_txn()
        zai_asset_id = self.get_zai_token()
        txn = ap.itxn.AssetTransfer(
            fee=1000,
            asset_receiver=to.native,
            asset_amount=asset_amount.native,
            xfer_asset=zai_asset_id.native,
            note=note.native,
        )
        txn.submit()
        return True

    @a4.abimethod()
    def fund_pool(
        self,
        fund_amount: ap.UInt64,
        folks_feed_oracle: ap.Application,
        txn: gtxn.AssetTransferTransaction,
    ) -> PoolFundResponse:

        asset_dollar_price = self.get_asset_price(folks_feed_oracle, txn.xfer_asset)
        assert (
            txn.asset_receiver == self.service_contract_address.native
        ), "The asset_receiver mut be the ZaibatsuService account"

        amount_plus_transaction_fee = self.calculate_amt_plus_fee(
            fund_amount, ap.UInt64(1)
        )
        assert (
            txn.asset_amount >= amount_plus_transaction_fee
        ), "The txn amount is insufficient"

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
        assert (
            txn.xfer_asset.id == zai_asset_id.native
        ), "The asset transfered must be the pool token"

        response = PoolVoteApprovalResponse(
            multiplier=a4.UInt64(txn.asset_amount),
            txn_id=a4.String.from_bytes(txn.txn_id),
        )
        return response

    @ap.subroutine
    def handle_create_zai_token(self) -> None:
        box = op.Box.get(b"ZAI")
        if not box[1]:
            asset_txn = ap.itxn.AssetConfig(
                fee=1000,
                decimals=6,
                total=1_000_000_000_000,
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
            op.Box.put(b"ZAI", a4.UInt64(asset_id).bytes)

    @ap.subroutine
    def get_zai_token(self) -> a4.UInt64:
        box_data, exists = op.Box.get(b"ZAI")
        zai_asset_id = a4.UInt64()
        if not exists:
            self.handle_create_zai_token()
            box_data, exists = op.Box.get(b"ZAI")
            zai_asset_id = a4.UInt64.from_bytes(box_data)
        else:
            zai_asset_id = a4.UInt64.from_bytes(box_data)
        return zai_asset_id
