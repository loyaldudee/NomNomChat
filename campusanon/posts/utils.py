import random
from datetime import timedelta
from django.utils import timezone
from .models import RateLimit


def is_rate_limited(user, action, limit, window_seconds):
    window_start = timezone.now() - timedelta(seconds=window_seconds)

    count = RateLimit.objects.filter(
        user=user,
        action=action,
        created_at__gte=window_start
    ).count()

    if count >= limit:
        return True

    RateLimit.objects.create(user=user, action=action)
    return False

ADJECTIVES = [
    "Silent", "Curious", "Hidden", "Lost", "Brave", "Witty", "Calm"
]

NOUNS = [
    "Fox", "Crow", "Leaf", "Wolf", "Tiger", "Owl", "River"
]


def generate_alias():
    return f"{random.choice(ADJECTIVES)}{random.choice(NOUNS)}{random.randint(100,999)}"
