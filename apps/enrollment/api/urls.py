# =================================================================
# apps/enrollment/api/urls.py
# -----------------------------------------------------------------
# MIGRATION FIX: Added app_name to allow for namespaced URL
# lookups from templates (e.g., 'enrollment-api:enrollment-mark-lesson-complete').
# =================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnrollmentViewSet

app_name = 'enrollment-api'

router = DefaultRouter()
router.register(r'', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
]