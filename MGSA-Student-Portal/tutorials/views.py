from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Tutorial, TutorialRegistration
from .serializers import (
    TutorialSerializer, TutorialCreateSerializer,
    TutorialRegistrationSerializer, TutorialRegistrationCreateSerializer
)

class TutorialListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department', 'tutor', 'is_active']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TutorialCreateSerializer
        return TutorialSerializer
    
    def get_queryset(self):
        return Tutorial.objects.filter(is_active=True).select_related('created_by')
    
    def perform_create(self, serializer):
        # Only allow Executives and Admins to create tutorials
        if self.request.user.role in ['Executive', 'Admin']:
            serializer.save(created_by=self.request.user)
        else:
            raise permissions.PermissionDenied("Only executives and admins can create tutorials")

class TutorialDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TutorialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Tutorial.objects.select_related('created_by')
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Only allow creator or admin to update
        if instance.created_by != request.user and request.user.role != 'Admin':
            return Response({
                'success': False,
                'message': 'You can only edit your own tutorials'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Only allow creator or admin to delete
        if instance.created_by != request.user and request.user.role != 'Admin':
            return Response({
                'success': False,
                'message': 'You can only delete your own tutorials'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

class TutorialRegistrationListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TutorialRegistrationCreateSerializer
        return TutorialRegistrationSerializer
    
    def get_queryset(self):
        # Students can see their own registrations
        # Executives/Admins can see all registrations for their tutorials
        if self.request.user.role == 'Student':
            return TutorialRegistration.objects.filter(
                student=self.request.user
            ).select_related('tutorial', 'student')
        else:
            # Executives and Admins can see registrations for tutorials they created
            return TutorialRegistration.objects.filter(
                tutorial__created_by=self.request.user
            ).select_related('tutorial', 'student')
    
    def perform_create(self, serializer):
        # Only students can register for tutorials
        if self.request.user.role != 'Student':
            raise permissions.PermissionDenied("Only students can register for tutorials")
        
        serializer.save(student=self.request.user)

class TutorialRegistrationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TutorialRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'Student':
            return TutorialRegistration.objects.filter(student=self.request.user)
        else:
            return TutorialRegistration.objects.filter(tutorial__created_by=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Decrement tutorial registration count
        tutorial = instance.tutorial
        tutorial.current_registrations = max(0, tutorial.current_registrations - 1)
        tutorial.save()
        
        return super().destroy(request, *args, **kwargs)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_tutorial_registrations(request):
    if request.user.role != 'Student':
        return Response({
            'success': False,
            'message': 'Only students can view their tutorial registrations'
        }, status=status.HTTP_403_FORBIDDEN)
    
    registrations = TutorialRegistration.objects.filter(
        student=request.user
    ).select_related('tutorial')
    
    serializer = TutorialRegistrationSerializer(registrations, many=True)
    
    return Response({
        'success': True,
        'registrations': serializer.data
    })