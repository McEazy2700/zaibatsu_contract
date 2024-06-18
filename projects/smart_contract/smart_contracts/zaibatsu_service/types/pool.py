from algopy.arc4 import Bool, Struct, UInt64  # pyright: ignore


class PoolCreationApproval(Struct, kw_only=True):
    initial_amount: UInt64
    success: Bool
