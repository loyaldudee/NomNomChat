from django.contrib import admin
from django.db.models import Count
# ✅ Added 'Notification' to the imports
from .models import Post, Comment, PostReport, CommentReport, AdminAuditLog, PostLike, Notification 

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'alias', 
        'community', 
        'post_type',
        'is_hidden', 
        'created_at', 
        'short_content', 
        'likes_count', 
        'reports_count'
    )
    
    list_filter = (
        'is_hidden', 
        'community', 
        'post_type'
    )
    
    search_fields = ('content', 'alias')
    list_editable = ('is_hidden',) 
    
    def short_content(self, obj):
        return obj.content[:50]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            total_likes=Count('likes', distinct=True),
            total_reports=Count('reports', distinct=True)
        )

    @admin.display(description='Likes', ordering='total_likes')
    def likes_count(self, obj):
        return obj.total_likes

    @admin.display(description='Reports', ordering='total_reports')
    def reports_count(self, obj):
        return obj.total_reports

# ... (Keep CommentAdmin, PostReportAdmin, etc. unchanged)
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('alias', 'post', 'is_hidden', 'created_at', 'reports_count')
    list_filter = ('is_hidden',)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(total_reports=Count('reports'))

    @admin.display(description='Reports', ordering='total_reports')
    def reports_count(self, obj):
        return obj.total_reports

@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'post', 'reason', 'created_at')

@admin.register(CommentReport)
class CommentReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'comment', 'reason', 'created_at')

@admin.register(AdminAuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action', 'target_type', 'reason', 'created_at')
    list_filter = ('action', 'target_type')

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)

# ✅ NEW: Notification Admin Section
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'actor', 'verb', 'is_read', 'created_at')
    list_filter = ('is_read', 'verb', 'created_at')  # Filter by Read Status & Type
    search_fields = ('recipient__username', 'actor__username')  # Search by users
    list_per_page = 50  # Notifications can be many, pagination helps