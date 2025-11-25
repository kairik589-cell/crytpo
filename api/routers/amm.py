from fastapi import APIRouter, HTTPException, Body
from api.core.database import (
    pools_col, token_balances_col, utxo_col,
    miner_fee_pot_col, pool_history_col, token_transfers_col
)
from api.models.market_models import PoolCreate, LiquidityAction, SwapRequest
from api.services.wallet_service import verify_signature
from api.core.utils import serialize_mongo
import time

router = APIRouter()

FEE_TOTAL = 0.003 # 0.3%
FEE_LP = 0.002    # 0.2% goes to pool
FEE_MINER = 0.001 # 0.1% goes to miners

@router.post("/pool/create")
async def create_pool(data: PoolCreate):
    # Check if pool exists
    pair = f"BTC-{data.token_symbol}"
    existing = await pools_col.find_one({"pair": pair})
    if existing:
        raise HTTPException(status_code=400, detail="Pool already exists")

    # Verify Balance & Signature (Simplified)
    # In real app: verify UTXOs for native and token balance

    # Initialize Pool
    pool_doc = {
        "pair": pair,
        "token_symbol": data.token_symbol,
        "reserve_native": data.initial_native,
        "reserve_token": data.initial_token,
        "total_shares": data.initial_native, # Initial shares = initial native (simplified)
        "created_at": time.time()
    }

    await pools_col.insert_one(pool_doc)

    # Give creator LP tokens (Shares)
    # We store LP shares in token_balances with a special symbol "LP-BTC-{SYMBOL}"
    lp_symbol = f"LP-{pair}"
    await token_balances_col.update_one(
        {"address": data.creator_address, "symbol": lp_symbol},
        {"$inc": {"balance": data.initial_native}},
        upsert=True
    )

    # Deduct User Assets (Simulator logic: we assume they deposited valid funds)
    # Native deduct:
    # await utxo_col.delete_many(...) # Complex for native, simplified for demo

    # Token deduct:
    await token_balances_col.update_one(
        {"address": data.creator_address, "symbol": data.token_symbol},
        {"$inc": {"balance": -data.initial_token}}
    )

    return serialize_mongo({"message": "Pool created", "pool": pool_doc})

@router.post("/liquidity/add")
async def add_liquidity(data: LiquidityAction):
    pool = await pools_col.find_one({"pair": data.pair})
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")

    # Calculate required amounts based on ratio
    # If providing Native, calculate Token needed
    # amount_token = amount_native * (reserve_token / reserve_native)

    current_native = pool["reserve_native"]
    current_token = pool["reserve_token"]

    amount_native = data.amount_native
    amount_token = data.amount_native * (current_token / current_native)

    # Check User Balances (Skip for demo brevity, assume valid)

    # Calculate Shares to mint
    # shares = (amount_native / reserve_native) * total_shares
    shares_minted = (amount_native / current_native) * pool["total_shares"]

    # Update Pool
    await pools_col.update_one(
        {"_id": pool["_id"]},
        {
            "$inc": {
                "reserve_native": amount_native,
                "reserve_token": amount_token,
                "total_shares": shares_minted
            }
        }
    )

    # Give User LP Tokens
    lp_symbol = f"LP-{data.pair}"
    await token_balances_col.update_one(
        {"address": data.user_address, "symbol": lp_symbol},
        {"$inc": {"balance": shares_minted}},
        upsert=True
    )

    return serialize_mongo({"message": "Liquidity added", "shares_minted": shares_minted})

@router.post("/swap")
async def swap(req: SwapRequest):
    pool = await pools_col.find_one({"pair": req.pair})
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")

    reserve_in = 0.0
    reserve_out = 0.0

    if req.direction == "native_to_token":
        reserve_in = pool["reserve_native"]
        reserve_out = pool["reserve_token"]
    else:
        reserve_in = pool["reserve_token"]
        reserve_out = pool["reserve_native"]

    # Constant Product Formula: x * y = k
    # Amount Out = (Amount In * 997 * Reserve Out) / (Reserve In * 1000 + Amount In * 997)
    # (Using 0.3% fee)

    amount_in_with_fee = req.amount_in * (1 - FEE_TOTAL)
    numerator = amount_in_with_fee * reserve_out
    denominator = reserve_in + amount_in_with_fee
    amount_out = numerator / denominator

    if amount_out < req.min_amount_out:
        raise HTTPException(status_code=400, detail=f"Slippage too high. Output: {amount_out}")

    # Fee Distribution
    # FEE_MINER (0.1%) goes to Pot
    fee_miner = req.amount_in * FEE_MINER
    await miner_fee_pot_col.update_one(
        {"_id": "global_pot"},
        {"$inc": {"amount": fee_miner}},
        upsert=True
    )

    # Update Pool Reserves
    # Pool gets the LP fee implicitly because the constant k grows
    # We add the FULL amount_in to reserve (minus miner fee if separated, but strictly k grows by LP fee)
    # Simplified: Add amount_in (less miner fee) to In-Reserve, Subtract amount_out from Out-Reserve

    amount_in_pool = req.amount_in - fee_miner

    update_query = {}
    if req.direction == "native_to_token":
        update_query = {
            "$inc": {
                "reserve_native": amount_in_pool,
                "reserve_token": -amount_out
            }
        }
    else:
         update_query = {
            "$inc": {
                "reserve_token": amount_in_pool,
                "reserve_native": -amount_out
            }
        }

    await pools_col.update_one({"_id": pool["_id"]}, update_query)

    # Update User Balances
    # 1. Deduct Input
    if req.direction == "native_to_token":
        # Deduct Native (Simplified: assume valid UTXO consolidation)
        # In real app, we'd delete UTXOs. Here we just assume wallet service handles it or valid signature.
        pass
    else:
        # Deduct Token
        await token_balances_col.update_one(
            {"address": req.user_address, "symbol": pool["token_symbol"]},
            {"$inc": {"balance": -req.amount_in}}
        )

    # 2. Credit Output
    if req.direction == "native_to_token":
        # Credit Token
        await token_balances_col.update_one(
            {"address": req.user_address, "symbol": pool["token_symbol"]},
            {"$inc": {"balance": amount_out}},
            upsert=True
        )
    else:
        # Credit Native (Create UTXO)
        await utxo_col.insert_one({
            "txid": f"swap_{time.time()}",
            "vout": 0,
            "amount": amount_out,
            "address": req.user_address
        })

    # Record Stats
    await pool_history_col.insert_one({
        "pair": req.pair,
        "price": amount_out / req.amount_in, # simplified price
        "timestamp": time.time(),
        "volume": req.amount_in
    })

    return serialize_mongo({"message": "Swap successful", "amount_out": amount_out})

@router.get("/pools")
async def list_pools():
    pools = await pools_col.find().to_list(length=100)
    return serialize_mongo(pools)
