# =================================================================
# apps/contracts/views.py
# -----------------------------------------------------------------
# MIGRATION: Queries are updated to be more explicit with the
# relational structure, ensuring data for the report is fetched
# efficiently from the new PostgreSQL schema.
# =================================================================

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.contrib.contenttypes.models import ContentType

from .models import Contract
from apps.enrollment.models import Enrollment
from apps.reports.services.excel_generator import ExcelReportGenerator
from apps.users.models import CustomUser
from apps.learning.models import Course, LearningPath

class ExportContractReportView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Handles the request to export a contract's employee progress report as an Excel file.
    """
    def test_func(self):
        contract = get_object_or_404(Contract, pk=self.kwargs['pk'])
        user = self.request.user
        return user.role == CustomUser.Roles.ADMIN or user == contract.client

    def get(self, request, *args, **kwargs):
        contract = get_object_or_404(Contract, pk=self.kwargs['pk'])

        # --- Data Gathering Logic (Live Relational Data) ---
        enrolled_students = contract.enrolled_students.all()
        student_ids = enrolled_students.values_list('id', flat=True)

        # Get all enrollments for these students
        all_enrollments = Enrollment.objects.filter(student_id__in=student_ids)

        report_data = []
        for student in enrolled_students:
            # Calculate average progress for this student
            avg_progress = all_enrollments.filter(student=student).aggregate(Avg('progress'))['progress__avg'] or 0

            report_data.append({
                'student_name': student.full_name or student.username,
                'student_email': student.email,
                'enrollment_date': student.date_joined.strftime("%Y-%m-%d"), # Approximation
                'progress': f"{avg_progress:.2f}",
                'status': 'Completed' if avg_progress >= 100 else 'In Progress',
            })

        report_title = f"Contract_{contract.title.replace(' ', '_')}"
        generator = ExcelReportGenerator()
        return generator.generate_course_enrollment_excel(report_title, report_data)