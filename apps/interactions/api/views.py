# =================================================================
# apps/interactions/api/views.py
# -----------------------------------------------------------------
# MIGRATION: The context-building logic for the AI assistant is
# updated to fetch Course and Lesson objects using the relational ORM.
# =================================================================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404

from .serializers import AIQuestionSerializer
from apps.interactions.services import AIAssistantService
from apps.learning.models import Course, Lesson

class AIAssistantApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AIQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        question = validated_data['question']
        course_id = validated_data['course_id']
        lesson_id = validated_data['lesson_id']

        try:
            course = get_object_or_404(Course, pk=course_id)
            lesson = get_object_or_404(Lesson, pk=lesson_id, course=course)

            context = {
                "course_title": course.title,
                "lesson_title": lesson.title,
                "lesson_content": lesson.content_data.get('description', 'No textual content available for this lesson.')
            }

            ai_service = AIAssistantService()
            answer = ai_service.get_answer(question=question, context=context)
            
            return Response({'answer': answer}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)