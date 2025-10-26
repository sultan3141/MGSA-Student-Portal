from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Q
from django.http import HttpResponse
import csv
from .models import User

@staff_member_required
def student_geographical_report(request):
    """Generate geographical report of students"""
    students = User.objects.filter(role='Student', is_active=True)
    
    # Statistics by zone
    zone_stats = students.values('zone').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Statistics by woreda
    woreda_stats = students.values('woreda', 'zone').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Statistics by kebele
    kebele_stats = students.values('kebele', 'woreda', 'zone').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'title': 'Student Geographical Distribution',
        'zone_stats': zone_stats,
        'woreda_stats': woreda_stats,
        'kebele_stats': kebele_stats,
        'total_students': students.count(),
    }
    
    return render(request, 'admin/student_geographical_report.html', context)

@staff_member_required
def export_students_csv(request):
    """Export all student data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mgsa_students.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Student ID', 'First Name', 'Middle Name', 'Last Name', 'Email',
        'Gender', 'Zone', 'Woreda', 'Kebele', 'College', 'Department',
        'Year of Study', 'Date Joined'
    ])
    
    students = User.objects.filter(role='Student', is_active=True).order_by('zone', 'woreda', 'kebele')
    
    for student in students:
        writer.writerow([
            student.student_id or '',
            student.first_name,
            student.middle_name or '',
            student.last_name,
            student.email,
            student.gender,
            student.zone,
            student.woreda,
            student.kebele or '',
            student.college,
            student.department,
            student.year_of_study,
            student.date_joined.strftime('%Y-%m-%d')
        ])
    
    return response

@staff_member_required
def student_demographics(request):
    """Show student demographics dashboard"""
    students = User.objects.filter(role='Student', is_active=True)
    
    # Gender distribution
    gender_stats = students.values('gender').annotate(count=Count('id'))
    
    # Year of study distribution
    year_stats = students.values('year_of_study').annotate(count=Count('id'))
    
    # Department distribution
    dept_stats = students.values('department').annotate(count=Count('id')).order_by('-count')[:10]
    
    # College distribution
    college_stats = students.values('college').annotate(count=Count('id'))
    
    context = {
        'title': 'Student Demographics',
        'gender_stats': gender_stats,
        'year_stats': year_stats,
        'dept_stats': dept_stats,
        'college_stats': college_stats,
        'total_students': students.count(),
    }
    
    return render(request, 'admin/student_demographics.html', context)