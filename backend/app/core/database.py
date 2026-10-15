import logging
import re
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError
from app.core.config import settings

logger = logging.getLogger("exampilote.database")

class DatabaseManager:
    """Manages the MongoDB Atlas client lifecycle and database access."""
    
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None

    @classmethod
    def get_masked_uri(cls, uri: Optional[str] = None) -> str:
        """Returns a sanitized URI with credentials masked to avoid exposing secrets."""
        target_uri = uri or settings.MONGODB_URI
        if not target_uri:
            return "[EMPTY URI]"
        # Mask password and auth user
        return re.sub(r"://([^:]+):([^@]+)@", r"://\1:***@", target_uri)

    @classmethod
    def get_client(cls) -> MongoClient:
        """Returns an active MongoClient instance or initializes one."""
        if cls._client is None:
            raw_uri = settings.MONGODB_URI.strip().strip('"').strip("'")
            logger.info("Initializing MongoClient connection...")
            cls._client = MongoClient(
                raw_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=10000,
                appname="ExamPilote"
            )
        return cls._client

    @classmethod
    def get_db(cls) -> Database:
        """Returns the configured MongoDB database handle."""
        if cls._db is None:
            client = cls.get_client()
            cls._db = client[settings.MONGODB_DATABASE]
        return cls._db

    @classmethod
    def ping(cls) -> dict:
        """Pings the MongoDB deployment and returns sanitized status information."""
        try:
            client = cls.get_client()
            # Send admin ping command to confirm server connectivity and authentication
            result = client.admin.command("ping")
            server_info = client.server_info()
            return {
                "connected": True,
                "database": settings.MONGODB_DATABASE,
                "ping_ok": result.get("ok", 0) == 1.0,
                "server_version": server_info.get("version", "unknown"),
                "message": "Successfully connected to MongoDB Atlas."
            }
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            logger.error("MongoDB Atlas connection failed: timeout or network error.")
            return {
                "connected": False,
                "database": settings.MONGODB_DATABASE,
                "ping_ok": False,
                "message": "Connection to MongoDB Atlas timed out. Please check cluster IP access list (Network Access)."
            }
        except OperationFailure as e:
            logger.error("MongoDB Atlas operation failed: authentication or permission error.")
            return {
                "connected": False,
                "database": settings.MONGODB_DATABASE,
                "ping_ok": False,
                "message": "Authentication failed. Please verify your Atlas database username and password."
            }
        except Exception as e:
            logger.error(f"Unexpected MongoDB error occurred: {type(e).__name__}")
            return {
                "connected": False,
                "database": settings.MONGODB_DATABASE,
                "ping_ok": False,
                "message": f"Database connection error: {type(e).__name__}"
            }

    @classmethod
    def init_indexes(cls) -> None:
        """Creates necessary indexes on required collections."""
        try:
            db = cls.get_db()
            # question_sets collection indexes
            db.question_sets.create_index("created_at")
            db.question_sets.create_index("topic")

            # quiz_attempts collection indexes
            db.quiz_attempts.create_index("question_set_id")
            db.quiz_attempts.create_index("submitted_at")
            logger.info("MongoDB indexes successfully verified.")
        except Exception as e:
            logger.warning(f"Could not verify/create indexes: {type(e).__name__}")

    @classmethod
    def close(cls) -> None:
        """Closes the MongoClient connection on shutdown."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("MongoDB client connection closed.")

def get_database() -> Database:
    """FastAPI dependency for accessing the database."""
    return DatabaseManager.get_db()
