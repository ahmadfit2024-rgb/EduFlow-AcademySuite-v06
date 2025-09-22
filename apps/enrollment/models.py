# =================================================================
# apps/enrollment/models.py
# -----------------------------------------------------------------
# FINAL FIX: Added unique `related_name` arguments to the
# `completed_lessons` and `last_accessed_lesson` fields to resolve
# the reverse accessor clash identified by the system check.
# =================================================================

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    enrollable = GenericForeignKey('content_type', 'object_id')

    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress'
    )
    progress = models.FloatField(default=0.0)

    completed_lessons = models.ManyToManyField(
        'learning.Lesson',
        blank=True,
        related_name='completed_by_enrollments' # FIX
    )
    last_accessed_lesson = models.ForeignKey(
        'learning.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='last_accessed_by_enrollments' # FIX
    )

    quiz_attempts = models.JSONField(default=list, blank=True)

    class Meta:
        unique_together = ('student', 'content_type', 'object_id')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.enrollable}"

    def update_progress(self):
        if self.content_type.model == 'course':
            course = self.enrollable
            total_lessons = course.lessons.count()

            if total_lessons > 0:
                completed_count = self.completed_lessons.count()
                self.progress = round((completed_count / total_lessons) * 100, 2)
            else:
                self.progress = 100 if self.status == 'completed' else 0

            if self.progress >= 100:
                self.status = 'completed'
                self.progress = 100

            self.save(update_fields=['progress', 'status'])