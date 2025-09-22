# =================================================================
# apps/learning/api/views.py
# -----------------------------------------------------------------
# MIGRATION: Logic is heavily adapted for the relational schema.
# - `update_lesson_order`: Now updates the `order` field on individual
#   Lesson model instances within a transaction for data integrity.
# - `update_structure`: Rebuilds the relationship through the
#   `LearningPathModule` model, clearing old entries and creating new
#   ones with the correct order.
# =================================================================

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from apps.learning.models import Course, LearningPath, Lesson, LearningPathModule
from .serializers import CourseSerializer, LearningPathSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAdminUser] # Example permission

    @action(detail=True, methods=['post'], url_path='update-lesson-order')
    @transaction.atomic
    def update_lesson_order(self, request, pk=None):
        course = self.get_object()
        lesson_ids_order = request.data.get('lesson_order', [])

        if not isinstance(lesson_ids_order, list):
            return Response({'error': 'lesson_order must be a list'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the order for each lesson
        for index, lesson_id in enumerate(lesson_ids_order):
            try:
                Lesson.objects.filter(pk=lesson_id, course=course).update(order=index + 1)
            except (Lesson.DoesNotExist, ValueError):
                # Handle cases where lesson_id is invalid or doesn't belong to the course
                continue

        return Response({'status': 'Lesson order updated successfully'}, status=status.HTTP_200_OK)

class LearningPathViewSet(viewsets.ModelViewSet):
    queryset = LearningPath.objects.all()
    serializer_class = LearningPathSerializer
    permission_classes = [permissions.IsAdminUser] # Example permission

    @action(detail=True, methods=['post'], url_path='update-structure')
    @transaction.atomic
    def update_structure(self, request, pk=None):
        learning_path = self.get_object()
        course_ids = request.data.get('course_ids', [])

        if not isinstance(course_ids, list):
            return Response({'error': 'course_ids must be a list'}, status=status.HTTP_400_BAD_REQUEST)

        # Clear existing course structure for this path
        learning_path.modules.all().delete()

        # Create new module entries with the correct order
        for index, course_id in enumerate(course_ids):
            try:
                course = Course.objects.get(pk=course_id)
                LearningPathModule.objects.create(
                    learning_path=learning_path,
                    course=course,
                    order=index + 1
                )
            except (Course.DoesNotExist, ValueError):
                continue

        return Response({'status': 'Learning path structure updated successfully'}, status=status.HTTP_200_OK)