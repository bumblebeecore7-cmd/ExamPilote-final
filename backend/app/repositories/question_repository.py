import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId
from pymongo.errors import PyMongoError
from app.core.database import DatabaseManager
from app.utils.serializers import serialize_doc

logger = logging.getLogger("exampilote.repositories.question")

class QuestionRepository:
    """Repository handling persistence and retrieval of question sets in MongoDB Atlas."""

    _fallback_cache: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _collection():
        return DatabaseManager.get_db().question_sets

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Saves a validated question set document to MongoDB Atlas."""
        data_to_insert = data.copy()
        if "created_at" not in data_to_insert:
            data_to_insert["created_at"] = datetime.now(timezone.utc)
        data_to_insert["schema_version"] = 1

        try:
            coll = cls._collection()
            result = coll.insert_one(data_to_insert)
            data_to_insert["_id"] = result.inserted_id
            data_to_insert["saved_to_atlas"] = True
            data_to_insert["storage_warning"] = None
            return serialize_doc(data_to_insert)
        except Exception as e:
            # Fallback to local session cache with explicit warning
            logger.warning(f"MongoDB Atlas save failed ({type(e).__name__}). Using session fallback.")
            new_id = ObjectId()
            data_to_insert["_id"] = new_id
            data_to_insert["saved_to_atlas"] = False
            data_to_insert["storage_warning"] = (
                f"Cloud save failed: {type(e).__name__} (Authentication/Network error). "
                f"Questions are available for this session. Update password in backend/.env to enable Atlas persistence."
            )
            serialized = serialize_doc(data_to_insert)
            cls._fallback_cache[str(new_id)] = serialized
            return serialized

    @classmethod
    def get_by_id(cls, question_set_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single question set by its ObjectId string."""
        if not ObjectId.is_valid(question_set_id):
            return None
        try:
            coll = cls._collection()
            doc = coll.find_one({"_id": ObjectId(question_set_id)})
            if doc:
                return serialize_doc(doc)
        except Exception as e:
            logger.warning(f"Could not read from MongoDB Atlas: {type(e).__name__}. Checking session cache.")

        # Check fallback cache
        return cls._fallback_cache.get(question_set_id)

    @classmethod
    def list_all(cls, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Retrieves paginated question sets ordered by most recent first."""
        try:
            coll = cls._collection()
            skip = (page - 1) * page_size
            total = coll.count_documents({})
            cursor = coll.find({}).sort("created_at", -1).skip(skip).limit(page_size)
            items = [serialize_doc(doc) for doc in cursor]
            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": items
            }
        except Exception as e:
            logger.warning(f"Could not list from MongoDB Atlas: {type(e).__name__}. Using session cache.")
            items = list(cls._fallback_cache.values())
            return {
                "total": len(items),
                "page": page,
                "page_size": page_size,
                "items": items
            }

    @classmethod
    def delete(cls, question_set_id: str) -> bool:
        """Deletes a question set by its ObjectId string."""
        if not ObjectId.is_valid(question_set_id):
            return False
        try:
            coll = cls._collection()
            res = coll.delete_one({"_id": ObjectId(question_set_id)})
            if res.deleted_count > 0:
                cls._fallback_cache.pop(question_set_id, None)
                return True
        except Exception:
            pass
        return cls._fallback_cache.pop(question_set_id, None) is not None
