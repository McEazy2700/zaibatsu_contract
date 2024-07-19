from algopy.arc4 import Bool, String, Struct, UInt64  # pyright: ignore


class PoolInfo(Struct, kw_only=True):
    pool_key: String
    token_balance: UInt64
    pool_asset_id: UInt64

class PoolFundResponse(Struct, kw_only=True):
    amount: UInt64
    success: Bool


class PoolVoteApprovalResponse(Struct, kw_only=True):
    multiplier: UInt64
    txn_id: String
