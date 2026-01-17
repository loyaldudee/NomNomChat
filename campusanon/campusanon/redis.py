import redis
from django.conf import settings

# Connect to the local Redis instance
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True  # Important: Returns strings instead of bytes
)