from django.db import models
from django.conf import settings

class Tutorial(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tutor = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    topics = models.JSONField(default=list, blank=True)
    
    # Schedule
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.JSONField(default=list)  # ['Monday', 'Wednesday', 'Friday']
    time = models.CharField(max_length=50)  # '14:00-16:00'
    
    max_students = models.PositiveIntegerField()
    current_registrations = models.PositiveIntegerField(default=0)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tutorials')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def is_full(self):
        return self.current_registrations >= self.max_students

class TutorialRegistration(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('attended', 'Attended'),
        ('cancelled', 'Cancelled'),
    ]
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tutorial_registrations')
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE, related_name='registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='registered')
    
    class Meta:
        unique_together = ['student', 'tutorial']
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.student.email} - {self.tutorial.title}"