import redis
import os
from django.conf import settings

# ⚡ 6. Redis (Production settings)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client = redis.Redis.from_url(
    redis_url,
    decode_responses=True  # Important: Returns strings instead of bytes
)