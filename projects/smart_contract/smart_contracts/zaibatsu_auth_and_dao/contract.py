# pyright: reportMissingModuleSource=false
import algopy as ap
from algopy import arc4 as a4
from algopy import gtxn, op

from smart_contracts.zaibatsu_auth_and_dao.types.pool import (
    PoolFundResponse,
    PoolInfo,
    PoolVoteApprovalResponse,
)
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
        pool_key: ap.String,
        image_url: ap.String,
        token_unit_name: ap.String,
        token_asset_name: ap.String,
        max_contributors: ap.UInt64,
        asset_decimals_multiplier: ap.UInt64,
    ) -> PoolInfo:
        assert (
            txn.asset_receiver == self.service_contract_address.native
        ), "The asset_receiver mut be the ZaibatsuLoan account"

        asset_dollar_price = self.get_asset_price(folks_feed_oracle, txn.xfer_asset)

        creation_fee = (
            asset_dollar_price * txn.asset_amount
        ) // asset_decimals_multiplier

        assert creation_fee >= ap.UInt64(
            20
        ), "The asset_amount must be worth at least 20 dollars"

        total = ap.UInt64(1000000) * max_contributors

        existing = op.Box.get(pool_key.bytes)
        assert not existing[1], "A pool with this key already exists"

        asset_txn = ap.itxn.AssetConfig(
            fee=1000,
            total=total,
            url=image_url,
            unit_name=token_unit_name,
            asset_name=token_asset_name,
            manager=ap.Global.current_application_address,
            reserve=ap.Global.current_application_address,
            freeze=ap.Global.current_application_address,
            clawback=ap.Global.current_application_address,
        )
        asset_txn.submit()
        pool_info = PoolInfo(
            pool_key=a4.String(pool_key),
            token_balance=a4.UInt64(total),
            pool_asset_id=a4.UInt64(op.ITxn.created_asset_id().id),
        )

        op.Box.put(pool_key.bytes, pool_info.bytes)
        return pool_info

    @a4.abimethod()
    def optin_pool_asset(
        self,
        optin_txn: gtxn.AssetTransferTransaction,
        pool_key: ap.String,
    ) -> None:
        pool_data, exists = op.Box.get(pool_key.bytes)
        assert exists, "A pool with that key does not exist"
        pool_info = PoolInfo.from_bytes(pool_data)

        assert (
            optin_txn.xfer_asset.id == pool_info.pool_asset_id.native
        ), "The OptIn txn asset must be the same as the pool asset"

    @a4.abimethod()
    def fund_pool(
        self,
        pool_key: ap.String,
        fund_amount: ap.UInt64,
        user_account: ap.Account,
        folks_feed_oracle: ap.Application,
        txn: gtxn.AssetTransferTransaction,
        pool_asset: ap.Asset,
        asset_decimals_multiplier: ap.UInt64,
    ) -> PoolFundResponse:
        pool_data, exists = op.Box.get(pool_key.bytes)
        assert exists, "A pool with that key does not exist"
        pool_info = PoolInfo.from_bytes(pool_data)

        assert (
            user_account == txn.sender
        ), "The user account must be the same as the txn sender"
        assert (
            pool_asset.id == pool_info.pool_asset_id.native
        ), "pool_asset must match the asset of the specified pool"

        asset_dollar_price = self.get_asset_price(folks_feed_oracle, txn.xfer_asset)
        asset_amount = txn.asset_amount

        asset_value_in_usd = (
            asset_amount // asset_decimals_multiplier * asset_dollar_price
        )

        reward_txn = ap.itxn.AssetTransfer(
            fee=1000,
            note="Pool fund reward",
            asset_receiver=user_account,
            asset_amount=asset_value_in_usd,
            xfer_asset=pool_info.pool_asset_id.native,
        )
        reward_txn.submit()

        pool_info.token_balance = a4.UInt64(pool_info.token_balance.native - asset_value_in_usd)

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
        )
        op.Box.put(pool_key.bytes, pool_info.bytes)
        return response

    @a4.abimethod()
    def approve_pool_vote(
        self,
        pool_key: ap.String,
        txn: gtxn.AssetTransferTransaction,
    ) -> PoolVoteApprovalResponse:
        box_data, exists = op.Box.get(pool_key.bytes)
        assert exists, "PoolInfo with that key does not exist"
        pool_info = PoolInfo.from_bytes(box_data)
        assert (
            txn.xfer_asset.id == pool_info.pool_asset_id.native
        ), "The asset transfered must be the pool token"

        response = PoolVoteApprovalResponse(
            multiplier=a4.UInt64(txn.asset_amount),
            txn_id=a4.String.from_bytes(txn.txn_id),
        )
        return response
