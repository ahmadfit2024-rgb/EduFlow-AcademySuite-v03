from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count
from apps.enrollment.models import Enrollment
from apps.learning.models import Course, LearningPath
from apps.users.models import CustomUser
from apps.contracts.models import Contract
from apps.interactions.models import DiscussionThread, DiscussionPost

class DashboardView(LoginRequiredMixin, View):
    """
    A smart view that renders the correct dashboard template
    based on the logged-in user's role and populates it with
    relevant data.
    """
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        user = request.user
        context = {'user': user}
        
        # ... (logic for admin, student, supervisor remains the same) ...

        if user.role == 'instructor':
            # Fetch courses taught by the instructor
            instructor_courses = Course.objects.filter(instructor=user)
            course_ids = [str(c._id) for c in instructor_courses]

            # Get total unique students across all instructor's courses
            total_students_count = Enrollment.objects.filter(enrollable_id__in=course_ids).values('student').distinct().count()

            # Get total unanswered questions for the instructor
            # Find threads where the instructor has not posted a reply
            instructor_posts = DiscussionPost.objects.filter(user=user).values_list('thread_id', flat=True)
            unanswered_threads_count = DiscussionThread.objects.filter(course_id__in=course_ids).exclude(pk__in=instructor_posts).count()
            
            # Get enrollment count for each course
            enrollments_per_course = Enrollment.objects.filter(enrollable_id__in=course_ids).values('enrollable_id').annotate(count=Count('student_id'))
            enrollment_map = {item['enrollable_id']: item['count'] for item in enrollments_per_course}

            # Attach enrollment count to each course object
            for course in instructor_courses:
                course.enrolled_count = enrollment_map.get(str(course._id), 0)

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

        # Mapping and rendering logic remains the same
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