from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import User
from posts.models import Post, Like, Comment
from resources.models import Resource
from tutorials.models import Tutorial, TutorialRegistration
from posts.serializers import PostSerializer, CommentSerializer
from resources.serializers import ResourceSerializer
from tutorials.serializers import TutorialSerializer, TutorialRegistrationSerializer

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_dashboard(request):
    """Student dashboard with personalized content"""
    if request.user.role != 'Student':
        return Response({
            'success': False,
            'message': 'Access denied. Student access only.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Student information
    student_info = {
        'name': f"{request.user.first_name} {request.user.last_name}",
        'department': request.user.department,
        'year_of_study': request.user.year_of_study,
        'college': request.user.college,
        'email': request.user.email,
        'student_id': request.user.student_id
    }
    
    # Recent posts (from user's department or general)
    recent_posts = Post.objects.filter(is_public=True).select_related(
        'author'
    ).prefetch_related('likes', 'comments').order_by('-created_at')[:10]
    
    posts_data = []
    for post in recent_posts:
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
            'author_name': f"{post.author.first_name} {post.author.last_name}",
            'author_role': post.author.role,
            'author_title': post.author.executive_title,
            'created_at': post.created_at,
            'likes_count': post.likes.count(),
            'comments_count': post.comments.count(),
            'has_liked': post.likes.filter(user=request.user).exists(),
            'media_count': len(post.media) if hasattr(post, 'media') else 0
        })
    
    # Recommended resources (from student's department)
    recommended_resources = Resource.objects.filter(
        Q(is_public=True) | Q(uploaded_by__department=request.user.department)
    ).select_related('uploaded_by').order_by('-download_count', '-created_at')[:8]
    
    resources_data = []
    for resource in recommended_resources:
        resources_data.append({
            'id': resource.id,
            'title': resource.title,
            'description': resource.description,
            'file_type': resource.file_type,
            'file_size': resource.file_size,
            'download_count': resource.download_count,
            'uploaded_by': f"{resource.uploaded_by.first_name} {resource.uploaded_by.last_name}",
            'created_at': resource.created_at
        })
    
    # Available tutorials (for student's department)
    available_tutorials = Tutorial.objects.filter(
        is_active=True,
        department=request.user.department
    ).annotate(
        available_slots=Count('max_students') - Count('registrations')
    ).order_by('-created_at')[:6]
    
    tutorials_data = []
    for tutorial in available_tutorials:
        tutorials_data.append({
            'id': tutorial.id,
            'title': tutorial.title,
            'description': tutorial.description,
            'tutor': tutorial.tutor,
            'topics': tutorial.topics,
            'schedule': tutorial.schedule,
            'max_students': tutorial.max_students,
            'current_registrations': tutorial.current_registrations,
            'available_slots': tutorial.max_students - tutorial.current_registrations,
            'is_full': tutorial.current_registrations >= tutorial.max_students,
            'start_date': tutorial.start_date,
            'end_date': tutorial.end_date
        })
    
    # Student's tutorial registrations
    student_registrations = TutorialRegistration.objects.filter(
        student=request.user
    ).select_related('tutorial').order_by('-registration_date')[:5]
    
    registrations_data = []
    for registration in student_registrations:
        registrations_data.append({
            'id': registration.id,
            'tutorial_title': registration.tutorial.title,
            'tutor': registration.tutorial.tutor,
            'registration_date': registration.registration_date,
            'status': registration.status,
            'tutorial_status': 'Active' if registration.tutorial.is_active else 'Completed'
        })
    
    # Student's activity stats
    student_stats = {
        'posts_liked': Like.objects.filter(user=request.user).count(),
        'comments_made': Comment.objects.filter(author=request.user).count(),
        'resources_downloaded': 0,  # You might want to track this
        'tutorials_registered': TutorialRegistration.objects.filter(student=request.user).count()
    }
    
    return Response({
        'success': True,
        'dashboard': {
            'student_info': student_info,
            'student_stats': student_stats,
            'recent_posts': posts_data,
            'recommended_resources': resources_data,
            'available_tutorials': tutorials_data,
            'my_registrations': registrations_data
        }
    })

class StudentPostList(generics.ListAPIView):
    """Students can view all public posts"""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'tags']
    
    def get_queryset(self):
        if self.request.user.role == 'Student':
            return Post.objects.filter(is_public=True).select_related(
                'author'
            ).prefetch_related('likes', 'comments').order_by('-created_at')
        return Post.objects.none()

