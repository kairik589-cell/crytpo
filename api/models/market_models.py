from pydantic import BaseModel
from typing import Optional

class LiquidityPoolModel(BaseModel):
    pair: str # e.g. "BTC-MTK"
    token_symbol: str
    reserve_native: float
    reserve_token: float
    total_shares: float

class PoolCreate(BaseModel):
    token_symbol: str
    initial_native: float
    initial_token: float
    creator_address: str
    signature: str

class LiquidityAction(BaseModel):
    pair: str
    user_address: str
    amount_native: Optional[float] = 0
    amount_token: Optional[float] = 0
    signature: str

class SwapRequest(BaseModel):
    user_address: str
    pair: str
    direction: str # "native_to_token" or "token_to_native"
    amount_in: float
    min_amount_out: float
    signature: str

class StakeRequest(BaseModel):
    user_address: str
    symbol: str # "BTC" (native) or Token Symbol
    amount: float
    duration_days: int # Lock period (simulated)
    signature: str
