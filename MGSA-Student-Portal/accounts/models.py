# accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.conf import settings

'''class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'Admin')
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)
'''
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        # Default to student role unless specified
        extra_fields.setdefault('role', 'student')
        extra_fields.setdefault('is_active', True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Executive', 'Executive'),
        ('Admin', 'Admin'),
    ]
    
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    
    YEAR_CHOICES = [
        ('Fresh', 'Fresh'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
        ('4th Year', '4th Year'),
        ('5th Year', '5th Year'),
    ]
    
    ZONE_CHOICES = [
        ('West Hararghe', 'West Hararghe'),
        ('East Hararghe', 'East Hararghe'),
    ]
    
    # Personal Information
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    # Geographical Information
    zone = models.CharField(max_length=20, choices=ZONE_CHOICES)
    woreda = models.CharField(max_length=100)
    kebele = models.CharField(max_length=100, blank=True)
    
    # Academic Information
    college = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    year_of_study = models.CharField(max_length=10, choices=YEAR_CHOICES)
    
    # Authentication
    email = models.EmailField(unique=True)
    student_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    # Role and Profile
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='Student')
    executive_title = models.CharField(max_length=50, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Preferences
    preferred_language = models.CharField(max_length=2, choices=[('en', 'English'), ('om', 'Afan Oromo')], default='en')
    preferred_theme = models.CharField(max_length=10, choices=[('light', 'Light'), ('dark', 'Dark')], default='light')
    
    # Status - THESE FIELDS ARE CRITICAL FOR ADMIN ACCESS
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Controls admin site access
    is_superuser = models.BooleanField(default=False)  # Controls all permissions
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    # CRITICAL: Proper permission methods for Django admin
    def has_perm(self, perm, obj=None):
        """
        Does the user have a specific permission?
        - Superusers have all permissions
        - Staff users have permissions based on their role
        """
        if self.is_active and self.is_superuser:
            return True
        
        # For staff users who are not superusers
        if self.is_active and self.is_staff:
            # Admin role users get most permissions
            if self.role == 'Admin':
                return True
            # Executive role users get limited admin access
            elif self.role == 'Executive':
                return perm in [
                    'accounts.view_user',
                    'posts.view_post',
                    'posts.add_post',
                    'posts.change_post',
                    'posts.delete_post',
                    'resources.view_resource',
                    'resources.add_resource', 
                    'resources.change_resource',
                    'resources.delete_resource',
                    'tutorials.view_tutorial',
                    'tutorials.add_tutorial',
                    'tutorials.change_tutorial',
                    'tutorials.delete_tutorial',
                ]
        
        return False

    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        """
        if self.is_active and self.is_superuser:
            return True
        
        if self.is_active and self.is_staff:
            # Admin role can access all apps
            if self.role == 'Admin':
                return True
            # Executive role can access specific apps
            elif self.role == 'Executive':
                return app_label in ['accounts', 'posts', 'resources', 'tutorials']
        
        return False

    @property
    def full_address(self):
        """Return complete geographical address"""
        address_parts = []
        if self.kebele:
            address_parts.append(self.kebele)
        if self.woreda:
            address_parts.append(self.woreda)
        if self.zone:
            address_parts.append(self.zone)
        return ", ".join(address_parts)

# Geographical and Academic Models
class Zone(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Zone'
        verbose_name_plural = 'Zones'

class Woreda(models.Model):
    name = models.CharField(max_length=100)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='woredas')
    
    class Meta:
        unique_together = ['name', 'zone']
        verbose_name = 'Woreda'
        verbose_name_plural = 'Woredas'
    
    def __str__(self):
        return f"{self.name} - {self.zone}"

class Kebele(models.Model):
    name = models.CharField(max_length=100)
    woreda = models.ForeignKey(Woreda, on_delete=models.CASCADE, related_name='kebeles')
    
    class Meta:
        unique_together = ['name', 'woreda']
        verbose_name = 'Kebele'
        verbose_name_plural = 'Kebeles'
    
    def __str__(self):
        return f"{self.name} - {self.woreda}"

class College(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'College'
        verbose_name_plural = 'Colleges'

class Department(models.Model):
    name = models.CharField(max_length=100)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='departments')
    
    class Meta:
        unique_together = ['name', 'college']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
    
    def __str__(self):
        return f"{self.name} - {self.college}"
# Executive Profile Model
class Executive(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='executive_profile'
    )
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.title}"
    
    class Meta:
        verbose_name = 'Executive Profile'
        verbose_name_plural = 'Executive Profiles'   
