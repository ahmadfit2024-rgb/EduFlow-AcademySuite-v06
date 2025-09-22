# =================================================================
# apps/reports/urls.py
# -----------------------------------------------------------------
# FINAL FIX: Added `app_name` to support namespacing in the
# main project urls.py, resolving an ImproperlyConfigured error.
# =================================================================

from django.urls import path
from .views import ReportDashboardView

app_name = 'reports'

urlpatterns = [
    path('', ReportDashboardView.as_view(), name='report_dashboard'),
]