from pydantic import BaseModel, validator
from typing import Optional
import time

class LiquidityPoolModel(BaseModel):
    pair: str
    token_symbol: str
    reserve_native: float
    reserve_token: float
    total_shares: float

class PoolCreate(BaseModel):
    token_symbol: str
    initial_native: float
    initial_token: float
    creator_address: str
    timestamp: float
    signature: str

    @validator('initial_native', 'initial_token')
    def positive_initial(cls, v):
        if v <= 0: raise ValueError('Initial liquidity must be positive')
        return v

    @validator('timestamp')
    def recent_timestamp(cls, v):
        if abs(time.time() - v) > 120: raise ValueError('Timestamp invalid')
        return v

class LiquidityAction(BaseModel):
    pair: str
    user_address: str
    amount_native: Optional[float] = 0.0
    amount_token: Optional[float] = 0.0
    timestamp: float
    signature: str

    @validator('amount_native', 'amount_token')
    def non_negative(cls, v):
        if v < 0: raise ValueError('Amount cannot be negative')
        return v

    @validator('timestamp')
    def recent_timestamp(cls, v):
        if abs(time.time() - v) > 120: raise ValueError('Timestamp invalid')
        return v

class SwapRequest(BaseModel):
    user_address: str
    pair: str
    direction: str
    amount_in: float
    min_amount_out: float
    timestamp: float
    signature: str

    @validator('amount_in')
    def positive_in(cls, v):
        if v <= 0: raise ValueError('Amount in must be positive')
        return v

    @validator('timestamp')
    def recent_timestamp(cls, v):
        if abs(time.time() - v) > 120: raise ValueError('Timestamp invalid')
        return v

class StakeRequest(BaseModel):
    user_address: str
    symbol: str
    amount: float
    duration_days: int
    timestamp: float
    signature: str

    @validator('amount')
    def positive_amount(cls, v):
        if v <= 0: raise ValueError('Amount must be positive')
        return v

    @validator('timestamp')
    def recent_timestamp(cls, v):
        if abs(time.time() - v) > 120: raise ValueError('Timestamp invalid')
        return v
