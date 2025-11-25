import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from api.routers.amm import swap, add_liquidity
from api.models.market_models import SwapRequest, LiquidityAction
import time

@pytest.mark.asyncio
@patch("api.routers.amm.pools_col")
@patch("api.routers.amm.token_balances_col")
@patch("api.routers.amm.utxo_col")
@patch("api.routers.amm.miner_fee_pot_col")
@patch("api.services.price_service.global_state_col") # Add missing patch
@patch("api.services.price_service.price_history_col") # Add missing patch
@patch("api.routers.amm.pool_history_col")
async def test_swap_native_to_token(mock_ph, mock_phist, mock_gs, mock_fee, mock_utxo, mock_bal, mock_pools):
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

    # Mock update_one result (modified_count=1 for success)
    success_res = MagicMock()
    success_res.modified_count = 1
    mock_pools.update_one = AsyncMock(return_value=success_res)

    mock_bal.update_one = AsyncMock()
    mock_utxo.insert_one = AsyncMock()
    mock_fee.update_one = AsyncMock()

    # Pricing Service Mocks
    mock_gs.find_one = AsyncMock(return_value={"price_usd": 1.0})
    mock_gs.update_one = AsyncMock()
    mock_phist.insert_one = AsyncMock()
    mock_phist.update_one = AsyncMock()
    mock_ph.insert_one = AsyncMock()

    req = SwapRequest(
        user_address="user1",
        pair="BTC-TKN",
        direction="native_to_token",
        amount_in=10.0,
        min_amount_out=0.0,
        signature="sig",
        timestamp=time.time()
    )

    res = await swap(req)

    assert 9.0 < res["amount_out"] < 9.1
    mock_fee.update_one.assert_called_once()

@pytest.mark.asyncio
@patch("api.routers.amm.pools_col")
@patch("api.routers.amm.token_balances_col")
async def test_add_liquidity(mock_bal, mock_pools):
    pool_doc = {
        "_id": "pool1",
        "pair": "BTC-TKN",
        "token_symbol": "TKN",
        "reserve_native": 100.0,
        "reserve_token": 100.0,
        "total_shares": 100.0
    }
    mock_pools.find_one = AsyncMock(return_value=pool_doc)

    # Mock update_one result for success
    success_res = MagicMock()
    success_res.modified_count = 1
    mock_pools.update_one = AsyncMock(return_value=success_res)

    mock_bal.update_one = AsyncMock()

    action = LiquidityAction(
        pair="BTC-TKN",
        user_address="user1",
        amount_native=10.0,
        signature="sig",
        timestamp=time.time()
    )

    res = await add_liquidity(action)

    assert res["shares_minted"] == 10.0
    mock_pools.update_one.assert_called_once()
