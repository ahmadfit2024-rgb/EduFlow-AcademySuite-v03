from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Avg
from django.conf import settings
from .models import Contract
from apps.enrollment.models import Enrollment
from apps.reports.services.excel_generator import ExcelReportGenerator

class ExportContractReportView(LoginRequiredMixin, View):
    """
    Handles the request to export a contract's employee progress report as an Excel file.
    """
    def get(self, request, *args, **kwargs):
        contract = get_object_or_404(Contract, pk=self.kwargs['pk'])
        
        # Security check: Ensure only the client of the contract or an admin can download
        if not (request.user.is_staff or request.user == contract.client):
            return redirect('dashboard')

        # --- Data Gathering Logic ---
        student_ids = contract.enrolled_students.values_list('id', flat=True)
        enrollments = Enrollment.objects.filter(student_id__in=student_ids)
        
        report_data = []
        for student in contract.enrolled_students.all():
            avg_progress = enrollments.filter(student=student).aggregate(Avg('progress'))['progress__avg'] or 0
            report_data.append({
                'student_name': student.full_name or student.username,
                'student_email': student.email,
                'enrollment_date': student.date_joined.strftime("%Y-%m-%d"), # Approximation of enrollment date
                'progress': avg_progress,
                'status': 'In Progress' if avg_progress < 100 else 'Completed',
            })
        
        # --- Generate and Return Excel File ---
        report_title = f"Contract_{contract.title.replace(' ', '_')}"
        generator = ExcelReportGenerator()
        return generator.generate_course_enrollment_excel(report_title, report_data)