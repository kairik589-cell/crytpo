import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from api.routers.amm import swap
from api.models.market_models import SwapRequest
import time

@pytest.mark.asyncio
@patch("api.routers.amm.pools_col")
@patch("api.routers.amm.token_balances_col")
@patch("api.routers.amm.utxo_col")
@patch("api.services.price_service.global_state_col")
@patch("api.services.price_service.price_history_col")
async def test_swap_optimistic_retry(mock_hist, mock_state, mock_utxo, mock_bal, mock_pools):
    # Setup Pool
    pool_doc = {
        "_id": "pool1", "pair": "BTC-TKN", "token_symbol": "TKN",
        "reserve_native": 100.0, "reserve_token": 100.0, "total_shares": 100.0
    }

    mock_pools.find_one = AsyncMock(return_value=pool_doc)

    # Mock update_one to FAIL first time, SUCCESS second time
    fail_res = MagicMock()
    fail_res.modified_count = 0
    success_res = MagicMock()
    success_res.modified_count = 1

    async def first_call(*args, **kwargs):
        return fail_res

    async def second_call(*args, **kwargs):
        return success_res

    mock_pools.update_one.side_effect = [first_call(), second_call()]

    mock_utxo.insert_one = AsyncMock()
    mock_bal.update_one = AsyncMock()
    mock_state.find_one = AsyncMock(return_value={"price_usd": 1.0})
    mock_state.update_one = AsyncMock()

    # Use current time to pass validation
    req = SwapRequest(
        user_address="u1", pair="BTC-TKN", direction="native_to_token",
        amount_in=10.0, min_amount_out=0.0, timestamp=time.time(), signature="sig"
    )

    res = await swap(req)

    assert res["message"] == "Swap successful"
    assert mock_pools.update_one.call_count == 2

@pytest.mark.asyncio
async def test_negative_input_validation():
    try:
        SwapRequest(
            user_address="u1", pair="BTC-TKN", direction="native_to_token",
            amount_in=-10.0, min_amount_out=0.0, timestamp=time.time(), signature="sig"
        )
        assert False, "Should raise Validation Error"
    except ValueError:
        assert True
