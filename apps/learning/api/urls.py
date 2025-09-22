# =================================================================
# apps/learning/api/urls.py
# -----------------------------------------------------------------
# MIGRATION FIX: Corrected the file to remove the erroneous import
# of a non-API view. The router is now correctly configured for
# the Course and LearningPath API endpoints.
# =================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LearningPathViewSet

app_name = 'learning-api'

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'paths', LearningPathViewSet, basename='learningpath')

urlpatterns = [
    path('', include(router.urls)),
]