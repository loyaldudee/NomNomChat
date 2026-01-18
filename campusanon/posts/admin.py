from django.contrib import admin
from .models import Post, Comment, PostReport, CommentReport, AdminAuditLog

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('alias', 'community', 'is_hidden', 'created_at', 'short_content')
    list_filter = ('is_hidden', 'community')
    search_fields = ('content', 'alias')
    
    def short_content(self, obj):
        return obj.content[:50]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('alias', 'post', 'is_hidden', 'created_at')
    list_filter = ('is_hidden',)

@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'post', 'reason', 'created_at')

@admin.register(AdminAuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action', 'target_type', 'reason', 'created_at')
    list_filter = ('action', 'target_type')