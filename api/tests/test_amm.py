import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from api.routers.amm import swap, add_liquidity
from api.models.market_models import SwapRequest, LiquidityAction

@pytest.mark.asyncio
@patch("api.routers.amm.pools_col")
@patch("api.routers.amm.token_balances_col")
@patch("api.routers.amm.utxo_col")
@patch("api.routers.amm.miner_fee_pot_col")
@patch("api.routers.amm.pool_history_col")
async def test_swap_native_to_token(mock_hist, mock_fee, mock_utxo, mock_bal, mock_pools):
    # Setup Pool
    # Reserve: 100 Native, 100 Token. Total Shares: 100
    pool_doc = {
        "_id": "pool1",
        "pair": "BTC-TKN",
        "token_symbol": "TKN",
        "reserve_native": 100.0,
        "reserve_token": 100.0,
        "total_shares": 100.0
    }
    mock_pools.find_one = AsyncMock(return_value=pool_doc)
    mock_pools.update_one = AsyncMock()

    # Critical: Mock the update_one method of token_balances_col to be awaitable
    mock_bal.update_one = AsyncMock()
    mock_utxo.insert_one = AsyncMock()
    mock_fee.update_one = AsyncMock()
    mock_hist.insert_one = AsyncMock()

    # Request: Swap 10 Native for Token
    # Fee (0.3%) = 0.03
    # Amount In (Pool) = 9.97
    # Amount Out = (9.97 * 100) / (100 + 9.97) = 997 / 109.97 ≈ 9.066

    req = SwapRequest(
        user_address="user1",
        pair="BTC-TKN",
        direction="native_to_token",
        amount_in=10.0,
        min_amount_out=0.0,
        signature="sig"
    )

    res = await swap(req)

    # Verify Math
    # assert res["amount_out"] around 9.066
    assert 9.0 < res["amount_out"] < 9.1

    # Verify Fee Pot Update (0.1% of 10 = 0.01)
    mock_fee.update_one.assert_called_once()

@pytest.mark.asyncio
@patch("api.routers.amm.pools_col")
@patch("api.routers.amm.token_balances_col")
async def test_add_liquidity(mock_bal, mock_pools):
    # Setup Pool
    pool_doc = {
        "_id": "pool1",
        "pair": "BTC-TKN",
        "token_symbol": "TKN",
        "reserve_native": 100.0,
        "reserve_token": 100.0,
        "total_shares": 100.0
    }
    mock_pools.find_one = AsyncMock(return_value=pool_doc)
    mock_pools.update_one = AsyncMock()
    mock_bal.update_one = AsyncMock()

    action = LiquidityAction(
        pair="BTC-TKN",
        user_address="user1",
        amount_native=10.0, # Should require 10.0 Token
        signature="sig"
    )

    res = await add_liquidity(action)

    # Shares minted = (10/100) * 100 = 10
    assert res["shares_minted"] == 10.0

    mock_pools.update_one.assert_called_once()
