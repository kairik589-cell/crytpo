from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from api.routers import tokens, amm, staking, extras, prices
from api.services import wallet_service, blockchain_service, price_service, economy_service
from api.core.blockchain_models import Block, Transaction, create_genesis_block
from api.core.utils import serialize_mongo
import time

app = FastAPI(title="Bitcoin Clone + DeFi (AMM & Staking)", version="2.1.0")

# Register Routers
app.include_router(tokens.router, prefix="/token", tags=["Token Layer"])
app.include_router(amm.router, prefix="/market", tags=["Marketplace (AMM)"])
app.include_router(staking.router, prefix="/staking", tags=["Staking"])
app.include_router(prices.router, prefix="/price", tags=["Pricing & Charts"])
app.include_router(extras.router, tags=["Extras"])

@app.on_event("startup")
async def startup_event():
    # Ensure genesis block exists
    await blockchain_service.init_chain()
    # Ensure initial price exists
    await price_service.init_price()
    # Initialize Economy (USDT + Price Anchor)
    await economy_service.init_economy()

@app.get("/")
def read_root():
    return {"message": "Bitcoin Clone + DeFi API is running. Use /docs for documentation."}

# Wallet Endpoints
@app.post("/wallet/new")
def create_wallet():
    wallet = wallet_service.generate_wallet()
    return wallet.dict()

@app.get("/wallet/{address}")
async def get_wallet_balance(address: str):
    balance = await blockchain_service.get_balance(address)
    utxos = await blockchain_service.get_utxos(address)
    # Use serialize_mongo to handle _id in utxos
    return serialize_mongo({"address": address, "balance": balance, "utxos": utxos})

# Blockchain Endpoints
@app.get("/chain/state")
async def get_chain_state():
    last_block = await blockchain_service.get_last_block()
    return serialize_mongo({"height": last_block.index if last_block else 0, "last_hash": last_block.hash if last_block else ""})

@app.post("/mine")
async def mine_block(miner_address: str = "miner1"):
    last_block = await blockchain_service.get_last_block()
    if not last_block:
        return {"error": "Chain not initialized"}

    # 1. Calculate Reward (Block Reward Only)
    block_reward = 50.0
    # Fees now go to ADMIN wallet directly during swap, not here.

    # Create CoinBase Transaction
    coinbase_tx = Transaction(
        inputs=[],
        outputs=[{"amount": block_reward, "address": miner_address}],
        timestamp=time.time()
    )
    coinbase_tx.txid = coinbase_tx.calculate_hash()

    # Create Block
    new_block = Block(
        index=last_block.index + 1,
        timestamp=time.time(),
        transactions=[coinbase_tx],
        previous_hash=last_block.hash,
        difficulty=last_block.difficulty
    )

    # Mine (PoW)
    new_block.mine_block()

    # Add to chain
    await blockchain_service.add_block(new_block)

    return serialize_mongo({
        "message": "Block mined",
        "block": new_block.dict(),
        "reward_breakdown": {
            "base": block_reward,
            "fees": 0.0, # Fees go to Admin
            "total": block_reward
        }
    })

@app.get("/block/{hash}")
async def get_block(hash: str):
    # This is a placeholder. In real implementation we'd query by hash
    # For now let's just return the last block if it matches, to save time on query impl
    last = await blockchain_service.get_last_block()
    if last and last.hash == hash:
        return serialize_mongo(last.dict())
    return {"error": "Block not found (simulator limited)"}

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)},
    )
