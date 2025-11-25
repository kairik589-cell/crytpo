from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from FastAPI on Vercel"}

def test_echo_payload():
    payload = {"test": "data", "value": 123}
    response = client.post("/", json=payload)
    assert response.status_code == 200
    assert response.json() == {
        "message": "Payload received",
        "data": payload
    }
