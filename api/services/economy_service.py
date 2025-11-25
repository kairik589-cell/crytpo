from api.core.database import tokens_col, token_balances_col, pools_col
import time

ADMIN_ADDRESS = "admin_wallet_001"

async def init_economy():
    """
    Initializes the simulated economy:
    1. Creates USDT (Stablecoin).
    2. Mints USDT to Admin.
    3. Creates BTC-USDT Pool to anchor price.
    """

    # 1. Create USDT if not exists
    usdt = await tokens_col.find_one({"symbol": "USDT"})
    if not usdt:
        await tokens_col.insert_one({
            "name": "Tether USD",
            "symbol": "USDT",
            "total_supply": 1_000_000_000.0,
            "owner_address": ADMIN_ADDRESS,
            "created_at": time.time()
        })
        # Mint to Admin
        await token_balances_col.update_one(
            {"address": ADMIN_ADDRESS, "symbol": "USDT"},
            {"$set": {"balance": 1_000_000_000.0}},
            upsert=True
        )

    # 2. Create Initial BTC-USDT Pool (Price Anchor)
    # Let's assume Admin also has some BTC (Native).
    # In this sim, we just "create" the pool reserves directly for bootstrapping.
    # Price: 1 BTC = 50,000 USDT
    pair = "BTC-USDT"
    pool = await pools_col.find_one({"pair": pair})
    if not pool:
        # Initial Liquidity: 10 BTC + 500,000 USDT
        await pools_col.insert_one({
            "pair": pair,
            "token_symbol": "USDT",
            "reserve_native": 10.0,    # 10 BTC
            "reserve_token": 500_000.0, # 500k USDT
            "total_shares": 10.0,
            "created_at": time.time()
        })

        # Give Admin LP tokens
        await token_balances_col.update_one(
            {"address": ADMIN_ADDRESS, "symbol": f"LP-{pair}"},
            {"$set": {"balance": 10.0}},
            upsert=True
        )
