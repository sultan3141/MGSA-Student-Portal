from django.db import models
from django.conf import settings
from django.utils import timezone

class Executive(models.Model):
    EXECUTIVE_TITLES = [
        ('president', 'President'),
        ('vice_president', 'Vice President'),
        ('secretary', 'Secretary'),
        ('treasurer', 'Treasurer'),
        ('academic_head', 'Academic Head'),
        ('events_coordinator', 'Events Coordinator'),
        ('public_relations', 'Public Relations Officer'),
        ('it_coordinator', 'IT Coordinator'),
        ('department_representative', 'Department Representative'),
        ('general_member', 'General Member'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('computer_science', 'Computer Science'),
        ('business', 'Business Administration'),
        ('engineering', 'Engineering'),
        ('medicine', 'Medicine'),
        ('law', 'Law'),
        ('arts', 'Arts and Humanities'),
        ('science', 'Natural Sciences'),
        ('social_sciences', 'Social Sciences'),
        ('education', 'Education'),
    ]
    
    COMMITTEE_CHOICES = [
        ('executive_committee', 'Executive Committee'),
        ('academic_committee', 'Academic Committee'),
        ('events_committee', 'Events Committee'),
        ('finance_committee', 'Finance Committee'),
        ('publicity_committee', 'Publicity Committee'),
        ('welfare_committee', 'Welfare Committee'),
        ('sports_committee', 'Sports Committee'),
        ('cultural_committee', 'Cultural Committee'),
    ]
    
    # One-to-one relationship with User
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='executive'
    )
    
    # Executive Information
    executive_title = models.CharField(max_length=50, choices=EXECUTIVE_TITLES)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True)
    committee = models.CharField(max_length=50, choices=COMMITTEE_CHOICES)
    
    # Term Information
    term_start_date = models.DateField()
    term_end_date = models.DateField()
    is_current = models.BooleanField(default=True)
    
    # Contact Information for Executive Role
    office_phone = models.CharField(max_length=15, blank=True)
    office_location = models.CharField(max_length=100, blank=True)
    office_hours = models.JSONField(
        default=list,
        blank=True,
        help_text="Office hours in JSON format"
    )
    
    # Executive Bio and Responsibilities
    bio = models.TextField(blank=True, help_text="Executive role biography")
    responsibilities = models.JSONField(
        default=list,
        blank=True,
        help_text="List of responsibilities"
    )
    goals = models.JSONField(
        default=list,
        blank=True,
        help_text="Goals for the term"
    )
    
    # Executive Performance
    performance_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    tasks_completed = models.PositiveIntegerField(default=0)
    tasks_pending = models.PositiveIntegerField(default=0)
    
    # Permissions and Access
    can_approve_posts = models.BooleanField(default=False)
    can_approve_resources = models.BooleanField(default=False)
    can_manage_tutorials = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_executives'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['executive_title', 'user__first_name', 'user__last_name']
        verbose_name = 'Executive'
        verbose_name_plural = 'Executives'
        indexes = [
            models.Index(fields=['executive_title']),
            models.Index(fields=['department']),
            models.Index(fields=['committee']),
            models.Index(fields=['is_current']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_executive_title_display()} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Update is_current based on term dates
        today = timezone.now().date()
        self.is_current = self.term_start_date <= today <= self.term_end_date
        
        # Set permissions based on executive title
        self.set_permissions_based_on_title()
        
        super().save(*args, **kwargs)
    
    def set_permissions_based_on_title(self):
        """Set permissions based on executive title"""
        if self.executive_title in ['president', 'vice_president']:
            self.can_approve_posts = True
            self.can_approve_resources = True
            self.can_manage_tutorials = True
            self.can_view_analytics = True
            self.can_manage_users = True
        elif self.executive_title in ['academic_head', 'it_coordinator']:
            self.can_approve_posts = True
            self.can_approve_resources = True
            self.can_manage_tutorials = True
            self.can_view_analytics = True
        elif self.executive_title in ['secretary', 'treasurer']:
            self.can_approve_posts = True
            self.can_view_analytics = True
        else:
            # Default permissions for other roles
            self.can_approve_posts = False
            self.can_approve_resources = False
            self.can_manage_tutorials = False
            self.can_view_analytics = False
            self.can_manage_users = False
    
    def is_term_active(self):
        """Check if the executive's term is currently active"""
        today = timezone.now().date()
        return self.term_start_date <= today <= self.term_end_date
    
    def days_remaining_in_term(self):
        """Calculate days remaining in term"""
        today = timezone.now().date()
        if today > self.term_end_date:
            return 0
        return (self.term_end_date - today).days
    
    def get_responsibilities_list(self):
        """Get responsibilities as a list"""
        return self.responsibilities if isinstance(self.responsibilities, list) else []
    
    def get_goals_list(self):
        """Get goals as a list"""
        return self.goals if isinstance(self.goals, list) else []
    
    def get_office_hours_display(self):
        """Format office hours for display"""
        if not self.office_hours:
            return "Not specified"
        
        hours_list = []
        for hour in self.office_hours:
            if isinstance(hour, dict):
                hours_list.append(f"{hour.get('day', '')}: {hour.get('time', '')}")
            else:
                hours_list.append(str(hour))
        
        return "; ".join(hours_list)
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def email(self):
        return self.user.email
    
    @property
    def phone(self):
        return self.user.phone

class ExecutiveTask(models.Model):
    TASK_PRIORITIES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    TASK_STATUS = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
    ]
    
    executive = models.ForeignKey(
        Executive,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=TASK_PRIORITIES, default='medium')
    status = models.CharField(max_length=15, choices=TASK_STATUS, default='pending')
    
    # Dates
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Task Details
    estimated_hours = models.PositiveIntegerField(default=1)
    actual_hours = models.PositiveIntegerField(null=True, blank=True)
    progress_percentage = models.PositiveIntegerField(default=0)
    
    # Relations
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_tasks'
    )
    
    # Notes and Attachments
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to='executive_tasks/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date', 'priority']
        verbose_name = 'Executive Task'
        verbose_name_plural = 'Executive Tasks'
    
    def __str__(self):
        return f"{self.title} - {self.executive.user.get_full_name()}"
    
    def is_overdue(self):
        """Check if task is overdue"""
        return self.due_date < timezone.now() and self.status != 'completed'
    
    def mark_completed(self):
        """Mark task as completed"""
        self.status = 'completed'
        self.completed_date = timezone.now()
        self.progress_percentage = 100
        self.save()
    
    def update_progress(self, percentage):
        """Update task progress"""
        self.progress_percentage = min(100, max(0, percentage))
        if self.progress_percentage == 100:
            self.status = 'completed'
            self.completed_date = timezone.now()
        elif self.progress_percentage > 0:
            self.status = 'in_progress'
        self.save()

