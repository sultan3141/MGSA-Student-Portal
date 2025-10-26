from django.contrib import admin
from .models import Executive, ExecutiveTask, ExecutiveMeeting, MeetingAttendance, ExecutiveReport

@admin.register(Executive)
class ExecutiveAdmin(admin.ModelAdmin):
    list_display = ['user', 'executive_title', 'department', 'committee', 'is_current', 'is_active', 'term_start_date', 'term_end_date']
    list_filter = ['executive_title', 'department', 'committee', 'is_current', 'is_active', 'is_verified']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'executive_title')
        }),
        ('Executive Details', {
            'fields': ('department', 'committee', 'term_start_date', 'term_end_date', 'is_current')
        }),
        ('Contact Information', {
            'fields': ('office_phone', 'office_location', 'office_hours')
        }),
        ('Executive Profile', {
            'fields': ('bio', 'responsibilities', 'goals')
        }),
        ('Performance', {
            'fields': ('performance_rating', 'tasks_completed', 'tasks_pending')
        }),
        ('Permissions', {
            'fields': (
                'can_approve_posts', 'can_approve_resources', 'can_manage_tutorials',
                'can_view_analytics', 'can_manage_users'
            ),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified', 'verified_at', 'verified_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(ExecutiveTask)
class ExecutiveTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'executive', 'priority', 'status', 'due_date', 'progress_percentage']
    list_filter = ['priority', 'status', 'due_date', 'assigned_date']
    search_fields = ['title', 'description', 'executive__user__first_name', 'executive__user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def executive_name(self, obj):
        return obj.executive.user.get_full_name()
    executive_name.admin_order_field = 'executive__user__first_name'

@admin.register(ExecutiveMeeting)
class ExecutiveMeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'meeting_type', 'meeting_date', 'location', 'organized_by', 'is_cancelled']
    list_filter = ['meeting_type', 'meeting_date', 'is_cancelled']
    search_fields = ['title', 'description', 'organized_by__user__first_name', 'organized_by__user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def organized_by_name(self, obj):
        return obj.organized_by.user.get_full_name()
    organized_by_name.admin_order_field = 'organized_by__user__first_name'

@admin.register(MeetingAttendance)
class MeetingAttendanceAdmin(admin.ModelAdmin):
    list_display = ['executive', 'meeting', 'rsvp_status', 'attended']
    list_filter = ['rsvp_status', 'attended', 'meeting__meeting_date']
    search_fields = ['executive__user__first_name', 'executive__user__last_name', 'meeting__title']

@admin.register(ExecutiveReport)
class ExecutiveReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'executive', 'report_type', 'period_start', 'period_end', 'is_submitted', 'is_approved']
    list_filter = ['report_type', 'is_submitted', 'is_approved', 'period_start', 'period_end']
    search_fields = ['title', 'executive__user__first_name', 'executive__user__last_name']
    readonly_fields = ['created_at', 'updated_at']