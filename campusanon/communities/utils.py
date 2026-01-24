from .models import Community, CommunityMembership

def get_or_create_global_community():
    """
    Safely retrieves the Global 'All' community.
    Since there is only one global community, using get_or_create here is safe.
    """
    community, _ = Community.objects.get_or_create(
        slug="all",
        defaults={
            "name": "All",
            "is_global": True,
        },
    )
    return community

# ❌ DELETED: get_or_create_academic_community
# We removed this function because it creates "Ghost Communities" (ignoring divisions).
# The logic for finding the correct class (e.g. "1st Year COMP A") 
# is now strictly handled inside accounts/views.py.

def add_user_to_community(user, community):
    """
    Simple helper to add a user to a community if not already a member.
    """
    CommunityMembership.objects.get_or_create(
        user=user,
        community=community
    )