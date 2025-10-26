from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    path('dashboard-stats/', views.dashboard_stats, name='dashboard-stats'),
    path('export-users/excel/', views.export_users_excel, name='export-users-excel'),
    path('export-users/pdf/', views.export_users_pdf, name='export-users-pdf'),

    # Dashboard
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin-dashboard'),
    
    # User Management
    path('admin/users/', admin_views.user_management, name='user-management'),
    path('admin/users/<int:user_id>/role/', admin_views.update_user_role, name='update-user-role'),
    path('admin/users/<int:user_id>/deactivate/', admin_views.deactivate_user, name='deactivate-user'),
    path('admin/users/<int:user_id>/activate/', admin_views.activate_user, name='activate-user'),
    
    # Content Management
    path('admin/content/', admin_views.content_management, name='content-management'),
    path('admin/content/<str:content_type>/<int:content_id>/delete/', admin_views.delete_content, name='delete-content'),
    path('admin/content/<str:content_type>/<int:content_id>/visibility/', admin_views.toggle_content_visibility, name='toggle-content-visibility'),
    
    # Export Data
    path('admin/export/', admin_views.export_data, name='export-data'),
    
    # System Settings
    path('admin/settings/', admin_views.system_settings, name='system-settings'),
    path('admin/settings/update/', admin_views.update_system_settings, name='update-system-settings'),
    
    # Analytics endpoints
    path('dashboard-stats/', views.dashboard_stats, name='dashboard_stats'),
    path('feedback-analytics/', views.feedback_analytics, name='feedback_analytics'),
    path('user-activity-logs/', views.user_activity_logs, name='user_activity_logs'),
    
    # Export endpoints
    path('export-users-excel/', views.export_users_excel, name='export_users_excel'),
    path('export-users-pdf/', views.export_users_pdf, name='export_users_pdf'),
    
    # Feedback endpoints
    path('feedback/submit/', views.submit_feedback, name='submit_feedback'),
]