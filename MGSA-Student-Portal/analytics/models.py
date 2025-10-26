from django.db import models
from django.conf import settings
from django.utils import timezone

class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('suggestion', 'Suggestion'),
        ('issue', 'Issue Report'),
        ('compliment', 'Compliment'),
        ('general', 'General Feedback'),
        ('technical', 'Technical Issue'),
        ('feature_request', 'Feature Request'),
    ]
    
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # User information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback_submissions'
    )
    anonymous = models.BooleanField(default=False)
    
    # Feedback content
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, default='general')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Metadata
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='submitted')
    
    # Response and tracking
    admin_notes = models.TextField(blank=True, null=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_feedback'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['feedback_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        user_info = "Anonymous" if self.anonymous else self.user.email if self.user else "Unknown User"
        return f"{self.subject} - {user_info} - {self.get_status_display()}"
    
    def mark_as_resolved(self, resolved_by_user=None, notes=""):
        """Mark feedback as resolved"""
        self.status = 'resolved'
        self.resolved_by = resolved_by_user
        self.resolved_at = timezone.now()
        self.admin_notes = notes
        self.save()
    
    def is_resolved(self):
        return self.status in ['resolved', 'closed']
    
    def get_user_display(self):
        """Get user display name while respecting anonymity"""
        if self.anonymous:
            return "Anonymous User"
        elif self.user:
            return self.user.get_full_name() or self.user.email
        return "Unknown User"

class SystemAnalytics(models.Model):
    """System-wide analytics data"""
    date = models.DateField(unique=True)
    
    # User metrics
    total_users = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    
    # Content metrics
    total_posts = models.PositiveIntegerField(default=0)
    new_posts = models.PositiveIntegerField(default=0)
    total_resources = models.PositiveIntegerField(default=0)
    new_resources = models.PositiveIntegerField(default=0)
    
    # Tutorial metrics
    total_tutorials = models.PositiveIntegerField(default=0)
    tutorial_registrations = models.PositiveIntegerField(default=0)
    completed_tutorials = models.PositiveIntegerField(default=0)
    
    # Feedback metrics
    total_feedback = models.PositiveIntegerField(default=0)
    resolved_feedback = models.PositiveIntegerField(default=0)
    pending_feedback = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    page_views = models.PositiveIntegerField(default=0)
    average_session_duration = models.DurationField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'System Analytics'
        verbose_name_plural = 'System Analytics'
    
    def __str__(self):
        return f"Analytics for {self.date}"
    
    def feedback_resolution_rate(self):
        """Calculate feedback resolution rate"""
        if self.total_feedback == 0:
            return 0
        return (self.resolved_feedback / self.total_feedback) * 100
    
    def user_growth_rate(self, previous_day):
        """Calculate user growth rate compared to previous day"""
        if previous_day.total_users == 0:
            return 0
        return ((self.total_users - previous_day.total_users) / previous_day.total_users) * 100

class UserActivity(models.Model):
    """Track individual user activities"""
    ACTIVITY_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('post_view', 'View Post'),
        ('post_create', 'Create Post'),
        ('resource_download', 'Download Resource'),
        ('tutorial_register', 'Register for Tutorial'),
        ('feedback_submit', 'Submit Feedback'),
        ('profile_update', 'Update Profile'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True)
    
    # Additional context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Related objects (optional)
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['activity_type', 'created_at']),
        ]
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
    
    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()} - {self.created_at}"

class FeedbackCategory(models.Model):
    """Categories for organizing feedback"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3498db')  # Hex color
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Feedback Category'
        verbose_name_plural = 'Feedback Categories'
    
    def __str__(self):
        return self.name

class FeedbackResponseTemplate(models.Model):
    """Templates for common feedback responses"""
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        FeedbackCategory,
        on_delete=models.CASCADE,
        related_name='templates'
    )
    subject_template = models.CharField(max_length=200)
    message_template = models.TextField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Feedback Response Template'
        verbose_name_plural = 'Feedback Response Templates'
    
    def __str__(self):
        return self.name
