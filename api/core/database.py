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
orders_col = db.orders
trades_col = db.trades
