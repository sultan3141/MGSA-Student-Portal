# students/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Student(models.Model):
    YEAR_CHOICES = [
        ('Fresh', 'Fresh'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
        ('4th Year', '4th Year'),
        ('5th Year', '5th Year'),
        ('6th Year', '6th Year'),
        ('Graduate', 'Graduate'),
    ]
    
    SEMESTER_CHOICES = [
        ('1st', '1st Semester'),
        ('2nd', '2nd Semester'),
        ('3rd', '3rd Semester'),
        ('Summer', 'Summer'),
    ]
    
    # One-to-one relationship with custom User model
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'  # Changed to standard name
    )
    
    # Academic Information
    student_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    year_of_study = models.CharField(max_length=10, choices=YEAR_CHOICES, default='Fresh')
    current_semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, default='1st')
    gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    cgpa = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    
    # Academic Status
    is_active_student = models.BooleanField(default=True)
    academic_status = models.CharField(
        max_length=20,
        choices=[
            ('regular', 'Regular'),
            ('probation', 'Academic Probation'),
            ('warning', 'Academic Warning'),
            ('suspended', 'Suspended'),
            ('graduated', 'Graduated'),
        ],
        default='regular'
    )
    
    # Additional Contact Information
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    
    # Student Bio
    bio = models.TextField(blank=True, help_text="Short biography about the student")
    interests = models.JSONField(default=list, blank=True, help_text="Student interests/hobbies")
    skills = models.JSONField(default=list, blank=True, help_text="Student skills")
    
    # Academic Preferences
    preferred_study_methods = models.JSONField(
        default=list, 
        blank=True,
        help_text="Preferred study methods (group, individual, etc.)"
    )
    availability = models.JSONField(
        default=list,
        blank=True,
        help_text="Weekly availability for tutorials/study groups"
    )
    
    # Profile Completion
    profile_completion_percentage = models.PositiveIntegerField(default=0)
    last_profile_update = models.DateTimeField(auto_now=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_students'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['year_of_study']),
            models.Index(fields=['academic_status']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_id or 'No ID'}"
    
    def save(self, *args, **kwargs):
        # Auto-generate student ID if not provided
        if not self.student_id:
            self.student_id = self.generate_student_id()
        
        # Calculate profile completion percentage
        self.calculate_profile_completion()
        
        super().save(*args, **kwargs)
    
    def generate_student_id(self):
        """Generate a unique student ID"""
        import random
        import string
        
        # Format: MGSA + Year + Random numbers
        year = timezone.now().year % 100  # Last two digits of year
        random_part = ''.join(random.choices(string.digits, k=4))
        
        student_id = f"MGSA{year}{random_part}"
        
        # Ensure uniqueness
        while Student.objects.filter(student_id=student_id).exists():
            random_part = ''.join(random.choices(string.digits, k=4))
            student_id = f"MGSA{year}{random_part}"
        
        return student_id
    
    def calculate_profile_completion(self):
        """Calculate profile completion percentage"""
        total_fields = 0
        completed_fields = 0
        
        # User fields
        user_fields = ['first_name', 'last_name', 'email', 'gender']
        for field in user_fields:
            total_fields += 1
            if getattr(self.user, field):
                completed_fields += 1
        
        # Student fields
        student_fields = ['year_of_study', 'emergency_contact_name', 'emergency_contact_phone', 'bio']
        for field in student_fields:
            total_fields += 1
            if getattr(self, field):
                completed_fields += 1
        
        if total_fields > 0:
            self.profile_completion_percentage = int((completed_fields / total_fields) * 100)
        else:
            self.profile_completion_percentage = 0
    
    def get_academic_standing(self):
        """Get academic standing based on GPA"""
        if self.cgpa >= 3.5:
            return "Excellent"
        elif self.cgpa >= 3.0:
            return "Very Good"
        elif self.cgpa >= 2.5:
            return "Good"
        elif self.cgpa >= 2.0:
            return "Satisfactory"
        else:
            return "Needs Improvement"
    
    def get_active_tutorials(self):
        """Get active tutorial registrations"""
        try:
            from tutorials.models import TutorialRegistration
            return TutorialRegistration.objects.filter(
                student=self.user,
                status='registered',
                tutorial__is_active=True
            )
        except ImportError:
            return []
    
    def get_completed_tutorials(self):
        """Get completed tutorial registrations"""
        try:
            from tutorials.models import TutorialRegistration
            return TutorialRegistration.objects.filter(
                student=self.user,
                status='attended'
            )
        except ImportError:
            return []
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def email(self):
        return self.user.email
    
    @property
    def department(self):
        return self.user.department if hasattr(self.user, 'department') else None
    
    @property
    def college(self):
        return self.user.college if hasattr(self.user, 'college') else None

class StudentAcademicRecord(models.Model):
    """Track student academic records"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='academic_records'
    )
    
    course_code = models.CharField(max_length=20)
    course_name = models.CharField(max_length=200)
    credit_hours = models.PositiveIntegerField()
    grade = models.CharField(max_length=5)  # A, A-, B+, etc.
    grade_points = models.DecimalField(max_digits=3, decimal_places=2)
    semester = models.CharField(max_length=10)
    academic_year = models.CharField(max_length=10)
    
    is_transfer_credit = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-academic_year', 'semester', 'course_code']
        verbose_name = 'Academic Record'
        verbose_name_plural = 'Academic Records'
        unique_together = ['student', 'course_code', 'semester', 'academic_year']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.course_code}"

class StudentAttendance(models.Model):
    """Track student attendance for tutorials/events"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    
    event_type = models.CharField(
        max_length=20,
        choices=[
            ('tutorial', 'Tutorial'),
            ('workshop', 'Workshop'),
            ('seminar', 'Seminar'),
            ('meeting', 'Meeting'),
            ('event', 'Event'),
        ]
    )
    
    event_title = models.CharField(max_length=200)
    event_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    present = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-event_date']
        verbose_name = 'Student Attendance'
        verbose_name_plural = 'Student Attendance Records'
    
    def __str__(self):
        status = "Present" if self.present else "Absent"
        return f"{self.student.user.get_full_name()} - {self.event_title} - {status}"

class StudentAchievement(models.Model):
    """Track student achievements and awards"""
    ACHIEVEMENT_TYPES = [
        ('academic', 'Academic'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('leadership', 'Leadership'),
        ('community', 'Community Service'),
        ('research', 'Research'),
        ('other', 'Other'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_achieved = models.DateField()
    organization = models.CharField(max_length=200, blank=True)
    certificate_url = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_achieved']
        verbose_name = 'Student Achievement'
        verbose_name_plural = 'Student Achievements'
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.title}"


# Signal to automatically create Student profile when User with Student role is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_student_profile(sender, instance, created, **kwargs):
    """
    Automatically create Student profile when a user with Student role is created
    """
    if created and hasattr(instance, 'role') and instance.role == 'Student':
        Student.objects.get_or_create(user=instance)
        print(f"Created Student profile for {instance.email}")

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_student_profile(sender, instance, **kwargs):
    """
    Update Student profile when User is updated
    """
    if hasattr(instance, 'role') and instance.role == 'Student':
        # Ensure Student profile exists
        Student.objects.get_or_create(user=instance)