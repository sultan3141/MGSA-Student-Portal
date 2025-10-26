from django.urls import path
from . import views

urlpatterns = [
    path('', views.TutorialListView.as_view(), name='tutorial-list'),
    path('<int:pk>/', views.TutorialDetailView.as_view(), name='tutorial-detail'),
    path('registrations/', views.TutorialRegistrationListView.as_view(), name='tutorial-registration-list'),
    path('registrations/<int:pk>/', views.TutorialRegistrationDetailView.as_view(), name='tutorial-registration-detail'),
    path('my-registrations/', views.my_tutorial_registrations, name='my-tutorial-registrations'),
]