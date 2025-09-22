# =================================================================
# apps/enrollment/api/serializers.py
# -----------------------------------------------------------------
# MIGRATION: Explicitly defined fields for clarity and to properly
# handle the new GenericForeignKey relationship.
# =================================================================
from rest_framework import serializers
from apps.enrollment.models import Enrollment

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = [
            'id',
            'student',
            'content_type',
            'object_id',
            'enrollable', # The read-only GenericForeignKey property
            'enrollment_date',
            'status',
            'progress'
        ]
        read_only_fields = ['enrollable']