from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import pytest
from api.index import app

client = TestClient(app)

# Mocking the database interaction
@patch("api.index.collection")
def test_read_root(mock_collection):
    # Setup mock cursor
    mock_cursor = AsyncMock()
    mock_cursor.__aiter__.return_value = [
        {"_id": "507f1f77bcf86cd799439011", "test": "data"}
    ]
    mock_collection.find.return_value.limit.return_value = mock_cursor

    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Success"
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["test"] == "data"

@patch("api.index.collection")
def test_create_entry(mock_collection):
    # Setup mock insert result
    mock_result = MagicMock()
    mock_result.inserted_id = "507f1f77bcf86cd799439011"
    mock_collection.insert_one = AsyncMock(return_value=mock_result)

    # Setup mock find_one
    mock_collection.find_one = AsyncMock(return_value={
        "_id": "507f1f77bcf86cd799439011",
        "test": "new data"
    })

    payload = {"test": "new data"}
    response = client.post("/", json=payload)

    assert response.status_code == 200
    assert response.json()["message"] == "Data saved successfully"
    assert response.json()["data"]["test"] == "new data"
