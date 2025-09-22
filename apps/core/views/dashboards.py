# =================================================================
# apps/core/views/dashboards.py
# -----------------------------------------------------------------
# MIGRATION: All database queries have been rewritten to use the
# relational ORM.
# - Student dashboard now uses GenericForeignKey to get enrollments.
# - Instructor dashboard uses standard reverse relations to count students and questions.
# - Third-party and Supervisor dashboards now query the relational models correctly.
# - Optimized queries using select_related and prefetch_related where applicable.
# =================================================================

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

from apps.enrollment.models import Enrollment
from apps.learning.models import Course, LearningPath
from apps.users.models import CustomUser
from apps.contracts.models import Contract
from apps.interactions.models import DiscussionThread, DiscussionPost

class DashboardView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        user = request.user
        context = {'user': user}
        
        if user.role == 'admin':
            context.update({
                'total_users': CustomUser.objects.count(),
                'total_students': CustomUser.objects.filter(role=CustomUser.Roles.STUDENT).count(),
                'total_instructors': CustomUser.objects.filter(role=CustomUser.Roles.INSTRUCTOR).count(),
                'total_courses': Course.objects.count(),
            })

        elif user.role == 'student':
            course_content_type = ContentType.objects.get_for_model(Course)
            student_enrollments = Enrollment.objects.filter(
                student=user, content_type=course_content_type
            ).select_related('enrollable') # `enrollable` is the GenericForeignKey

            enrolled_courses_data = []
            for enrollment in student_enrollments:
                course = enrollment.enrollable
                if not course:
                    continue

                # Determine the URL to continue learning
                if enrollment.last_accessed_lesson:
                    continue_url = reverse('learning:lesson_detail', kwargs={
                        'course_slug': course.slug,
                        'lesson_order': enrollment.last_accessed_lesson.order
                    })
                else:
                    first_lesson = course.lessons.order_by('order').first()
                    if first_lesson:
                        continue_url = reverse('learning:lesson_detail', kwargs={
                            'course_slug': course.slug,
                            'lesson_order': first_lesson.order
                        })
                    else:
                        continue_url = '#' # Or a link to the course page

                enrolled_courses_data.append({
                    'course': course,
                    'progress': enrollment.progress,
                    'continue_url': continue_url
                })
            
            context['enrolled_courses_data'] = enrolled_courses_data

        elif user.role == 'instructor':
            instructor_courses = Course.objects.filter(instructor=user)
            course_ids = instructor_courses.values_list('pk', flat=True)
            
            course_content_type = ContentType.objects.get_for_model(Course)
            total_students_count = Enrollment.objects.filter(
                content_type=course_content_type, object_id__in=course_ids
            ).values('student').distinct().count()

            # Logic to find unanswered questions
            course_threads = DiscussionThread.objects.filter(course_id__in=course_ids)
            replied_thread_ids = DiscussionPost.objects.filter(thread__in=course_threads, user=user).values_list('thread_id', flat=True)
            unanswered_threads_count = course_threads.exclude(pk__in=replied_thread_ids).count()
            
            # Get student count for each course
            enrollments_per_course = Enrollment.objects.filter(
                content_type=course_content_type, object_id__in=course_ids
            ).values('object_id').annotate(count=Count('student_id'))
            
            enrollment_map = {item['object_id']: item['count'] for item in enrollments_per_course}

            for course in instructor_courses:
                course.enrolled_count = enrollment_map.get(course.pk, 0)

            context.update({
                'instructor_courses': instructor_courses,
                'total_students': total_students_count,
                'total_courses': instructor_courses.count(),
                'new_questions_count': unanswered_threads_count,
            })

        elif user.role == 'third_party':
            try:
                contract = Contract.objects.get(client=user, is_active=True)
                student_ids = contract.enrolled_students.values_list('id', flat=True)
                enrollments = Enrollment.objects.filter(student_id__in=student_ids)
                average_progress = enrollments.aggregate(Avg('progress'))['progress__avg'] or 0
                
                employee_data = []
                for student in contract.enrolled_students.all():
                    avg_student_progress = enrollments.filter(student=student).aggregate(Avg('progress'))['progress__avg'] or 0
                    employee_data.append({
                        'name': student.full_name or student.username,
                        'email': student.email,
                        'progress': avg_student_progress,
                    })
                context.update({
                    'contract': contract,
                    'total_employees': len(student_ids),
                    'average_progress': average_progress,
                    'employee_data': employee_data,
                })
            except Contract.DoesNotExist:
                context['contract'] = None
        
        elif user.role == 'supervisor':
            context['learning_paths'] = LearningPath.objects.filter(supervisor=user).prefetch_related('courses')

        dashboard_templates = {
            'admin': 'dashboards/admin.html',
            'supervisor': 'dashboards/supervisor.html',
            'instructor': 'dashboards/instructor.html',
            'student': 'dashboards/student.html',
            'third_party': 'dashboards/third_party.html',
        }
        template_name = dashboard_templates.get(user.role)
        if not template_name:
            return redirect('login')

        return render(request, template_name, context)