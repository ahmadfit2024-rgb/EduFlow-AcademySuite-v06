# =================================================================
# apps/learning/admin.py
# -----------------------------------------------------------------
# FINAL FIX: Registered a standalone `LessonAdmin` with `search_fields`
# to satisfy the `autocomplete_fields` requirement from
# `DiscussionThreadAdmin`, resolving the admin.E039 system check error.
# =================================================================

from django.contrib import admin
from .models import Course, LearningPath, Lesson, Question, Answer, LearningPathModule

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    ordering = ('course', 'order')

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    ordering = ('order',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'instructor')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]

class LearningPathModuleInline(admin.TabularInline):
    model = LearningPathModule
    extra = 1
    ordering = ('order',)

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ('title', 'supervisor', 'created_at')
    list_filter = ('supervisor',)
    search_fields = ('title', 'description')
    inlines = [LearningPathModuleInline]

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'lesson')
    list_filter = ('lesson__course__title',)
    inlines = [AnswerInline]