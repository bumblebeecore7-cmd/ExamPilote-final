from bson import ObjectId
from datetime import datetime, timezone
from typing import Any, Dict

def serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Converts MongoDB document fields (ObjectId, datetime) to JSON-serializable types."""
    if not doc:
        return {}
    res = {}
    for key, value in doc.items():
        if key == "_id":
            res["id"] = str(value)
        elif isinstance(value, ObjectId):
            res[key] = str(value)
        elif isinstance(value, datetime):
            if value.tzinfo is None:
                res[key] = value.replace(tzinfo=timezone.utc)
            else:
                res[key] = value
        elif isinstance(value, list):
            res[key] = [
                serialize_doc(item) if isinstance(item, dict)
                else str(item) if isinstance(item, ObjectId)
                else item
                for item in value
            ]
        elif isinstance(value, dict):
            res[key] = serialize_doc(value)
        else:
            res[key] = value
    return res
