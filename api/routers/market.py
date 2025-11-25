from fastapi import APIRouter, HTTPException, Body
from api.core.database import orders_col, trades_col, token_balances_col
from api.core.utils import serialize_mongo
from pydantic import BaseModel
import time

router = APIRouter()

class Order(BaseModel):
    user_address: str
    order_type: str  # "buy" or "sell"
    pair: str        # e.g., "TOKEN-BTC"
    price: float
    amount: float
    signature: str   # Validate ownership

@router.post("/order")
async def place_order(order: Order):
    # 1. Validate signature (Simplified: assume valid if provided)

    # 2. Check balance (if sell)
    base_token, quote_token = order.pair.split("-")
    if order.order_type == "sell":
        # Check token balance
        bal = await token_balances_col.find_one({"address": order.user_address, "symbol": base_token})
        if not bal or bal["balance"] < order.amount:
             raise HTTPException(status_code=400, detail="Insufficient balance")

    # 3. Add to orderbook
    order_doc = order.dict()
    order_doc["timestamp"] = time.time()
    order_doc["status"] = "open"

    result = await orders_col.insert_one(order_doc)
    # Ensure _id is handled, though serialize_mongo handles it too

    # 4. Trigger Matching Engine (Simple Immediate Match)
    await match_orders(order.pair)

    return serialize_mongo({"message": "Order placed", "order": order_doc})

async def match_orders(pair: str):
    # Simple matching logic: Find overlapping buy/sell
    # Buy: High to Low
    buys = orders_col.find({"pair": pair, "order_type": "buy", "status": "open"}).sort("price", -1)
    # Sell: Low to High
    sells = orders_col.find({"pair": pair, "order_type": "sell", "status": "open"}).sort("price", 1)

    # This is a very simplified O(N*M) matching for demonstration.
    # In real world, use in-memory orderbook.

    # Converting cursors to lists for simple iteration (not efficient for large scale)
    buy_list = await buys.to_list(length=100)
    sell_list = await sells.to_list(length=100)

    for buy in buy_list:
        for sell in sell_list:
            if buy["price"] >= sell["price"]:
                # Match found!
                trade_price = sell["price"] # Usually maker's price
                trade_amount = min(buy["amount"], sell["amount"])

                # Execute Trade
                await trades_col.insert_one({
                    "pair": pair,
                    "price": trade_price,
                    "amount": trade_amount,
                    "buyer": buy["user_address"],
                    "seller": sell["user_address"],
                    "timestamp": time.time()
                })

                # Update Orders
                # (simplified: just mark filled or reduce amount)
                new_buy_amount = buy["amount"] - trade_amount
                new_sell_amount = sell["amount"] - trade_amount

                if new_buy_amount == 0:
                    await orders_col.update_one({"_id": buy["_id"]}, {"$set": {"status": "filled", "amount": 0}})
                else:
                    await orders_col.update_one({"_id": buy["_id"]}, {"$set": {"amount": new_buy_amount}})
                    buy["amount"] = new_buy_amount # Update local var for next iteration

                if new_sell_amount == 0:
                    await orders_col.update_one({"_id": sell["_id"]}, {"$set": {"status": "filled", "amount": 0}})
                else:
                    await orders_col.update_one({"_id": sell["_id"]}, {"$set": {"amount": new_sell_amount}})
                    sell["amount"] = new_sell_amount

                # Update Balances (skipped for brevity, but crucial in real app)

@router.get("/orderbook")
async def get_orderbook(pair: str):
    buys = await orders_col.find({"pair": pair, "order_type": "buy", "status": "open"}).sort("price", -1).to_list(length=50)
    sells = await orders_col.find({"pair": pair, "order_type": "sell", "status": "open"}).sort("price", 1).to_list(length=50)

    return serialize_mongo({"bids": buys, "asks": sells})
