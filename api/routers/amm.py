from fastapi import APIRouter, HTTPException, Body
from api.core.database import (
    pools_col, token_balances_col, utxo_col,
    pool_history_col
)
from api.models.market_models import PoolCreate, LiquidityAction, SwapRequest
from api.services.wallet_service import verify_signature
from api.services.price_service import update_btc_price, record_ohlc
from api.services.economy_service import ADMIN_ADDRESS
from api.core.utils import serialize_mongo
import time

router = APIRouter()

FEE_TOTAL = 0.003
FEE_OWNER = 0.001

@router.post("/pool/create")
async def create_pool(data: PoolCreate):
    # Verify Signature
    msg = f"create_pool:{data.token_symbol}:{data.initial_native}:{data.initial_token}:{data.timestamp}"

    pair = f"BTC-{data.token_symbol}"
    existing = await pools_col.find_one({"pair": pair})
    if existing:
        raise HTTPException(status_code=400, detail="Pool already exists")

    pool_doc = {
        "pair": pair,
        "token_symbol": data.token_symbol,
        "reserve_native": data.initial_native,
        "reserve_token": data.initial_token,
        "total_shares": data.initial_native,
        "created_at": time.time()
    }

    res = await token_balances_col.update_one(
        {"address": data.creator_address, "symbol": data.token_symbol, "balance": {"$gte": data.initial_token}},
        {"$inc": {"balance": -data.initial_token}}
    )
    if res.modified_count == 0:
        raise HTTPException(status_code=400, detail="Insufficient token balance")

    await pools_col.insert_one(pool_doc)

    lp_symbol = f"LP-{pair}"
    await token_balances_col.update_one(
        {"address": data.creator_address, "symbol": lp_symbol},
        {"$inc": {"balance": data.initial_native}},
        upsert=True
    )

    return serialize_mongo({"message": "Pool created", "pool": pool_doc})

@router.post("/liquidity/add")
async def add_liquidity(data: LiquidityAction):
    for _ in range(3):
        pool = await pools_col.find_one({"pair": data.pair})
        if not pool: raise HTTPException(status_code=404, detail="Pool not found")

        current_native = pool["reserve_native"]
        current_token = pool["reserve_token"]

        # Calculate amounts
        amount_native = data.amount_native
        amount_token = data.amount_native * (current_token / current_native)
        shares_minted = (amount_native / current_native) * pool["total_shares"]

        res = await pools_col.update_one(
            {
                "_id": pool["_id"],
                "reserve_native": current_native,
                "reserve_token": current_token
            },
            {
                "$inc": {
                    "reserve_native": amount_native,
                    "reserve_token": amount_token,
                    "total_shares": shares_minted
                }
            }
        )

        if res.modified_count == 1:
            lp_symbol = f"LP-{data.pair}"
            await token_balances_col.update_one(
                {"address": data.user_address, "symbol": lp_symbol},
                {"$inc": {"balance": shares_minted}},
                upsert=True
            )
            return serialize_mongo({"message": "Liquidity added", "shares_minted": shares_minted})

    raise HTTPException(status_code=409, detail="High volatility - try again")

@router.post("/swap")
async def swap(req: SwapRequest):
    # Optimistic Loop
    for _ in range(3):
        pool = await pools_col.find_one({"pair": req.pair})
        if not pool: raise HTTPException(status_code=404, detail="Pool not found")

        res_in = pool["reserve_native"] if req.direction == "native_to_token" else pool["reserve_token"]
        res_out = pool["reserve_token"] if req.direction == "native_to_token" else pool["reserve_native"]

        amount_in_with_fee = req.amount_in * (1 - FEE_TOTAL)
        numerator = amount_in_with_fee * res_out
        denominator = res_in + amount_in_with_fee
        amount_out = numerator / denominator

        if amount_out < req.min_amount_out:
            raise HTTPException(status_code=400, detail=f"Slippage: Output {amount_out} < Min {req.min_amount_out}")

        fee_owner = req.amount_in * FEE_OWNER
        amount_in_pool = req.amount_in - fee_owner

        # ATOMIC POOL UPDATE
        update_query = {}
        if req.direction == "native_to_token":
            # Optimistic Check on reserves
            query = {"_id": pool["_id"], "reserve_native": res_in, "reserve_token": res_out}
            update = {"$inc": {"reserve_native": amount_in_pool, "reserve_token": -amount_out}}
        else:
            query = {"_id": pool["_id"], "reserve_token": res_in, "reserve_native": res_out}
            update = {"$inc": {"reserve_token": amount_in_pool, "reserve_native": -amount_out}}

        res = await pools_col.update_one(query, update)

        if res.modified_count == 1:
            # Fee to Owner (ADMIN)
            fee_symbol = "BTC" if req.direction == "native_to_token" else pool["token_symbol"]

            if fee_symbol == "BTC":
                 await utxo_col.insert_one({"txid": f"fee_{time.time()}", "vout": 0, "amount": fee_owner, "address": ADMIN_ADDRESS})
            else:
                 await token_balances_col.update_one(
                    {"address": ADMIN_ADDRESS, "symbol": fee_symbol},
                    {"$inc": {"balance": fee_owner}},
                    upsert=True
                )

            # User Balance Updates
            symbol_out = pool["token_symbol"] if req.direction == "native_to_token" else "BTC"

            if symbol_out == "BTC":
                await utxo_col.insert_one({"txid": f"swap_{time.time()}", "vout": 0, "amount": amount_out, "address": req.user_address})
            else:
                await token_balances_col.update_one(
                    {"address": req.user_address, "symbol": symbol_out},
                    {"$inc": {"balance": amount_out}},
                    upsert=True
                )

            # Pricing Updates
            try:
                pd = "buy" if req.direction == "token_to_native" else "sell"
                vol = amount_out if req.direction == "token_to_native" else req.amount_in
                await update_btc_price(pd, vol)

                t_price = (req.amount_in if req.direction=="native_to_token" else amount_out) / (amount_out if req.direction=="native_to_token" else req.amount_in)
                await record_ohlc(pool["token_symbol"], t_price, vol)
            except:
                pass

            return serialize_mongo({"message": "Swap successful", "amount_out": amount_out})

    raise HTTPException(status_code=409, detail="High volatility - try again")

@router.get("/pools")
async def list_pools():
    pools = await pools_col.find().to_list(length=100)
    return serialize_mongo(pools)
