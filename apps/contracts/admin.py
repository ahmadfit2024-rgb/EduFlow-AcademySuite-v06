# =================================================================
# apps/contracts/admin.py
# -----------------------------------------------------------------
# MIGRATION: This admin interface is updated to use Django's
# standard features for relational models, such as `filter_horizontal`
# for a better ManyToMany user experience.
# =================================================================

from django.contrib import admin
from .models import Contract
from apps.users.models import CustomUser

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'client')
    search_fields = ('title', 'client__username', 'client__full_name')
    autocomplete_fields = ('client',)

    # Use filter_horizontal for a better experience with ManyToManyFields
    filter_horizontal = ('enrolled_students', 'learning_paths')

    fieldsets = (
        (None, {
            'fields': ('title', 'client', 'is_active')
        }),
        ('Contract Period', {
            'fields': ('start_date', 'end_date')
        }),
        ('Entitlements', {
            'fields': ('learning_paths', 'enrolled_students')
        }),
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Filter the 'enrolled_students' selector to only show users with the 'student' role
        if db_field.name == "enrolled_students":
            kwargs["queryset"] = CustomUser.objects.filter(role='student')
        return super().formfield_for_manytomany(db_field, request, **kwargs)