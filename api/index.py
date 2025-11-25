from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from api.routers import tokens, market
from api.services import wallet_service, blockchain_service
from api.core.blockchain_models import Block, Transaction, create_genesis_block

app = FastAPI(title="Bitcoin Clone + Token Layer", version="1.0.0")

# Register Routers
app.include_router(tokens.router, prefix="/token", tags=["Token Layer"])
app.include_router(market.router, prefix="/market", tags=["Marketplace"])

@app.on_event("startup")
async def startup_event():
    # Ensure genesis block exists
    await blockchain_service.init_chain()

@app.get("/")
def read_root():
    return {"message": "Bitcoin Clone API is running. Use /docs for documentation."}

# Wallet Endpoints
@app.post("/wallet/new")
def create_wallet():
    wallet = wallet_service.generate_wallet()
    return wallet.dict()

@app.get("/wallet/{address}")
async def get_wallet_balance(address: str):
    balance = await blockchain_service.get_balance(address)
    utxos = await blockchain_service.get_utxos(address)
    for u in utxos: u["_id"] = str(u["_id"])
    return {"address": address, "balance": balance, "utxos": utxos}

# Blockchain Endpoints
@app.get("/chain/state")
async def get_chain_state():
    last_block = await blockchain_service.get_last_block()
    return {"height": last_block.index if last_block else 0, "last_hash": last_block.hash if last_block else ""}

@app.post("/mine")
async def mine_block(miner_address: str = "miner1"):
    last_block = await blockchain_service.get_last_block()
    if not last_block:
        return {"error": "Chain not initialized"}

    # Create CoinBase Transaction
    coinbase_tx = Transaction(
        inputs=[],
        outputs=[{"amount": 50.0, "address": miner_address}],
        timestamp=0 # Simplified
    )
    coinbase_tx.txid = coinbase_tx.calculate_hash()

    # Create Block
    new_block = Block(
        index=last_block.index + 1,
        timestamp=0, # Use current time in model
        transactions=[coinbase_tx],
        previous_hash=last_block.hash,
        difficulty=last_block.difficulty
    )

    # Mine (PoW)
    new_block.mine_block()

    # Add to chain
    await blockchain_service.add_block(new_block)

    return {"message": "Block mined", "block": new_block.dict()}

@app.get("/block/{hash}")
async def get_block(hash: str):
    # This is a placeholder. In real implementation we'd query by hash
    # For now let's just return the last block if it matches, to save time on query impl
    last = await blockchain_service.get_last_block()
    if last and last.hash == hash:
        return last.dict()
    return {"error": "Block not found (simulator limited)"}

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": str(exc)},
    )
