from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Student

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_student_profile(sender, instance, created, **kwargs):
    """Automatically create student profile when user is created with student role"""
    if created and instance.role == 'Student':
        Student.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_student_profile(sender, instance, **kwargs):
    """Save student profile when user is saved"""
    if hasattr(instance, 'student'):
        instance.student.save()