from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Executive

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_executive_profile(sender, instance, created, **kwargs):
    """Automatically create executive profile when user is created with executive role"""
    if created and instance.role == 'Executive':
        Executive.objects.create(
            user=instance,
            executive_title='general_member',
            committee='executive_committee',
            term_start_date=timezone.now().date(),
            term_end_date=timezone.now().date() + timezone.timedelta(days=365)  # 1 year term
        )

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_executive_profile(sender, instance, **kwargs):
    """Save executive profile when user is saved"""
    if hasattr(instance, 'executive'):
        instance.executive.save()