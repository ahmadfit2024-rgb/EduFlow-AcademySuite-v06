# =================================================================
# apps/enrollment/admin.py
# -----------------------------------------------------------------
# MIGRATION: Updated the admin list_display to correctly show
# the `enrollable` object via the GenericForeignKey.
# =================================================================

from django.contrib import admin
from .models import Enrollment

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'enrollable', 'status', 'progress', 'enrollment_date')
    list_filter = ('status', 'content_type')
    search_fields = ('student__username', 'object_id')
    autocomplete_fields = ('student',)