import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId
from app.core.database import DatabaseManager
from app.utils.serializers import serialize_doc

logger = logging.getLogger("exampilote.repositories.quiz_attempt")

class QuizAttemptRepository:
    """Repository handling persistence and retrieval of quiz attempts in MongoDB Atlas."""

    _fallback_cache: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _collection():
        return DatabaseManager.get_db().quiz_attempts

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Saves a quiz attempt document to MongoDB Atlas."""
        data_to_insert = data.copy()
        if "submitted_at" not in data_to_insert:
            data_to_insert["submitted_at"] = datetime.now(timezone.utc)
        
        try:
            coll = cls._collection()
            result = coll.insert_one(data_to_insert)
            data_to_insert["_id"] = result.inserted_id
            data_to_insert["saved_to_atlas"] = True
            return serialize_doc(data_to_insert)
        except Exception as e:
            logger.warning(f"MongoDB Atlas save attempt failed ({type(e).__name__}). Using session fallback.")
            new_id = ObjectId()
            data_to_insert["_id"] = new_id
            data_to_insert["saved_to_atlas"] = False
            serialized = serialize_doc(data_to_insert)
            cls._fallback_cache[str(new_id)] = serialized
            return serialized

    @classmethod
    def get_by_id(cls, attempt_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single quiz attempt by its ObjectId string."""
        if not ObjectId.is_valid(attempt_id):
            return None
        try:
            coll = cls._collection()
            doc = coll.find_one({"_id": ObjectId(attempt_id)})
            if doc:
                return serialize_doc(doc)
        except Exception as e:
            logger.warning(f"Could not read attempt from Atlas: {type(e).__name__}")

        return cls._fallback_cache.get(attempt_id)

    @classmethod
    def list_all(cls, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Retrieves paginated quiz attempts ordered by most recent first."""
        try:
            coll = cls._collection()
            skip = (page - 1) * page_size
            total = coll.count_documents({})
            cursor = coll.find({}).sort("submitted_at", -1).skip(skip).limit(page_size)
            items = [serialize_doc(doc) for doc in cursor]
            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": items
            }
        except Exception as e:
            logger.warning(f"Could not list attempts from Atlas: {type(e).__name__}")
            items = list(cls._fallback_cache.values())
            return {
                "total": len(items),
                "page": page,
                "page_size": page_size,
                "items": items
            }

    @classmethod
    def get_by_question_set_id(cls, question_set_id: str) -> List[Dict[str, Any]]:
        """Retrieves all attempts for a specific question set."""
        try:
            coll = cls._collection()
            cursor = coll.find({"question_set_id": question_set_id}).sort("submitted_at", -1)
            return [serialize_doc(doc) for doc in cursor]
        except Exception:
            return [item for item in cls._fallback_cache.values() if item.get("question_set_id") == question_set_id]
