# =================================================================
# apps/learning/views.py
# -----------------------------------------------------------------
# MIGRATION: All views have been refactored to work with the new
# relational models (PostgreSQL).
# - Object lookups now use standard Django ORM methods (e.g., get_object_or_404).
# - Accessing related objects (lessons, questions) is done via relational managers (e.g., course.lessons.all()).
# - Quiz building logic now creates separate Question and Answer objects.
# - The logic for creating and ordering lessons is updated for the new relational structure.
# =================================================================

from django.views.generic import DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from .models import Course, LearningPath, Lesson, Question, Answer, LearningPathModule
from .forms import LearningPathForm, LessonForm
from apps.enrollment.models import Enrollment
from apps.users.models import CustomUser

class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'learning/lesson_detail.html'
    slug_url_kwarg = 'course_slug'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        lesson_order = self.kwargs.get('lesson_order')

        try:
            current_lesson = course.lessons.get(order=lesson_order)
        except Lesson.DoesNotExist:
            # Redirect to the first lesson if the requested order doesn't exist
            first_lesson = course.lessons.order_by('order').first()
            if first_lesson:
                return redirect('learning:lesson_detail', course_slug=course.slug, lesson_order=first_lesson.order)
            return redirect('dashboard') # Or to a "course has no lessons" page

        sorted_lessons = course.lessons.order_by('order')
        prev_lesson = sorted_lessons.filter(order__lt=current_lesson.order).last()
        next_lesson = sorted_lessons.filter(order__gt=current_lesson.order).first()

        # Get or create enrollment and update progress
        course_content_type = ContentType.objects.get_for_model(Course)
        enrollment, _ = Enrollment.objects.get_or_create(
            student=self.request.user,
            content_type=course_content_type,
            object_id=course.pk
        )
        enrollment.last_accessed_lesson = current_lesson
        enrollment.save()

        context.update({
            'sorted_lessons': sorted_lessons,
            'current_lesson': current_lesson,
            'prev_lesson_order': prev_lesson.order if prev_lesson else None,
            'next_lesson_order': next_lesson.order if next_lesson else None,
            'progress': enrollment.progress,
        })
        return context

class LearningPathCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = LearningPath
    form_class = LearningPathForm
    template_name = 'learning/path_form.html'

    def test_func(self):
        return self.request.user.role in ['admin', 'supervisor']

    def get_success_url(self):
        return reverse('learning:path_builder', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Create New Learning Path"
        return context

class PathBuilderView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = LearningPath
    template_name = 'learning/path_builder.html'
    context_object_name = 'learning_path'

    def test_func(self):
        return self.request.user.role in ['admin', 'supervisor']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_path = self.get_object()
        path_course_ids = learning_path.courses.values_list('id', flat=True)
        context['available_courses'] = Course.objects.exclude(id__in=path_course_ids)
        return context

class CourseManageView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Course
    template_name = 'learning/manage_course.html'
    context_object_name = 'course'

    def test_func(self):
        course = self.get_object()
        return self.request.user.role == 'admin' or course.instructor == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lesson_form'] = LessonForm()
        return context

class LessonCreateView(LoginRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm

    def form_valid(self, form):
        course = get_object_or_404(Course, pk=self.kwargs['pk'])
        lesson = form.save(commit=False)
        lesson.course = course

        # Determine the next order
        last_lesson = course.lessons.order_by('-order').first()
        lesson.order = (last_lesson.order + 1) if last_lesson else 1

        video_url = form.cleaned_data.get('video_url')
        if lesson.content_type == 'video' and video_url:
            lesson.content_data = {'video_url': video_url}

        lesson.save()
        return render(self.request, 'partials/_lesson_list.html', {'course': course})

class QuizBuilderView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Course
    template_name = 'learning/quiz_builder.html'
    pk_url_kwarg = 'course_pk'
    context_object_name = 'course'

    def test_func(self):
        course = self.get_object()
        return self.request.user.role == 'admin' or course.instructor == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_id'], course=self.get_object())
        context['lesson'] = lesson
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        course = self.get_object()
        lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_id'], course=course)

        # Clear existing questions and answers for this lesson to rebuild them
        lesson.questions.all().delete()

        post_data = request.POST
        i = 1
        while f'question-text-{i}' in post_data:
            question_text = post_data[f'question-text-{i}']
            if not question_text:
                i += 1
                continue

            question = Question.objects.create(lesson=lesson, question_text=question_text)
            correct_answer_identifier = post_data.get(f'is-correct-{i}')

            j = 1
            while f'answer-text-{i}-{j}' in post_data:
                answer_text = post_data[f'answer-text-{i}-{j}']
                if answer_text:
                    is_correct = correct_answer_identifier == f'{i}-{j}'
                    Answer.objects.create(question=question, answer_text=answer_text, is_correct=is_correct)
                j += 1
            i += 1

        messages.success(request, f"Quiz for '{lesson.title}' has been saved successfully.")
        return redirect('learning:course_manage', pk=course.pk)

class TakeQuizView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'learning/take_quiz.html'
    pk_url_kwarg = 'course_pk'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_id'], course=self.get_object())
        if lesson.content_type != 'quiz':
            messages.error(self.request, "This lesson is not a quiz.")
            return redirect('dashboard')
        context['lesson'] = lesson
        return context

class QuizResultView(LoginRequiredMixin, DetailView):
    model = Enrollment
    template_name = 'learning/quiz_result.html'
    pk_url_kwarg = 'enrollment_pk'
    context_object_name = 'enrollment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempt_id = self.kwargs['attempt_id']
        attempt = next((att for att in self.object.quiz_attempts if att['attempt_id'] == attempt_id), None)
        if not attempt:
            messages.error(self.request, "Quiz attempt not found.")
            return redirect('dashboard')
        
        lesson = get_object_or_404(Lesson, pk=attempt['lesson_id'])
        course = lesson.course
        
        context['attempt'] = attempt
        context['lesson'] = lesson
        context['course'] = course
        return context