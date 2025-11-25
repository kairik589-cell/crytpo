from fastapi import APIRouter, HTTPException, Body
from api.core.database import (
    utxo_col, tx_col, token_transfers_col,
    token_balances_col, tokens_col, pool_history_col,
    mining_stats_col, blocks_col
)
from api.core.utils import serialize_mongo
import time

router = APIRouter()

# 1. Faucet
@router.post("/faucet")
async def faucet(address: str = Body(..., embed=True)):
    # Limit logic skipped for demo
    amount = 10.0
    await utxo_col.insert_one({
        "txid": f"faucet_{time.time()}",
        "vout": 0,
        "amount": amount,
        "address": address
    })
    return {"message": f"Sent {amount} coins to {address}"}

# 2. Wallet History
@router.get("/wallet/{address}/history")
async def wallet_history(address: str):
    # Native TXs (simplified view)
    # Token Transfers
    transfers = await token_transfers_col.find({
        "$or": [{"sender_address": address}, {"receiver_address": address}]
    }).sort("timestamp", -1).to_list(length=50)

    return serialize_mongo({"history": transfers})

# 3. Token Burn
@router.post("/token/burn")
async def token_burn(symbol: str = Body(...), amount: float = Body(...), address: str = Body(...)):
    bal = await token_balances_col.find_one({"address": address, "symbol": symbol})
    if not bal or bal["balance"] < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    await token_balances_col.update_one(
        {"_id": bal["_id"]},
        {"$inc": {"balance": -amount}}
    )

    # Update total supply in token metadata
    await tokens_col.update_one(
        {"symbol": symbol},
        {"$inc": {"total_supply": -amount}}
    )
    return {"message": f"Burned {amount} {symbol}"}

# 4. Token Update
@router.post("/token/update")
async def token_update(symbol: str = Body(...), description: str = Body(...), website: str = Body(...)):
    # Verify owner (skipped)
    await tokens_col.update_one(
        {"symbol": symbol},
        {"$set": {"description": description, "website": website}}
    )
    return {"message": "Token updated"}

# 5. Rich List
@router.get("/token/{symbol}/richlist")
async def rich_list(symbol: str):
    holders = await token_balances_col.find({"symbol": symbol}).sort("balance", -1).limit(10).to_list(length=10)
    return serialize_mongo(holders)

# 6. Market Stats
@router.get("/market/stats")
async def market_stats():
    # 24h Volume (from pool history)
    cutoff = time.time() - 86400
    cursor = pool_history_col.aggregate([
        {"$match": {"timestamp": {"$gte": cutoff}}},
        {"$group": {"_id": None, "total_volume": {"$sum": "$volume"}}}
    ])
    res = await cursor.to_list(length=1)
    vol = res[0]["total_volume"] if res else 0.0
    return {"volume_24h": vol}

# 7. Miner Leaderboard (Mocked/Simplified)
@router.get("/miner/leaderboard")
async def miner_leaderboard():
    # In real app, aggregate from blocks collection by 'miner_address' in coinbase tx
    # Since our block model stores txs as objects, aggregation is complex.
    # Return placeholder
    return {"leaderboard": [{"address": "miner1", "blocks": 42}]}

# 8. Chart Data
@router.get("/market/chart/{pair}")
async def chart_data(pair: str):
    data = await pool_history_col.find({"pair": pair}).sort("timestamp", 1).limit(100).to_list(length=100)
    return serialize_mongo(data)

# 9. Health Check
@router.get("/system/health")
async def health_check():
    return {"status": "online", "timestamp": time.time()}

# 10. Network Stats
@router.get("/network/stats")
async def network_stats():
    count = await blocks_col.count_documents({})
    return {"block_height": count}
