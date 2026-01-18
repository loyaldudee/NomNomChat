from django.contrib import admin
from .models import Community, CommunityMembership

@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_global', 'year', 'branch')
    list_filter = ('is_global', 'year')
    search_fields = ('name', 'slug')

@admin.register(CommunityMembership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'community', 'joined_at')