# =================================================================
# apps/learning/models.py
# -----------------------------------------------------------------
# MIGRATION: This is the most significant change. The original
# embedded models (Lesson, Question, Answer, Module) from MongoDB
# have been converted into separate, concrete relational models.
# - ForeignKey relationships now link everything:
#   - Lesson -> Course
#   - Question -> Lesson
#   - Answer -> Question
#   - LearningPathModule -> LearningPath and Course
# - Removed all Djongo-specific fields and abstract classes.
# - Added related_name attributes for easier reverse lookups.
# =================================================================

from django.db import models
from django.conf import settings

# --- Main Learning Models (Now Relational) ---

class Course(models.Model):
    """ Represents a single, self-contained course. """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses_taught'
    )
    category = models.CharField(max_length=100)
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    cover_image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    """ Represents a single lesson within a course. Now a separate table. """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    CONTENT_CHOICES = [
        ('video', 'Video'),
        ('pdf', 'PDF'),
        ('quiz', 'Quiz'),
        ('text_editor', 'Text Editor')
    ]
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_CHOICES
    )
    # This will store video URLs, text content, etc. Quiz content is now linked via relations.
    content_data = models.JSONField(default=dict, blank=True)
    is_previewable = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - Lesson {self.order}: {self.title}"

class Question(models.Model):
    """ Represents a single quiz question for a lesson. Now a separate table. """
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()

    def __str__(self):
        return self.question_text[:80]

class Answer(models.Model):
    """ Represents a single answer choice for a question. Now a separate table. """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer_text

class LearningPath(models.Model):
    """ Represents a high-level learning path or diploma. """
    title = models.CharField(max_length=255)
    description = models.TextField()
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='paths_supervised'
    )
    # The relationship to courses is now managed by a through model
    courses = models.ManyToManyField(
        Course,
        through='LearningPathModule',
        related_name='learning_paths'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class LearningPathModule(models.Model):
    """
    This is a "through" model that connects LearningPath and Course,
    and stores the order of the course within the path.
    """
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('learning_path', 'course')

    def __str__(self):
        return f"{self.learning_path.title}: {self.course.title} (Order: {self.order})"