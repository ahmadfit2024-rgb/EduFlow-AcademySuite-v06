# =================================================================
# apps/interactions/views.py
# -----------------------------------------------------------------
# MIGRATION: Adapted all views to use the new relational models.
# - Lookups for Course and Lesson now use standard primary keys.
# - When creating a DiscussionThread, the ForeignKey fields for
#   `course` and `lesson` are now assigned the actual model instances.
# =================================================================

from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render

from .models import DiscussionThread, DiscussionPost
from .forms import DiscussionThreadForm, DiscussionPostForm
from apps.learning.models import Course, Lesson

class AddDiscussionThreadView(LoginRequiredMixin, CreateView):
    model = DiscussionThread
    form_class = DiscussionThreadForm

    def form_valid(self, form):
        course = get_object_or_404(Course, pk=self.request.POST.get('course_id'))
        lesson = get_object_or_404(Lesson, pk=self.kwargs.get('lesson_id'))

        thread = form.save(commit=False)
        thread.student = self.request.user
        thread.course = course
        thread.lesson = lesson
        thread.save()

        threads = DiscussionThread.objects.filter(lesson=lesson).order_by('-created_at')
        context = {
            'threads': threads,
            'course': course,
            'current_lesson_id': lesson.pk
        }

        response = render(self.request, 'interactions/partials/_discussion_list.html', context)
        response['HX-Trigger-Detail'] = '{"message": "Your question has been posted successfully!"}'
        response['HX-Trigger'] = 'showToast'
        return response

class AddDiscussionPostView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = DiscussionPost
    form_class = DiscussionPostForm
    template_name = 'interactions/partials/_thread_detail.html'

    def test_func(self):
        return self.request.user.is_authenticated

    def form_valid(self, form):
        thread = get_object_or_404(DiscussionThread, pk=self.kwargs['thread_id'])

        post = form.save(commit=False)
        post.thread = thread
        post.user = self.request.user
        post.save()

        # Re-render the thread detail partial to include the new reply
        context = {'thread': thread, 'request': self.request} # Pass request for template tags
        response = render(self.request, self.template_name, context)
        response['HX-Trigger-Detail'] = '{"message": "Your reply has been posted."}'
        response['HX-Trigger'] = 'showToast'
        return response

class AIChatFormView(LoginRequiredMixin, TemplateView):
    template_name = 'interactions/partials/_ai_chat_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'course_pk': self.kwargs.get('course_pk'),
            'lesson_id': self.kwargs.get('lesson_id'),
        })
        return context