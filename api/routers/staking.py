from fastapi import APIRouter, HTTPException, Body
from api.core.database import stakes_col, token_balances_col, utxo_col
from api.models.market_models import StakeRequest
from api.core.utils import serialize_mongo
import time

router = APIRouter()

APY = 0.05 # 5% Annual Percentage Yield

@router.post("/deposit")
async def stake_deposit(req: StakeRequest):
    # Verify signature
    # ... (Simplified)

    # Check Balance & Deduct
    if req.symbol == "BTC":
        # Check native balance (simplified)
        pass
    else:
        bal = await token_balances_col.find_one({"address": req.user_address, "symbol": req.symbol})
        if not bal or bal["balance"] < req.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        await token_balances_col.update_one(
            {"_id": bal["_id"]},
            {"$inc": {"balance": -req.amount}}
        )

    # Create Stake Position
    stake_doc = {
        "user_address": req.user_address,
        "symbol": req.symbol,
        "amount": req.amount,
        "start_time": time.time(),
        "duration_days": req.duration_days,
        "status": "active"
    }

    await stakes_col.insert_one(stake_doc)

    return serialize_mongo({"message": "Staked successfully", "stake": stake_doc})

@router.post("/withdraw")
async def stake_withdraw(stake_id: str = Body(..., embed=True), signature: str = Body(..., embed=True)):
    from bson import ObjectId
    try:
        oid = ObjectId(stake_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    stake = await stakes_col.find_one({"_id": oid})
    if not stake or stake["status"] != "active":
        raise HTTPException(status_code=400, detail="Stake not found or inactive")

    # Calculate Reward
    # Simple Interest: Principal * Rate * Time
    elapsed_seconds = time.time() - stake["start_time"]
    elapsed_years = elapsed_seconds / (365 * 24 * 3600)

    # In this fast simulation, let's treat 1 minute as 1 year for visible rewards?
    # Or just stick to realism. Let's stick to realism but return tiny amounts.

    reward = stake["amount"] * APY * elapsed_years
    total_return = stake["amount"] + reward

    # Update Stake Status
    await stakes_col.update_one({"_id": oid}, {"$set": {"status": "withdrawn", "end_time": time.time(), "reward": reward}})

    # Credit User
    if stake["symbol"] == "BTC":
        await utxo_col.insert_one({
            "txid": f"stake_return_{time.time()}",
            "vout": 0,
            "amount": total_return,
            "address": stake["user_address"]
        })
    else:
        await token_balances_col.update_one(
            {"address": stake["user_address"], "symbol": stake["symbol"]},
            {"$inc": {"balance": total_return}},
            upsert=True
        )

    return serialize_mongo({
        "message": "Unstaked successfully",
        "principal": stake["amount"],
        "reward": reward,
        "total": total_return
    })
