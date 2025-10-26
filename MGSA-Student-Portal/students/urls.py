from django.urls import path
from . import views

urlpatterns = [
    # Student Dashboard
    path('dashboard/', views.student_dashboard, name='student-dashboard'),
    
    # Posts
    path('posts/', views.StudentPostList.as_view(), name='student-posts'),
    path('posts/<int:pk>/', views.StudentPostDetail.as_view(), name='student-post-detail'),
    path('posts/<int:post_id>/like/', views.student_like_post, name='student-like-post'),
    path('posts/<int:post_id>/comment/', views.student_comment_post, name='student-comment-post'),
    
    # Resources
    path('resources/', views.StudentResourceList.as_view(), name='student-resources'),
    path('resources/<int:resource_id>/download/', views.student_download_resource, name='student-download-resource'),
    
    # Tutorials
    path('tutorials/', views.StudentTutorialList.as_view(), name='student-tutorials'),
    path('tutorials/registrations/', views.StudentTutorialRegistrationList.as_view(), name='student-tutorial-registrations'),
    path('tutorials/registrations/<int:registration_id>/cancel/', views.student_cancel_registration, name='student-cancel-registration'),
]