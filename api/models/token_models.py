from pydantic import BaseModel, validator
import time

class TokenCreate(BaseModel):
    name: str
    symbol: str
    total_supply: float
    owner_address: str

    @validator('total_supply')
    def positive_supply(cls, v):
        if v <= 0:
            raise ValueError('Total supply must be positive')
        return v

class TokenTransfer(BaseModel):
    sender_address: str
    sender_public_key: str
    receiver_address: str
    symbol: str
    amount: float
    timestamp: float # Replay protection
    signature: str

    @validator('amount')
    def positive_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @validator('timestamp')
    def recent_timestamp(cls, v):
        # Allow 60s window (plus slight drift)
        if abs(time.time() - v) > 120:
            raise ValueError('Timestamp too old or in future')
        return v
