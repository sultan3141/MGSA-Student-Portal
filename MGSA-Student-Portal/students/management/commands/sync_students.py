from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from students.models import Student

User = get_user_model()

class Command(BaseCommand):
    help = 'Sync Student objects for existing users with Student role'

    def handle(self, *args, **options):
        # Get all users with Student role
        student_users = User.objects.filter(role='Student')
        
        self.stdout.write(f"Found {student_users.count()} users with Student role")
        
        created_count = 0
        for user in student_users:
            # Create Student profile if it doesn't exist
            student, created = Student.objects.get_or_create(user=user)
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created Student profile for {user.email}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Student profile already exists for {user.email}')
                )
        
        total_students = Student.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully synced {created_count} new Student profiles. Total students: {total_students}')
        )