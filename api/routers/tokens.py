from fastapi import APIRouter, HTTPException, Body
from api.core.database import tokens_col, token_balances_col, token_transfers_col
from api.models.token_models import TokenCreate, TokenTransfer
from api.services.wallet_service import verify_signature
from api.core.utils import serialize_mongo
import time

router = APIRouter()

@router.post("/create")
async def create_token(token: TokenCreate):
    existing = await tokens_col.find_one({"symbol": token.symbol})
    if existing:
        raise HTTPException(status_code=400, detail="Token symbol already exists")

    token_doc = token.dict()
    token_doc["created_at"] = time.time()

    await tokens_col.insert_one(token_doc)

    # Mint initial supply
    await token_balances_col.insert_one({
        "address": token.owner_address,
        "symbol": token.symbol,
        "balance": token.total_supply
    })

    return serialize_mongo({"message": "Token created successfully", "token": token_doc})

@router.post("/transfer")
async def transfer_token(transfer: TokenTransfer):
    # 1. Verify Signature (Replay Protection via timestamp in message)
    # Message: sender:receiver:symbol:amount:timestamp
    msg = f"{transfer.sender_address}:{transfer.receiver_address}:{transfer.symbol}:{transfer.amount}:{transfer.timestamp}"

    if not verify_signature(transfer.sender_public_key, msg, transfer.signature):
         raise HTTPException(status_code=400, detail="Invalid signature")

    # 2. Atomic Balance Check & Update (CAS - Compare and Swap)
    # We update ONLY IF balance >= amount.
    result = await token_balances_col.update_one(
        {
            "address": transfer.sender_address,
            "symbol": transfer.symbol,
            "balance": {"$gte": transfer.amount} # ATOMIC CONDITION
        },
        {"$inc": {"balance": -transfer.amount}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Insufficient token balance (or race condition)")

    # 3. Add to receiver (Safe to just increment, no condition needed)
    await token_balances_col.update_one(
        {"address": transfer.receiver_address, "symbol": transfer.symbol},
        {"$inc": {"balance": transfer.amount}},
        upsert=True
    )

    # 4. Record transfer
    await token_transfers_col.insert_one(transfer.dict())

    return {"message": "Token transfer successful", "tx_id": f"tx_{time.time()}"}

@router.get("/list")
async def list_tokens():
    cursor = tokens_col.find()
    tokens = await cursor.to_list(length=100)
    return serialize_mongo(tokens)

@router.get("/{symbol}")
async def get_token(symbol: str):
    token = await tokens_col.find_one({"symbol": symbol})
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return serialize_mongo(token)

@router.get("/{symbol}/holders")
async def get_holders(symbol: str):
    cursor = token_balances_col.find({"symbol": symbol})
    holders = await cursor.to_list(length=100)
    return serialize_mongo(holders)
