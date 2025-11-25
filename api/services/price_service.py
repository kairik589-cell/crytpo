from api.core.database import global_state_col, price_history_col
import time
from api.core.utils import serialize_mongo

async def init_price():
    state = await global_state_col.find_one({"_id": "btc_price"})
    if not state:
        await global_state_col.insert_one({
            "_id": "btc_price",
            "price_usd": 1.0, # Initial peg
            "last_updated": time.time()
        })

async def get_btc_price():
    state = await global_state_col.find_one({"_id": "btc_price"})
    if state:
        return state.get("price_usd", 1.0)
    return 1.0

async def update_btc_price(direction: str, volume: float):
    """
    Updates BTC price based on market pressure.
    direction: "buy" (Token->BTC) or "sell" (BTC->Token)
    volume: Amount of BTC involved
    """
    current = await get_btc_price()

    # Sensitivity factor: How much price moves per unit of volume
    # For simulation, let's say 1 BTC volume moves price by 0.01%
    sensitivity = 0.0001

    change = volume * sensitivity * current

    new_price = current
    if direction == "buy":
        new_price += change
    else:
        new_price -= change

    # Prevent negative or zero price
    if new_price < 0.01:
        new_price = 0.01

    await global_state_col.update_one(
        {"_id": "btc_price"},
        {"$set": {"price_usd": new_price, "last_updated": time.time()}},
        upsert=True
    )

    # Record BTC OHLC (Native Price)
    await record_ohlc("BTC", new_price, volume)

    return new_price

async def record_ohlc(symbol: str, price: float, volume: float):
    """
    Records price data bucketed by minute.
    """
    timestamp = time.time()
    minute_bucket = int(timestamp // 60) * 60 # Floor to nearest minute

    # Check if bucket exists
    bucket_id = f"{symbol}_{minute_bucket}"

    existing = await price_history_col.find_one({"_id": bucket_id})

    if existing:
        # Update OHLC
        update_fields = {
            "close": price,
            "volume": existing["volume"] + volume,
            "high": max(existing["high"], price),
            "low": min(existing["low"], price)
        }
        await price_history_col.update_one({"_id": bucket_id}, {"$set": update_fields})
    else:
        # Create new candle
        doc = {
            "_id": bucket_id,
            "symbol": symbol,
            "timestamp": minute_bucket,
            "open": price,
            "high": price,
            "low": price,
            "close": price,
            "volume": volume
        }
        await price_history_col.insert_one(doc)

async def get_ohlc_data(symbol: str, limit: int = 60):
    cursor = price_history_col.find({"symbol": symbol}).sort("timestamp", -1).limit(limit)
    data = await cursor.to_list(length=limit)
    # Sort chronological for chart
    data.reverse()
    return serialize_mongo(data)
