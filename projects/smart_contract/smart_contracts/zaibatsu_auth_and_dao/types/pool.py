from algopy.arc4 import Bool, Struct, UInt64  # pyright: ignore


class PoolFundResponse(Struct, kw_only=True):
    amount: UInt64
    success: Bool
