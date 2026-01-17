from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


from .models import Community
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


class SearchCommunitiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 🛡️ Ban Safety Check
        if request.user.is_banned:
            return Response(
                {"error": "User is banned"},
                status=status.HTTP_403_FORBIDDEN
            )

        query = request.query_params.get("q", "").strip()

        if not query:
            return Response([], status=status.HTTP_200_OK)

        communities = Community.objects.filter(
            name__icontains=query
        )[:20]

        return Response([
            {
                "id": str(c.id),
                "name": c.name,
                "slug": c.slug,
                "is_global": c.is_global,
            }
            for c in communities
        ])