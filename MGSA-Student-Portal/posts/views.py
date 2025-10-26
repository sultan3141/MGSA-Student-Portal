from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from .models import Post, Like, Comment
from .serializers import (
    PostSerializer, PostCreateSerializer, LikeSerializer,
    CommentSerializer, CommentCreateSerializer
)
from .filters import PostFilter

class PostListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'tags', 'is_public']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostSerializer
    
    def get_queryset(self):
        queryset = Post.objects.filter(is_public=True).select_related('author').prefetch_related('likes', 'comments')
        
        # If user is authenticated, show their private posts too
        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(is_public=True) | Q(author=self.request.user)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        # Only allow Executives and Admins to create posts
        if self.request.user.role in ['Executive', 'Admin']:
            serializer.save(author=self.request.user)
        else:
            raise permissions.PermissionDenied("Only executives and admins can create posts")

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Post.objects.select_related('author').prefetch_related('likes', 'comments')
        
        # If user is authenticated, show their private posts too
        if self.request.user.is_authenticated:
            return queryset.filter(
                Q(is_public=True) | Q(author=self.request.user)
            )
        return queryset.filter(is_public=True)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Only allow author or admin to update
        if instance.author != request.user and request.user.role != 'Admin':
            return Response({
                'success': False,
                'message': 'You can only edit your own posts'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Only allow author or admin to delete
        if instance.author != request.user and request.user.role != 'Admin':
            return Response({
                'success': False,
                'message': 'You can only delete your own posts'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_like(request, post_id):
    try:
        post = Post.objects.get(id=post_id, is_public=True)
    except Post.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Post not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        message = 'Post unliked'
        has_liked = False
    else:
        message = 'Post liked'
        has_liked = True
    
    likes_count = post.likes.count()
    
    return Response({
        'success': True,
        'message': message,
        'has_liked': has_liked,
        'likes_count': likes_count
    })

class CommentListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_queryset(self):
        return Comment.objects.filter(
            post_id=self.kwargs['post_id'],
            parent_comment__isnull=True
        ).select_related('user').prefetch_related('replies')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['post'] = Post.objects.get(id=self.kwargs['post_id'])
        return context

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Comment.objects.select_related('user', 'post')
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Only allow author to update
        if instance.user != request.user:
            return Response({
                'success': False,
                'message': 'You can only edit your own comments'
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance.is_edited = True
        instance.save()
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Only allow author or post author or admin to delete
        if (instance.user != request.user and 
            instance.post.author != request.user and 
            request.user.role != 'Admin'):
            return Response({
                'success': False,
                'message': 'You can only delete your own comments'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)
class PostListView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter    