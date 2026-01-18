from django.contrib import admin
from .models import User, EmailOTP

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'internal_username', 'year', 'branch', 'is_banned', 'created_at')
    search_fields = ('internal_username', 'email_hash')
    list_filter = ('is_banned', 'year', 'branch')
    ordering = ('-created_at',)

@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'attempts', 'expires_at')
    search_fields = ('email',)