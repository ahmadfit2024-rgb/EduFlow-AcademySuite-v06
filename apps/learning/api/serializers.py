# =================================================================
# apps/learning/api/serializers.py
# -----------------------------------------------------------------
# MIGRATION: Serializers are updated for the relational models.
# - LearningPathSerializer now properly represents the ManyToMany
#   relationship to Courses for richer API responses.
# =================================================================
from rest_framework import serializers
from apps.learning.models import Course, LearningPath, Lesson

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'category', 'instructor']

class LearningPathSerializer(serializers.ModelSerializer):
    # Use the CourseSerializer to show nested course details
    courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = LearningPath
        fields = ['id', 'title', 'description', 'supervisor', 'courses']