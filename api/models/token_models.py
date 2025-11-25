from pydantic import BaseModel

class TokenCreate(BaseModel):
    name: str
    symbol: str
    total_supply: float
    owner_address: str

class TokenTransfer(BaseModel):
    sender_address: str
    sender_public_key: str
    receiver_address: str
    symbol: str
    amount: float
    signature: str
