from django.contrib import admin
from .models import Feedback, SystemAnalytics, UserActivity, FeedbackCategory, FeedbackResponseTemplate

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['subject', 'user', 'feedback_type', 'priority', 'status', 'created_at']
    list_filter = ['feedback_type', 'status', 'priority', 'anonymous', 'created_at']
    search_fields = ['subject', 'message', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['mark_as_resolved', 'mark_as_under_review']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'anonymous')
        }),
        ('Feedback Content', {
            'fields': ('feedback_type', 'subject', 'message', 'priority')
        }),
        ('Status & Response', {
            'fields': ('status', 'admin_notes', 'resolved_by', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status='resolved', resolved_by=request.user)
        self.message_user(request, f'{updated} feedback items marked as resolved.')
    mark_as_resolved.short_description = "Mark selected feedback as resolved"
    
    def mark_as_under_review(self, request, queryset):
        updated = queryset.update(status='under_review')
        self.message_user(request, f'{updated} feedback items marked as under review.')
    mark_as_under_review.short_description = "Mark selected feedback as under review"

@admin.register(SystemAnalytics)
class SystemAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_users', 'new_users', 'total_posts', 'tutorial_registrations']
    list_filter = ['date']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'created_at', 'ip_address']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

@admin.register(FeedbackCategory)
class FeedbackCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

@admin.register(FeedbackResponseTemplate)
class FeedbackResponseTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'subject_template']
