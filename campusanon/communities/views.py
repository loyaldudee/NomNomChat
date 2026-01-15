from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CommunityMembership


class MyCommunitiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = CommunityMembership.objects.filter(user=request.user)

        data = []
        for m in memberships:
            c = m.community
            data.append({
                "id": str(c.id),
                "name": c.name,
                "slug": c.slug,
                "is_global": c.is_global,
            })

        return Response(data)
