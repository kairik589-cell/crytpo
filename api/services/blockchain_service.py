from api.core.database import blocks_col, utxo_col, mempool_col
from api.core.blockchain_models import Block, Transaction, TransactionInput, TransactionOutput, create_genesis_block
import time

async def get_last_block():
    last_block = await blocks_col.find_one(sort=[("index", -1)])
    if not last_block:
        return None
    return Block(**last_block)

async def init_chain():
    if await blocks_col.count_documents({}) == 0:
        genesis = create_genesis_block()
        genesis.hash = genesis.calculate_hash()
        await blocks_col.insert_one(genesis.dict())
        return True
    return False

async def add_block(block: Block):
    # Verify previous hash
    last_block = await get_last_block()
    if last_block and block.previous_hash != last_block.hash:
        raise ValueError("Invalid previous hash")

    await blocks_col.insert_one(block.dict())

    # Update UTXOs
    for tx in block.transactions:
        # Remove spent outputs
        for inp in tx.inputs:
            await utxo_col.delete_one({"txid": inp.txid, "vout": inp.vout})

        # Add new outputs
        for i, out in enumerate(tx.outputs):
            await utxo_col.insert_one({
                "txid": tx.txid,
                "vout": i,
                "amount": out.amount,
                "address": out.address
            })

    # Clear mempool
    txids = [tx.txid for tx in block.transactions]
    if txids:
        await mempool_col.delete_many({"txid": {"$in": txids}})

async def get_balance(address: str):
    pipeline = [
        {"$match": {"address": address}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    cursor = utxo_col.aggregate(pipeline)
    result = await cursor.to_list(length=1)
    if result:
        return result[0]["total"]
    return 0.0

async def get_utxos(address: str):
    cursor = utxo_col.find({"address": address})
    return await cursor.to_list(length=None)
