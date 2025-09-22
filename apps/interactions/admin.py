# =================================================================
# apps/interactions/admin.py
# -----------------------------------------------------------------
# MIGRATION: Updated the admin interface to correctly display and
# manage the new relational DiscussionThread and DiscussionPost models.
# Added autocomplete_fields for better performance with foreign keys.
# =================================================================

from django.contrib import admin
from .models import DiscussionThread, DiscussionPost

@admin.register(DiscussionThread)
class DiscussionThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'course', 'lesson', 'created_at')
    search_fields = ('title', 'question')
    list_filter = ('course',)
    autocomplete_fields = ('student', 'course', 'lesson')

class DiscussionPostInline(admin.TabularInline):
    model = DiscussionPost
    extra = 0
    readonly_fields = ('user', 'reply_text', 'created_at')

@admin.register(DiscussionPost)
class DiscussionPostAdmin(admin.ModelAdmin):
    list_display = ('thread', 'user', 'created_at')
    search_fields = ('reply_text',)
    autocomplete_fields = ('thread', 'user')