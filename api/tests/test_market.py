import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from api.routers.market import match_orders
from api.core.database import orders_col, trades_col

@pytest.mark.asyncio
@patch("api.routers.market.orders_col")
@patch("api.routers.market.trades_col")
async def test_match_orders(mock_trades, mock_orders):
    # Setup Orders
    # Buy Order: Price 100, Amount 1
    buy_order = {"_id": "buy1", "pair": "T-B", "price": 100, "amount": 1, "order_type": "buy", "user_address": "u1", "status": "open"}
    # Sell Order: Price 90, Amount 1 (Should match because Sell Price <= Buy Price)
    sell_order = {"_id": "sell1", "pair": "T-B", "price": 90, "amount": 1, "order_type": "sell", "user_address": "u2", "status": "open"}

    # Mock cursors (AsyncMock)
    mock_cursor_buys = AsyncMock()
    mock_cursor_buys.to_list.return_value = [buy_order]

    mock_cursor_sells = AsyncMock()
    mock_cursor_sells.to_list.return_value = [sell_order]

    # Configure side effects for find calls
    def find_side_effect(query):
        mock_cursor = MagicMock()
        if query.get("order_type") == "buy":
             mock_cursor.sort.return_value = mock_cursor_buys
        else:
             mock_cursor.sort.return_value = mock_cursor_sells
        return mock_cursor

    mock_orders.find.side_effect = find_side_effect

    # CRITICAL: Configure trades_col.insert_one to be awaitable
    mock_trades.insert_one = AsyncMock()
    # Also need to mock update_one which is called later
    mock_orders.update_one = AsyncMock()

    await match_orders("T-B")

    # Check that a trade was recorded
    mock_trades.insert_one.assert_called()
    call_args = mock_trades.insert_one.call_args[0][0]
    assert call_args["price"] == 90
    assert call_args["buyer"] == "u1"
    assert call_args["seller"] == "u2"
