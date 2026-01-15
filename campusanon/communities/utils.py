from .models import Community, CommunityMembership


def get_or_create_global_community():
    community, _ = Community.objects.get_or_create(
        slug="all",
        defaults={
            "name": "All",
            "is_global": True,
        },
    )
    return community


def get_or_create_academic_community(year, branch):
    slug = f"{year}-{branch.lower()}"

    community, _ = Community.objects.get_or_create(
        slug=slug,
        defaults={
            "name": f"{year} {branch}",
            "year": year,
            "branch": branch,
            "is_global": False,
        },
    )
    return community


def add_user_to_community(user, community):
    CommunityMembership.objects.get_or_create(
        user=user,
        community=community
    )
