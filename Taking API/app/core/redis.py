import redis
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=2,
    )
    # Test connection
    redis_client.ping()
    logger.info("Redis connected successfully.")
except Exception as e:
    logger.warning(f"Redis unavailable, caching disabled: {e}")
    redis_client = None
