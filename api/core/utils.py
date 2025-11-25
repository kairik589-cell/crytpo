from bson import ObjectId
from typing import Any

def serialize_mongo(obj: Any) -> Any:
    """
    Recursively convert ObjectId to string in dicts and lists.
    """
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        return {k: serialize_mongo(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_mongo(v) for v in obj]
    return obj
