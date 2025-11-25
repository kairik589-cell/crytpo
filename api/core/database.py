import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URI = "mongodb+srv://Vercel-Admin-data:Bhkxu4nxHIvG2kPJ@data.ecs0ces.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "bitcoin_clone_db"

client = AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]

# Collections
blocks_col = db.blocks
tx_col = db.transactions
utxo_col = db.utxos
mempool_col = db.mempool
tokens_col = db.tokens
token_balances_col = db.token_balances
token_transfers_col = db.token_transfers

# Market (AMM)
pools_col = db.pools
pool_history_col = db.pool_history

# Staking
stakes_col = db.stakes

# Stats & Mining
mining_stats_col = db.mining_stats
miner_fee_pot_col = db.miner_fee_pot # Stores accumulated fees waiting to be mined

# Deprecated/Legacy (kept if needed)
orders_col = db.orders
trades_col = db.trades
