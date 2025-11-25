from fastapi import FastAPI, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from bson import ObjectId

app = FastAPI()

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://Vercel-Admin-data:Bhkxu4nxHIvG2kPJ@data.ecs0ces.mongodb.net/?retryWrites=true&w=majority"
client = AsyncIOMotorClient(MONGODB_URI)
db = client.get_database("vercel_test_db")
collection = db.get_collection("entries")

# Helper to convert ObjectId to string
def pydantic_encoder(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj

@app.get("/")
async def read_root():
    try:
        entries = []
        cursor = collection.find().limit(10)
        async for document in cursor:
            # Convert ObjectId to string for JSON serialization
            document["_id"] = str(document["_id"])
            entries.append(document)
        return {"message": "Success", "data": entries}
    except Exception as e:
        return {"message": "Error fetching data", "error": str(e)}

@app.post("/")
async def create_entry(payload: Dict[Any, Any] = Body(...)):
    try:
        # Insert into MongoDB
        result = await collection.insert_one(payload)
        new_entry = await collection.find_one({"_id": result.inserted_id})

        # Convert ObjectId to string
        new_entry["_id"] = str(new_entry["_id"])

        return {
            "message": "Data saved successfully",
            "data": new_entry
        }
    except Exception as e:
        return {"message": "Error saving data", "error": str(e)}
