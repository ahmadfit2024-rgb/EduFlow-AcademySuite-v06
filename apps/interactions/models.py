# =================================================================
# apps/interactions/models.py
# -----------------------------------------------------------------
# MIGRATION: Replaced Djongo fields with standard Django fields.
# Converted `lesson_id` and `course_id` from CharField to proper
# ForeignKey relationships to ensure relational integrity with the
# newly structured learning models.
# =================================================================

from django.db import models
from django.conf import settings

class DiscussionThread(models.Model):
    """
    Represents a discussion thread related to a specific lesson.
    """
    lesson = models.ForeignKey('learning.Lesson', on_delete=models.CASCADE, related_name='discussion_threads')
    course = models.ForeignKey('learning.Course', on_delete=models.CASCADE, related_name='discussion_threads')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class DiscussionPost(models.Model):
    """
    Represents a single reply within a discussion thread.
    """
    thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reply_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.user.username} on {self.thread.title}"