class StudentPostDetail(generics.RetrieveAPIView):
    """Students can view individual post details"""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'Student':
            return Post.objects.filter(is_public=True)
        return Post.objects.none()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def student_like_post(request, post_id):
    """Students can like/unlike posts"""
    if request.user.role != 'Student':
        return Response({
            'success': False,
            'message': 'Access denied. Student access only.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        post = Post.objects.get(id=post_id, is_public=True)
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
    
    except Post.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Post not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def student_comment_post(request, post_id):
    """Students can comment on posts"""
    if request.user.role != 'Student':
        return Response({
            'success': False,
            'message': 'Access denied. Student access only.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        post = Post.objects.get(id=post_id, is_public=True)
        content = request.data.get('content', '').strip()
        
        if not content:
            return Response({
                'success': False,
                'message': 'Comment content is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content
        )
        
        return Response({
            'success': True,
            'message': 'Comment added successfully',
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'author_name': f"{request.user.first_name} {request.user.last_name}",
                'created_at': comment.created_at
            }
        })
    
    except Post.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Post not found'
        }, status=status.HTTP_404_NOT_FOUND)

class StudentResourceList(generics.ListAPIView):
    """Students can view all public resources"""
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'file_type', 'uploaded_by']
    
    def get_queryset(self):
        if self.request.user.role == 'Student':
            return Resource.objects.filter(is_public=True).select_related('uploaded_by').order_by('-created_at')
        return Resource.objects.none()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def student_download_resource(request, resource_id):
    """Students can download resources (increment download count)"""
    if request.user.role != 'Student':
        return Response({
            'success': False,
            'message': 'Access denied. Student access only.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        resource = Resource.objects.get(id=resource_id, is_public=True)
        resource.download_count += 1
        resource.save()
        
        return Response({
            'success': True,
            'message': 'Download recorded',
            'resource': {
                'id': resource.id,
                'title': resource.title,
                'file_url': resource.file_url,
                'file_name': resource.file_name,
                'download_count': resource.download_count
            }
        })
    
    except Resource.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Resource not found'
        }, status=status.HTTP_404_NOT_FOUND)

class StudentTutorialList(generics.ListAPIView):
    """Students can view available tutorials"""
    serializer_class = TutorialSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department', 'tutor']
    
    def get_queryset(self):
        if self.request.user.role == 'Student':
            return Tutorial.objects.filter(is_active=True).select_related('created_by').order_by('-created_at')
        return Tutorial.objects.none()

class StudentTutorialRegistrationList(generics.ListCreateAPIView):
    """Students can register for tutorials and view their registrations"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        return TutorialRegistrationSerializer
    
    def get_queryset(self):
        if self.request.user.role == 'Student':
            return TutorialRegistration.objects.filter(student=self.request.user).select_related('tutorial')
        return TutorialRegistration.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role == 'Student':
            tutorial = serializer.validated_data['tutorial']
            
            # Check if tutorial is active
            if not tutorial.is_active:
                raise permissions.PermissionDenied("This tutorial is not active")
            
            # Check if tutorial is full
            if tutorial.current_registrations >= tutorial.max_students:
                raise permissions.PermissionDenied("This tutorial is full")
            
            # Check if already registered
            if TutorialRegistration.objects.filter(student=self.request.user, tutorial=tutorial).exists():
                raise permissions.PermissionDenied("You are already registered for this tutorial")
            
            # Increment registration count
            tutorial.current_registrations += 1
            tutorial.save()
            
            serializer.save(student=self.request.user)
        else:
            raise permissions.PermissionDenied("Only students can register for tutorials")

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def student_cancel_registration(request, registration_id):
    """Students can cancel their tutorial registration"""
    if request.user.role != 'Student':
        return Response({
            'success': False,
            'message': 'Access denied. Student access only.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        registration = TutorialRegistration.objects.get(
            id=registration_id, 
            student=request.user,
            status='registered'
        )
        
        # Decrement tutorial registration count
        tutorial = registration.tutorial
        tutorial.current_registrations = max(0, tutorial.current_registrations - 1)
        tutorial.save()
        
        registration.status = 'cancelled'
        registration.save()
        
        return Response({
            'success': True,
            'message': 'Registration cancelled successfully'
        })
    
    except TutorialRegistration.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Registration not found or cannot be cancelled'
        }, status=status.HTTP_404_NOT_FOUND)
