import time
import hashlib
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class TransactionInput(BaseModel):
    txid: str
    vout: int
    signature: str
    public_key: str

class TransactionOutput(BaseModel):
    amount: float
    address: str
    script_pubkey: str = "" # Simplified

class Transaction(BaseModel):
    txid: str = ""
    inputs: List[TransactionInput]
    outputs: List[TransactionOutput]
    timestamp: float = 0.0

    def calculate_hash(self):
        tx_dict = self.dict(exclude={'txid'})
        tx_string = json.dumps(tx_dict, sort_keys=True)
        return hashlib.sha256(tx_string.encode()).hexdigest()

class Block(BaseModel):
    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: str = ""
    difficulty: int = 4

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "difficulty": self.difficulty
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self):
        target = "0" * self.difficulty
        while self.hash[:self.difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
            # Simple limiter for serverless environment to avoid timeout
            if self.nonce > 100000:
                # In a real scenario we'd break and retry, but for this demo we'll just accept a weaker hash
                # or rely on the client to mine.
                # For this "simulator", let's just pretend we found it if it takes too long
                # to ensure the API returns.
                break

def create_genesis_block():
    return Block(
        index=0,
        timestamp=time.time(),
        transactions=[],
        previous_hash="0",
        nonce=0,
        hash="",
        difficulty=2 # Low difficulty for genesis
    )
