# =================================================================
# apps/reports/views.py
# -----------------------------------------------------------------
# MIGRATION: All data-fetching logic for report generation has
# been updated to use the relational ORM, including queries that
# utilize the GenericForeignKey on the Enrollment model.
# =================================================================

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType

from .services.pdf_generator import PDFReportGenerator
from .services.excel_generator import ExcelReportGenerator
from apps.users.models import CustomUser
from apps.learning.models import Course
from apps.enrollment.models import Enrollment

class ReportDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "reports/report_dashboard.html"

    def test_func(self):
        return self.request.user.role in [CustomUser.Roles.ADMIN, CustomUser.Roles.SUPERVISOR]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Reporting Dashboard"
        context["students"] = CustomUser.objects.filter(role=CustomUser.Roles.STUDENT)
        context["courses"] = Course.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        report_type = request.POST.get("report_type")
        course_id = request.POST.get("course_id") # This name is used by both forms now

        if not course_id:
            messages.error(request, "Please select a course.")
            return redirect('reports:report_dashboard')
        
        course = get_object_or_404(Course, pk=course_id)
        course_content_type = ContentType.objects.get_for_model(Course)

        if report_type == "student_pdf":
            student_id = request.POST.get("student_id")
            if not student_id:
                messages.error(request, "Please select a student for the PDF report.")
                return redirect('reports:report_dashboard')

            student = get_object_or_404(CustomUser, id=student_id)
            enrollment = Enrollment.objects.filter(
                student=student, content_type=course_content_type, object_id=course.pk
            ).first()

            if not enrollment:
                messages.warning(request, f"{student} is not enrolled in '{course.title}'.")
                return redirect('reports:report_dashboard')

            student_data = {
                "student_name": student.full_name or student.username,
                "course_title": course.title,
                "enrollment_date": enrollment.enrollment_date.strftime("%Y-%m-%d"),
                "progress": enrollment.progress,
                "status": enrollment.get_status_display(),
            }
            generator = PDFReportGenerator()
            return generator.generate_student_performance_pdf(student_data)

        elif report_type == "course_excel":
            enrollments = Enrollment.objects.filter(
                content_type=course_content_type, object_id=course.pk
            ).select_related('student')

            enrollments_data = [
                {
                    'student_name': enr.student.full_name or enr.student.username,
                    'student_email': enr.student.email,
                    'enrollment_date': enr.enrollment_date.strftime("%Y-%m-%d"),
                    'progress': enr.progress,
                    'status': enr.get_status_display(),
                }
                for enr in enrollments
            ]
            generator = ExcelReportGenerator()
            return generator.generate_course_enrollment_excel(course.title, enrollments_data)

        messages.error(request, "Invalid report type selected.")
        return redirect('reports:report_dashboard')