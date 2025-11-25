from fastapi import APIRouter, HTTPException
from api.core.database import pools_col
from api.services.price_service import get_btc_price, get_ohlc_data
from api.core.utils import serialize_mongo

router = APIRouter()

@router.get("/ticker")
async def get_prices():
    """
    Returns the current price of BTC (in USD) and all Tokens (in BTC and USD).
    """
    btc_usd = await get_btc_price()

    # Get all pools to calculate token prices
    pools = await pools_col.find().to_list(length=100)

    token_prices = {}

    for pool in pools:
        symbol = pool["token_symbol"]
        res_native = pool["reserve_native"]
        res_token = pool["reserve_token"]

        if res_token > 0:
            price_btc = res_native / res_token
            price_usd = price_btc * btc_usd

            token_prices[symbol] = {
                "price_btc": price_btc,
                "price_usd": price_usd
            }

    return {
        "BTC": {"price_usd": btc_usd},
        "tokens": token_prices
    }

@router.get("/chart/{symbol}")
async def get_chart_data(symbol: str):
    """
    Returns OHLC (Open-High-Low-Close) data for a specific symbol (1-minute candles).
    For 'BTC', it returns the global BTC/USD price history.
    For Tokens, it returns Token/BTC price history.
    """
    data = await get_ohlc_data(symbol)
    return serialize_mongo(data)
