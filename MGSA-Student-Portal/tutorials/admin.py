# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Tutorial, TutorialRegistration

@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'tutor', 
        'department', 
        'start_date', 
        'end_date',
        'time',
        'current_registrations_display',
        'max_students',
        'is_active',
        'created_by',
        'created_at'
    ]
    
    list_filter = [
        'is_active',
        'department',
        'start_date',
        'end_date',
        'created_at'
    ]
    
    search_fields = [
        'title',
        'tutor',
        'department',
        'description'
    ]
    
    readonly_fields = [
        'current_registrations',
        'created_at',
        'updated_at',
        'registrations_count'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title',
                'description',
                'tutor',
                'department',
                'topics'
            )
        }),
        ('Schedule', {
            'fields': (
                'start_date',
                'end_date',
                'days',
                'time'
            )
        }),
        ('Capacity', {
            'fields': (
                'max_students',
                'current_registrations',
                'registrations_count'
            )
        }),
        ('Metadata', {
            'fields': (
                'created_by',
                'is_active',
                'created_at',
                'updated_at'
            )
        }),
    )
    
    def current_registrations_display(self, obj):
        color = 'red' if obj.is_full() else 'green'
        return format_html(
            '<span style="color: {};">{}/{} ({}%)</span>',
            color,
            obj.current_registrations,
            obj.max_students,
            int((obj.current_registrations / obj.max_students) * 100) if obj.max_students > 0 else 0
        )
    current_registrations_display.short_description = 'Registrations'
    
    def registrations_count(self, obj):
        return obj.registrations.count()
    registrations_count.short_description = 'Total Registrations (All Status)'
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('registrations')

@admin.register(TutorialRegistration)
class TutorialRegistrationAdmin(admin.ModelAdmin):
    list_display = [
        'student_email',
        'tutorial_title',
        'status_display',
        'registration_date',
        'tutorial_dates'
    ]
    
    list_filter = [
        'status',
        'registration_date',
        'tutorial__department',
        'tutorial__start_date'
    ]
    
    search_fields = [
        'student__email',
        'student__first_name',
        'student__last_name',
        'tutorial__title',
        'tutorial__tutor'
    ]
    
    readonly_fields = ['registration_date']
    
    fieldsets = (
        ('Registration Details', {
            'fields': (
                'student',
                'tutorial',
                'status',
                'registration_date'
            )
        }),
    )
    
    def student_email(self, obj):
        return obj.student.email
    student_email.short_description = 'Student Email'
    student_email.admin_order_field = 'student__email'
    
    def tutorial_title(self, obj):
        return obj.tutorial.title
    tutorial_title.short_description = 'Tutorial'
    tutorial_title.admin_order_field = 'tutorial__title'
    
    def tutorial_dates(self, obj):
        return f"{obj.tutorial.start_date} to {obj.tutorial.end_date}"
    tutorial_dates.short_description = 'Tutorial Dates'
    
    def status_display(self, obj):
        color_map = {
            'registered': 'blue',
            'attended': 'green', 
            'cancelled': 'red'
        }
        color = color_map.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'tutorial')

# Optional: Custom admin actions
def mark_registrations_attended(modeladmin, request, queryset):
    queryset.update(status='attended')
mark_registrations_attended.short_description = "Mark selected registrations as attended"

def mark_registrations_cancelled(modeladmin, request, queryset):
    queryset.update(status='cancelled')
mark_registrations_cancelled.short_description = "Mark selected registrations as cancelled"

# Add actions to TutorialRegistrationAdmin
TutorialRegistrationAdmin.actions = [mark_registrations_attended, mark_registrations_cancelled]