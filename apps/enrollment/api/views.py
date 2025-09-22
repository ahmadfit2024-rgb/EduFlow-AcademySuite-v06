# =================================================================
# apps/enrollment/api/views.py
# -----------------------------------------------------------------
# MIGRATION: Logic is heavily refactored for the relational schema.
# - `mark_lesson_complete`: Uses standard ORM to find the enrollment
#   and adds the completed lesson via the new ManyToMany relationship.
# - `submit_quiz`: Fetches relational Course, Lesson, and Answer
#   objects to accurately calculate the quiz score.
# - Uses GenericForeignKey lookups via ContentType to handle enrollments.
# =================================================================

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
import uuid
from datetime import datetime

from apps.enrollment.models import Enrollment
from apps.learning.models import Course, Lesson, Answer
from .serializers import EnrollmentSerializer

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='mark-lesson-complete')
    def mark_lesson_complete(self, request):
        user = request.user
        course_id = request.data.get('course_id')
        lesson_id = request.data.get('lesson_id')
        if not course_id or not lesson_id:
            return Response({'error': 'course_id and lesson_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        course_content_type = ContentType.objects.get_for_model(Course)
        enrollment = get_object_or_404(
            Enrollment,
            student=user,
            content_type=course_content_type,
            object_id=course_id
        )
        lesson_to_complete = get_object_or_404(Lesson, pk=lesson_id, course_id=course_id)

        enrollment.completed_lessons.add(lesson_to_complete)
        enrollment.last_accessed_lesson = lesson_to_complete
        enrollment.save()
        enrollment.update_progress() # This method was also updated in the model

        return Response({'status': 'success', 'progress': enrollment.progress}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='submit-quiz')
    def submit_quiz(self, request):
        user = request.user
        course_id = request.data.get('course_id')
        lesson_id = request.data.get('lesson_id')
        answers = {key.split('[')[1].split(']')[0]: value for key, value in request.data.items() if key.startswith('answers')}

        course_content_type = ContentType.objects.get_for_model(Course)
        enrollment = get_object_or_404(
            Enrollment,
            student=user,
            content_type=course_content_type,
            object_id=course_id
        )
        lesson = get_object_or_404(Lesson, pk=lesson_id, course_id=course_id)

        if lesson.content_type != 'quiz':
            return Response({'error': 'Lesson is not a quiz.'}, status=status.HTTP_400_BAD_REQUEST)

        questions = lesson.questions.all().prefetch_related('answers')
        total_questions = questions.count()
        correct_answers_count = 0

        # Grade the submission
        for i, question in enumerate(questions):
            question_key = f'question_{i+1}'
            submitted_answer_id = answers.get(question_key)
            
            # Find the correct answer ID for this question
            correct_answer = question.answers.filter(is_correct=True).first()

            if correct_answer and submitted_answer_id == str(correct_answer.pk):
                correct_answers_count += 1

        score = round((correct_answers_count / total_questions) * 100, 2) if total_questions > 0 else 100

        # Save the attempt with a unique ID
        attempt_id = str(uuid.uuid4())
        attempt_data = {
            'attempt_id': attempt_id,
            'lesson_id': lesson_id,
            'score': score,
            'submitted_at': datetime.utcnow().isoformat(),
            'answers': answers,
        }
        
        enrollment.quiz_attempts.append(attempt_data)
        enrollment.save(update_fields=['quiz_attempts'])

        result_url = reverse('learning:quiz_result', kwargs={'enrollment_pk': enrollment.pk, 'attempt_id': attempt_id})

        return Response({'status': 'success', 'result_url': result_url}, status=status.HTTP_200_OK)