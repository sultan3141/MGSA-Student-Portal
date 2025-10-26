from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Resource
from .serializers import ResourceSerializer, ResourceCreateSerializer

class ResourceListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'file_type', 'uploaded_by', 'is_public']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ResourceCreateSerializer
        return ResourceSerializer
    
    def get_queryset(self):
        queryset = Resource.objects.filter(is_public=True).select_related('uploaded_by')
        
        # If user is authenticated, show their private resources too
        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(is_public=True) | Q(uploaded_by=self.request.user)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        # Only allow Executives and Admins to upload resources
        if self.request.user.role in ['Executive', 'Admin']:
            serializer.save(uploaded_by=self.request.user)
        else:
            raise permissions.PermissionDenied("Only executives and admins can upload resources")

class ResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Resource.objects.select_related('uploaded_by')
        
        # If user is authenticated, show their private resources too
        if self.request.user.is_authenticated:
            return queryset.filter(
                Q(is_public=True) | Q(uploaded_by=self.request.user)
            )
        return queryset.filter(is_public=True)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Only allow uploader or admin to update
        if instance.uploaded_by != request.user and request.user.role != 'Admin':
            return Response({
                'success': False,
                'message': 'You can only edit your own resources'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Only allow uploader or admin to delete
        if instance.uploaded_by != request.user and request.user.role != 'Admin':
            return Response({
                'success': False,
                'message': 'You can only delete your own resources'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def increment_download_count(request, resource_id):
    try:
        resource = Resource.objects.get(id=resource_id)
        resource.download_count += 1
        resource.save()
        
        return Response({
            'success': True,
            'message': 'Download count incremented',
            'download_count': resource.download_count
        })
    except Resource.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Resource not found'
        }, status=status.HTTP_404_NOT_FOUND)
