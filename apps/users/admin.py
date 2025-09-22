# =================================================================
# apps/users/admin.py
# -----------------------------------------------------------------
# MIGRATION: This ensures the CustomUser model is properly managed
# in the admin panel, displaying all relevant fields from the
# new PostgreSQL-compatible model.
# =================================================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Customize the Django admin interface for the CustomUser model.
    """
    model = CustomUser
    list_display = ('username', 'email', 'full_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'groups')
    search_fields = ('username', 'full_name', 'email')
    ordering = ('-date_joined',)
    
    # Add custom fields to the admin form
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Profile', {'fields': ('role', 'full_name', 'avatar_url')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role & Profile', {'fields': ('role', 'full_name', 'avatar_url')}),
    )