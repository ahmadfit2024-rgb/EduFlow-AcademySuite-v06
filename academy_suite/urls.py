# =================================================================
# academy_suite/urls.py
# -----------------------------------------------------------------
# FINAL FIX: Ensures all `include()` statements for APIs and apps
# use the correct namespacing for robust URL reversing.
# =================================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Routes (Version 1)
    path('api/v1/users/', include('apps.users.api.urls')),
    path('api/v1/learning/', include('apps.learning.api.urls', namespace='learning-api')),
    path('api/v1/enrollment/', include('apps.enrollment.api.urls', namespace='enrollment-api')),
    path('api/v1/interactions/', include('apps.interactions.api.urls', namespace='interactions_api')),
    path('api/v1/reports/', include('apps.reports.api.urls')), # No namespace needed for empty urls

    # Frontend Routes
    path('users/', include('apps.users.urls')),
    path('learning/', include('apps.learning.urls')),
    path('interactions/', include('apps.interactions.urls')),
    path('enrollment/', include('apps.enrollment.urls')),
    path('contracts/', include('apps.contracts.urls')),
    path('reports/', include('apps.reports.urls', namespace='reports')),

    # Core app will handle main routes
    path('', include('apps.core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)