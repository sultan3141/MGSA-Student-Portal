# frontend/urls.py or your main urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Main Pages
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('student-dashboard/', views.student_dashboard, name='student-dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('executive-dashboard/', views.executive_dashboard, name='executive-dashboard'),
    
    # All functionality handled within student-dashboard
]