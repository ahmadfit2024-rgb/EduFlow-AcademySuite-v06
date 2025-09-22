import openpyxl
from django.http import HttpResponse
from io import BytesIO # Import BytesIO to handle in-memory files

class ExcelReportGenerator:
    """
    A service to generate Excel (XLSX) files.
    """
    def generate_course_enrollment_excel(self, course_title: str, enrollments_data: list) -> HttpResponse:
        """
        Generates an Excel report of all students enrolled in a course.

        Args:
            course_title: The title of the course.
            enrollments_data: A list of dictionaries, where each dict represents an enrolled student.

        Returns:
            An HttpResponse object with the XLSX file.
        """
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = f"Enrollments for {course_title[:20]}"

        # Define Headers
        headers = ["Student Name", "Email", "Enrollment Date", "Progress (%)", "Status"]
        sheet.append(headers)

        # Populate Data
        for enrollment in enrollments_data:
            row = [
                enrollment.get('student_name'),
                enrollment.get('student_email'),
                enrollment.get('enrollment_date'),
                enrollment.get('progress'),
                enrollment.get('status'),
            ]
            sheet.append(row)

        # --- NEW METHOD TO SAVE IN MEMORY ---
        # Create an in-memory binary stream
        buffer = BytesIO()
        # Save the workbook to the stream
        workbook.save(buffer)
        # Move the cursor to the beginning of the stream
        buffer.seek(0)

        # Create the HTTP response with the in-memory file
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="course_enrollments_{course_title}.xlsx"'
        
        return response