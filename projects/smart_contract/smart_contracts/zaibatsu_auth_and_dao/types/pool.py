from algopy.arc4 import Bool, String, Struct, UInt64  # pyright: ignore


class PoolFundResponse(Struct, kw_only=True):
    amount: UInt64
    asset_price: UInt64
    success: Bool


class PoolVoteApprovalResponse(Struct, kw_only=True):
    multiplier: UInt64
    txn_id: String
