from django.urls import path
from . import views

urlpatterns = [
    # Executive Dashboard
    path('dashboard/', views.executive_dashboard, name='executive-dashboard'),
    
    # Post Management
    path('posts/', views.ExecutivePostListCreate.as_view(), name='executive-posts'),
    path('posts/<int:pk>/', views.ExecutivePostDetail.as_view(), name='executive-post-detail'),
    
    # Resource Management
    path('resources/', views.ExecutiveResourceListCreate.as_view(), name='executive-resources'),
    path('resources/<int:pk>/', views.ExecutiveResourceDetail.as_view(), name='executive-resource-detail'),
    
    # Tutorial Management
    path('tutorials/', views.ExecutiveTutorialListCreate.as_view(), name='executive-tutorials'),
    path('tutorials/<int:pk>/', views.ExecutiveTutorialDetail.as_view(), name='executive-tutorial-detail'),
    path('tutorials/<int:tutorial_id>/registrations/', views.executive_tutorial_registrations, name='executive-tutorial-registrations'),
]