from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.db.models import Count
from .models import User, Zone, Woreda, Kebele, College, Department

# Custom Filters
class RoleFilter(admin.SimpleListFilter):
    title = 'Role'
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        return [
            ('Student', 'Students'),
            ('Executive', 'Executives'),
            ('Admin', 'Admins'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(role=self.value())
        return queryset

class ZoneFilter(admin.SimpleListFilter):
    title = 'Zone'
    parameter_name = 'zone'

    def lookups(self, request, model_admin):
        zones = User.objects.values_list('zone', flat=True).distinct()
        return [(zone, zone) for zone in zones if zone]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(zone=self.value())
        return queryset

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Display fields in list view
    list_display = [
        'email', 'get_full_name', 'role', 'zone', 'woreda', 
        'department', 'is_active', 'is_staff', 'is_superuser'
    ]
    
    # Filters in the right sidebar
    list_filter = [
        RoleFilter, ZoneFilter, 'is_active', 'is_staff', 'is_superuser',
        'department', 'year_of_study', 'gender'
    ]
    
    # Search fields
    search_fields = [
        'email', 'first_name', 'last_name', 'middle_name',
        'student_id', 'zone', 'woreda', 'kebele', 'department'
    ]
    
    # Default ordering
    ordering = ['-date_joined']
    
    # Read-only fields
    readonly_fields = ['date_joined', 'last_login', 'updated_at']
    
    # Field organization in edit form
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'password')
        }),
        ('Personal Information', {
            'fields': (
                'first_name', 'middle_name', 'last_name', 'gender',
                'profile_picture'
            )
        }),
        ('Geographical Information', {
            'fields': ('zone', 'woreda', 'kebele')
        }),
        ('Academic Information', {
            'fields': ('college', 'department', 'year_of_study', 'student_id')
        }),
        ('Role & Preferences', {
            'fields': (
                'role', 'executive_title', 'preferred_language',
                'preferred_theme'
            )
        }),
        ('Admin Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups',
                'user_permissions'
            )
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'updated_at')
        }),
    )
    
    # Fields when creating new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2', 
                'first_name', 'last_name', 'role',
                'is_active', 'is_staff', 'is_superuser'
            ),
        }),
    )
    
    # Custom method for display
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'first_name'
    
    # Bulk actions
    actions = ['make_admin', 'make_executive', 'make_student', 'activate_users', 'deactivate_users']
    
    def make_admin(self, request, queryset):
        updated = queryset.update(role='Admin', is_staff=True)
        self.message_user(request, f'{updated} users were made Admins.')
    make_admin.short_description = "Make selected users Admins"
    
    def make_executive(self, request, queryset):
        updated = queryset.update(role='Executive', is_staff=True)
        self.message_user(request, f'{updated} users were made Executives.')
    make_executive.short_description = "Make selected users Executives"
    
    def make_student(self, request, queryset):
        updated = queryset.update(role='Student', is_staff=False)
        self.message_user(request, f'{updated} users were made Students.')
    make_student.short_description = "Make selected users Students"
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users were activated.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users were deactivated.')
    deactivate_users.short_description = "Deactivate selected users"

# Simple admin for geographical models
@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_count']
    search_fields = ['name']
    
    def student_count(self, obj):
        return User.objects.filter(zone=obj.name, role='Student').count()
    student_count.short_description = 'Students'

@admin.register(Woreda)
class WoredaAdmin(admin.ModelAdmin):
    list_display = ['name', 'zone', 'student_count']
    list_filter = ['zone']
    search_fields = ['name', 'zone__name']
    
    def student_count(self, obj):
        return User.objects.filter(woreda=obj.name, role='Student').count()
    student_count.short_description = 'Students'

@admin.register(Kebele)
class KebeleAdmin(admin.ModelAdmin):
    list_display = ['name', 'woreda', 'zone', 'student_count']
    list_filter = ['woreda__zone', 'woreda']
    search_fields = ['name', 'woreda__name']
    
    def zone(self, obj):
        return obj.woreda.zone
    zone.short_description = 'Zone'
    
    def student_count(self, obj):
        return User.objects.filter(kebele=obj.name, role='Student').count()
    student_count.short_description = 'Students'

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_count', 'department_count']
    search_fields = ['name']
    
    def student_count(self, obj):
        return User.objects.filter(college=obj.name, role='Student').count()
    student_count.short_description = 'Students'
    
    def department_count(self, obj):
        return obj.departments.count()
    department_count.short_description = 'Departments'

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'college', 'student_count']
    list_filter = ['college']
    search_fields = ['name', 'college__name']
    
    def student_count(self, obj):
        return User.objects.filter(department=obj.name, role='Student').count()
    student_count.short_description = 'Students'
    
