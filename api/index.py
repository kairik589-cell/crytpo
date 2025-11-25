from fastapi import FastAPI, Body
from typing import Dict, Any

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on Vercel"}

@app.post("/")
def echo_payload(payload: Dict[Any, Any] = Body(...)):
    return {
        "message": "Payload received",
        "data": payload
    }
