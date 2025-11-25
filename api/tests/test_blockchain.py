import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from api.core.blockchain_models import Block, Transaction
from api.services import blockchain_service

@pytest.mark.asyncio
async def test_block_hashing():
    block = Block(
        index=0,
        timestamp=1234567890,
        transactions=[],
        previous_hash="0",
        nonce=0,
        difficulty=1
    )
    hash1 = block.calculate_hash()
    assert hash1 is not None

    block.nonce += 1
    hash2 = block.calculate_hash()
    assert hash1 != hash2

@pytest.mark.asyncio
async def test_mining():
    block = Block(
        index=1,
        timestamp=1234567890,
        transactions=[],
        previous_hash="000",
        nonce=0,
        difficulty=2
    )
    block.mine_block()
    assert block.hash.startswith("00")

@pytest.mark.asyncio
@patch("api.services.blockchain_service.blocks_col")
@patch("api.services.blockchain_service.utxo_col")
async def test_add_block(mock_utxo, mock_blocks):
    # Mock last block
    last_block_dict = {
        "index": 0, "timestamp": 0, "transactions": [], "previous_hash": "0", "nonce": 0, "hash": "abc", "difficulty": 2
    }
    mock_blocks.find_one = AsyncMock(return_value=last_block_dict)
    mock_blocks.insert_one = AsyncMock()

    new_block = Block(
        index=1,
        timestamp=1,
        transactions=[],
        previous_hash="abc",
        difficulty=2
    )
    new_block.mine_block()

    await blockchain_service.add_block(new_block)
    mock_blocks.insert_one.assert_called_once()
