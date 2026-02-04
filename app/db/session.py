from databases import Database
from app.config import settings
import logging

logger = logging.getLogger(__name__)

database = Database(settings.DATABASE_URL)

async def connect_to_db():
    try:
        logger.info("Connecting to database...")
        await database.connect()
        logger.info("Database connected.")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

async def close_db_connection():
    try:
        logger.info("Closing database connection...")
        await database.disconnect()
        logger.info("Database connection closed.")
    except Exception as e:
        logger.error(f"Failed to close database connection: {e}")
        raise