class ExecutiveMeeting(models.Model):
    MEETING_TYPES = [
        ('general', 'General Meeting'),
        ('executive', 'Executive Meeting'),
        ('committee', 'Committee Meeting'),
        ('emergency', 'Emergency Meeting'),
        ('planning', 'Planning Meeting'),
    ]
    
    title = models.CharField(max_length=200)
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPES, default='general')
    description = models.TextField(blank=True)
    
    # Schedule
    meeting_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    location = models.CharField(max_length=100, blank=True)
    virtual_link = models.URLField(blank=True)
    
    # Organizer
    organized_by = models.ForeignKey(
        Executive,
        on_delete=models.CASCADE,
        related_name='organized_meetings'
    )
    
    # Attendees
    attendees = models.ManyToManyField(
        Executive,
        through='MeetingAttendance',
        related_name='meetings_attended'
    )
    
    # Agenda and Minutes
    agenda = models.JSONField(default=list, blank=True)
    minutes = models.TextField(blank=True)
    decisions_made = models.JSONField(default=list, blank=True)
    action_items = models.JSONField(default=list, blank=True)
    
    # Status
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-meeting_date']
        verbose_name = 'Executive Meeting'
        verbose_name_plural = 'Executive Meetings'
    
    def __str__(self):
        return f"{self.title} - {self.meeting_date.strftime('%Y-%m-%d %H:%M')}"
    
    def is_upcoming(self):
        """Check if meeting is upcoming"""
        return self.meeting_date > timezone.now() and not self.is_cancelled
    
    def get_attendees_count(self):
        """Get count of confirmed attendees"""
        return self.attendees.filter(meetingattendance__attended=True).count()

class MeetingAttendance(models.Model):
    """Through model for meeting attendance"""
    executive = models.ForeignKey(Executive, on_delete=models.CASCADE)
    meeting = models.ForeignKey(ExecutiveMeeting, on_delete=models.CASCADE)
    
    rsvp_status = models.CharField(
        max_length=10,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('declined', 'Declined'),
        ],
        default='pending'
    )
    
    attended = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['executive', 'meeting']
        verbose_name = 'Meeting Attendance'
        verbose_name_plural = 'Meeting Attendances'
    
    def __str__(self):
        return f"{self.executive.user.get_full_name()} - {self.meeting.title}"

class ExecutiveReport(models.Model):
    REPORT_TYPES = [
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('quarterly', 'Quarterly Report'),
        ('annual', 'Annual Report'),
        ('special', 'Special Report'),
    ]
    
    executive = models.ForeignKey(
        Executive,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Report Content
    accomplishments = models.JSONField(default=list, blank=True)
    challenges = models.JSONField(default=list, blank=True)
    lessons_learned = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    next_steps = models.JSONField(default=list, blank=True)
    
    # Metrics
    tasks_completed = models.PositiveIntegerField(default=0)
    tasks_pending = models.PositiveIntegerField(default=0)
    meetings_attended = models.PositiveIntegerField(default=0)
    initiatives_launched = models.PositiveIntegerField(default=0)
    
    # Status
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_reports'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Files
    report_file = models.FileField(upload_to='executive_reports/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_end', '-created_at']
        verbose_name = 'Executive Report'
        verbose_name_plural = 'Executive Reports'
    
    def __str__(self):
        return f"{self.title} - {self.executive.user.get_full_name()}"
    
    def submit_report(self):
        """Mark report as submitted"""
        self.is_submitted = True
        self.submitted_at = timezone.now()
        self.save()
    
    def approve_report(self, approved_by_user):
        """Approve the report"""
        self.is_approved = True
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.save()