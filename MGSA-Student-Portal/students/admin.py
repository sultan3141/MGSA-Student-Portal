'''from django.contrib import admin
from .models import Student, StudentAcademicRecord, StudentAttendance, StudentAchievement

class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'get_full_name', 'get_department', 'year_of_study', 'student_id', 'is_verified', 'is_active_student')
    list_filter = ('is_verified', 'is_active_student', 'year_of_study', 'academic_status', 'user__department')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'student_id')
    readonly_fields = ('created_at', 'updated_at', 'last_profile_update')
    list_select_related = ('user',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'student_id')
        }),
        ('Academic Information', {
            'fields': ('year_of_study', 'current_semester', 'gpa', 'cgpa', 'academic_status')
        }),
        ('Status', {
            'fields': ('is_active_student', 'is_verified', 'verified_at', 'verified_by')
        }),
        ('Additional Information', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation')
        }),
        ('Profile Information', {
            'fields': ('bio', 'interests', 'skills', 'preferred_study_methods', 'availability')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_profile_update'),
            'classes': ('collapse',)
        }),
    )
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'user__first_name'
    
    def get_department(self, obj):
        return obj.user.department if obj.user.department else '-'
    get_department.short_description = 'Department'
    get_department.admin_order_field = 'user__department'

class StudentAcademicRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_code', 'course_name', 'grade', 'semester', 'academic_year')
    list_filter = ('semester', 'academic_year', 'grade', 'is_transfer_credit')
    search_fields = ('student__user__email', 'student__user__first_name', 'course_code', 'course_name')
    list_select_related = ('student__user',)

class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'event_type', 'event_title', 'event_date', 'present')
    list_filter = ('event_type', 'present', 'event_date')
    search_fields = ('student__user__email', 'student__user__first_name', 'event_title')
    list_select_related = ('student__user',)

class StudentAchievementAdmin(admin.ModelAdmin):
    list_display = ('student', 'achievement_type', 'title', 'date_achieved', 'is_verified')
    list_filter = ('achievement_type', 'is_verified', 'date_achieved')
    search_fields = ('student__user__email', 'student__user__first_name', 'title')
    list_select_related = ('student__user',)

admin.site.register(Student, StudentAdmin)
admin.site.register(StudentAcademicRecord, StudentAcademicRecordAdmin)
admin.site.register(StudentAttendance, StudentAttendanceAdmin)
admin.site.register(StudentAchievement, StudentAchievementAdmin)'''

from django.contrib import admin
from .models import Student, StudentAcademicRecord, StudentAttendance, StudentAchievement

class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'get_full_name', 'get_department', 'get_college', 'get_zone', 'get_woreda', 'year_of_study', 'student_id', 'is_verified', 'is_active_student')
    list_filter = ('is_verified', 'is_active_student', 'year_of_study', 'academic_status', 'user__department', 'user__zone')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'student_id', 'user__department', 'user__zone')
    readonly_fields = ('created_at', 'updated_at', 'last_profile_update')
    list_select_related = ('user',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'student_id')
        }),
        ('Academic Information', {
            'fields': ('year_of_study', 'current_semester', 'gpa', 'cgpa', 'academic_status')
        }),
        ('Status', {
            'fields': ('is_active_student', 'is_verified', 'verified_at', 'verified_by')
        }),
        ('Additional Information', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation')
        }),
        ('Profile Information', {
            'fields': ('bio', 'interests', 'skills', 'preferred_study_methods', 'availability')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_profile_update'),
            'classes': ('collapse',)
        }),
    )
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'user__first_name'
    
    def get_department(self, obj):
        return obj.user.department or '-'
    get_department.short_description = 'Department'
    get_department.admin_order_field = 'user__department'
    
    def get_college(self, obj):
        return obj.user.college or '-'
    get_college.short_description = 'College'
    get_college.admin_order_field = 'user__college'
    
    def get_zone(self, obj):
        return obj.user.zone or '-'
    get_zone.short_description = 'Zone'
    get_zone.admin_order_field = 'user__zone'
    
    def get_woreda(self, obj):
        return obj.user.woreda or '-'
    get_woreda.short_description = 'Woreda'
    get_woreda.admin_order_field = 'user__woreda'

admin.site.register(Student, StudentAdmin)
admin.site.register(StudentAcademicRecord)
admin.site.register(StudentAttendance)
admin.site.register(StudentAchievement)