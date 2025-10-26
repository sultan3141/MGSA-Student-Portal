from django.urls import path, include
from knox import views as knox_views
from . import views
from accounts.views import login_page, login_submit, register_page, logout_view

urlpatterns = [
    # Authentication
    path('register/', register_page, name='register-page'),
    path('login/submit/', login_submit, name='login'), 
    path('login/', login_page, name='login-page'), 
    path('logout/', logout_view, name='logout'),  
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    
    # Template views
    path('register/', views.register_page, name='register-page'),
    path('login/', views.login_page, name='login-page'),
    path('login/submit/', views.login_submit, name='login-submit'),
    path('logout/', views.logout_view, name='logout'),
    
    # User profile
    path('me/', views.get_current_user, name='get_current_user'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', views.UserUpdateView.as_view(), name='user-update'),
    path('change-password/', views.change_password, name='change-password'),
    
    # Admin user management
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/role/', views.UserRoleUpdateView.as_view(), name='user-role-update'),
    
    # Geographical and academic data
    path('zones/', views.ZoneListView.as_view(), name='zone-list'),
    path('woredas/', views.WoredaListView.as_view(), name='woreda-list'),
    path('colleges/', views.CollegeListView.as_view(), name='college-list'),
    path('departments/', views.DepartmentListView.as_view(), name='department-list'),
    
    path('api/login/', views.api_login, name='api-login'),
    path('api/users/', views.api_get_users, name='api-users'),
]