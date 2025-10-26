"""
URL configuration for mgsa_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL configuration for mgsa_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from accounts import admin_views
from . import views

@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'MGSA Portal API',
        'version': '1.0.0',
        'endpoints': {
            'authentication': '/api/auth/',
            'posts': '/api/posts/', 
            'resources': '/api/resources/',
            'tutorials': '/api/tutorials/',
            'analytics': '/api/analytics/',
            'executive': '/api/executive/',
            'student': '/api/student/',
        }
    })

# Custom admin URLs
admin_urlpatterns = [
    path('geographical-report/', admin_views.student_geographical_report, name='student_geographical_report'),
    path('export-students-csv/', admin_views.export_students_csv, name='export_students_csv'),
    path('student-demographics/', admin_views.student_demographics, name='student_demographics'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/reports/', include(admin_urlpatterns)),
    path('api/', api_root, name='api-root'),
    path('api/auth/', include('accounts.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/resources/', include('resources.urls')),
    path('api/tutorials/', include('tutorials.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/executive/', include('executive.urls')),
    path('api/student/', include('students.urls')),
    
    # Main pages
    path('', views.index, name='index'),
    
    # Authentication URLs
    path('login/', views.login_page, name='login-page'),
    path('login/submit/', views.login_submit, name='login-submit'),
    path('register/', views.register_page, name='register-page'),
    path('logout/', views.logout_view, name='logout'),
    path('register/submit/', views.register_submit, name='register-submit'),
    path('force-logout/', views.force_logout, name='force-logout'),
    
    # Dashboard pages
    path('student-dashboard/', views.student_dashboard, name='student-dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('executive-dashboard/', views.executive_dashboard, name='executive-dashboard'),
    path('contact/feedback/', views.contact_feedback, name='contact_feedback'),
    path('tutorials/', include('tutorials.urls')),
    
    # Tutorial URLs
    path('tutorials/register/', views.register_tutorial, name='register_tutorial'),
    path('tutorials/cancel/<int:registration_id>/', views.cancel_tutorial_registration, name='cancel_tutorial_registration'),
    
    # Redirects
    path('login/pages/student-dashboard.html', lambda request: redirect('student-dashboard')),
    path('login/pages/admin-dashboard.html', lambda request: redirect('admin-dashboard')),
    path('login/pages/executive-dashboard.html', lambda request: redirect('executive-dashboard')),
    path('accounts/login/', lambda request: redirect('/login' + request.GET.get('next', '/')), name='accounts-login'),
    path('contact/feedback/', views.contact_feedback, name='contact_feedback'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)