from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.core.cache import cache
from .models import Community, CommunityMembership
from django.db.models import Count, Sum, F, IntegerField
from django.db.models.functions import Coalesce
from django.db.models import Count

class MyCommunitiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # 1. GENERATE A UNIQUE CACHE KEY
        is_admin = user.is_staff or user.is_superuser
        cache_key = f"communities_admin" if is_admin else f"communities_user_{user.id}"
        
        # 2. CHECK REDIS
        cached_data = cache.get(cache_key)
        if cached_data:
            print("⚡ Serving from Cache (Fast!)") 
            return Response(cached_data)

        # ---------------------------------------------------------
        # 👑 GOD MODE (Staff/Superuser sees ALL)
        # ---------------------------------------------------------
        if user.is_staff or user.is_superuser:
            print(f"👑 ADMIN DETECTED ({user.username}): Showing ALL communities")
            all_communities = Community.objects.all()
        else:
            # -----------------------------------------------------
            # NORMAL STUDENT LOGIC (Strict Mode)
            # -----------------------------------------------------
            
            # 1. GLOBAL ONLY: Only automatically show "All" (is_global=True)
            # We REMOVED the logic that guessed based on Branch/Year.
            auto_communities = Community.objects.filter(is_global=True)

            # 2. MANUAL: Get communities the user ACTUALLY joined (The strict A/B assignment)
            joined_ids = CommunityMembership.objects.filter(
                user=user
            ).values_list('community_id', flat=True)
            
            manual_communities = Community.objects.filter(id__in=joined_ids)

            # 3. COMBINE
            all_communities = (auto_communities | manual_communities).distinct()

        # 4. Serialize
        data = []
        for c in all_communities:
            data.append({
                "id": str(c.id),
                "name": c.name,
                "slug": c.slug,
                "is_global": c.is_global,
                "branch": c.branch, 
                "year": c.year,
                "division": c.division # ✅ Helpful for frontend
            })

        # 5. SAVE TO REDIS (15 mins)
        cache.set(cache_key, data, timeout=900)

        return Response(data)

class SearchCommunitiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_banned:
            return Response({"error": "User is banned"}, status=403)

        query = request.query_params.get("q", "").strip()
        if not query:
            return Response([])

        communities = Community.objects.filter(name__icontains=query)[:20]

        return Response([{
            "id": str(c.id),
            "name": c.name,
            "slug": c.slug,
            "is_global": c.is_global
        } for c in communities])
    

class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 🛡️ ALGORITHM: The "Anti-Spam" Engagement Score
        # We use 'post' (singular) because that is the relationship name Django found.
        # We assume comments are linked via 'comments' (standard related_name).
        
        communities = Community.objects.filter(is_global=False).annotate(
            # 1. Count Posts
            total_posts=Count('post', distinct=True),
            
            # 2. Count Post Likes (Requires user interaction)
            total_post_likes=Count('post__likes', distinct=True),
            
            # 3. Count Comments (High value interaction)
            total_comments=Count('post__comments', distinct=True),
            
            # 4. Count Comment Likes (Depth of conversation)
            # We use 'post__comments__likes' assuming the Comment model has a 'likes' relation
            total_comment_likes=Count('post__comments__likes', distinct=True)
        )

        data = []
        for c in communities:
            # 🧮 THE FORMULA
            score = (
                (c.total_posts * 5) +        # Base value (lowered to discourage spam)
                (c.total_post_likes * 2) +   # Likes prove quality
                (c.total_comments * 8) +     # Comments are GOLD (conversation)
                (c.total_comment_likes * 1)  # Good replies count too
            )
            
            data.append({
                "id": str(c.id),
                "name": c.name,
                "score": score,
                "stats": {
                    "posts": c.total_posts,
                    "likes": c.total_post_likes,
                    "comments": c.total_comments
                }
            })

        # Sort by Score (Highest First) in Python 
        # (It's safer than doing math in the SQL order_by clause for complex sums)
        data.sort(key=lambda x: x['score'], reverse=True)

        # Assign Ranks
        for index, item in enumerate(data):
            item['rank'] = index + 1

        return Response(data)

class CommunityScoreView(APIView):
    """ Get the score for just ONE community (using the same formula) """
    permission_classes = [IsAuthenticated]

    def get(self, request, community_id):
        try:
            # We execute the same annotation for a single community
            c = Community.objects.filter(id=community_id).annotate(
                total_posts=Count('post', distinct=True),
                total_post_likes=Count('post__likes', distinct=True),
                total_comments=Count('post__comments', distinct=True),
                total_comment_likes=Count('post__comments__likes', distinct=True)
            ).first()

            if not c:
                return Response({"score": 0})

            # 🧮 SAME FORMULA
            score = (
                (c.total_posts * 5) + 
                (c.total_post_likes * 2) + 
                (c.total_comments * 8) + 
                (c.total_comment_likes * 1)
            )

            return Response({"score": score})
        except Exception as e:
            # Fallback if a relation doesn't exist yet (e.g. no comments yet)
            print(f"Score Calc Error: {e}")
            return Response({"score": 0})