import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from api.services.price_service import update_btc_price

@pytest.mark.asyncio
@patch("api.services.price_service.global_state_col")
@patch("api.services.price_service.price_history_col")
async def test_update_price(mock_history, mock_state):
    # Setup initial state (BTC = $1.0)
    mock_state.find_one = AsyncMock(return_value={"price_usd": 1.0})
    mock_state.update_one = AsyncMock()
    mock_history.find_one = AsyncMock(return_value=None) # No existing bucket
    mock_history.insert_one = AsyncMock()

    # 1. Test Buy Pressure (Token -> Native) -> Price UP
    # Volume = 100 BTC. Sensitivity 0.0001
    # Change = 100 * 0.0001 * 1.0 = 0.01
    # New Price = 1.01

    new_price = await update_btc_price("buy", 100.0)

    assert 1.009 < new_price < 1.011
    mock_state.update_one.assert_called()

    # 2. Test Sell Pressure (Native -> Token) -> Price DOWN
    # Reset mock state to return new price for next call simulation
    mock_state.find_one = AsyncMock(return_value={"price_usd": 1.01})

    # Sell 200 BTC. Change = 200 * 0.0001 * 1.01 = 0.0202
    # New Price = 1.01 - 0.0202 = 0.9898

    new_price_2 = await update_btc_price("sell", 200.0)

    assert 0.98 < new_price_2 < 0.99
