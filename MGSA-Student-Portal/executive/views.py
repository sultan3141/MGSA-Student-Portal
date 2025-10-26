from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
from django.utils import timezone

from accounts.models import User
from posts.models import Post, Comment
from resources.models import Resource
from tutorials.models import Tutorial, TutorialRegistration
from posts.serializers import PostSerializer, PostCreateSerializer
from resources.serializers import ResourceSerializer, ResourceCreateSerializer
from tutorials.serializers import TutorialSerializer, TutorialCreateSerializer

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def executive_dashboard(request):
    """Executive dashboard with limited analytics"""
    if request.user.role not in ['Executive', 'Admin']:
        return Response({
            'success': False,
            'message': 'Access denied. Executive privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Date range for analytics (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Basic analytics that executives can see
    user_stats = User.objects.filter(
        is_active=True, 
        role='Student'
    ).aggregate(
        total_students=Count('id'),
        new_students_30_days=Count('id', filter=Q(date_joined__gte=thirty_days_ago))
    )
    
    # Department breakdown (executives can see this)
    students_by_department = User.objects.filter(
        is_active=True, 
        role='Student'
    ).values('department').annotate(count=Count('id')).order_by('-count')[:10]
    
    # Year breakdown
    students_by_year = User.objects.filter(
        is_active=True, 
        role='Student'
    ).values('year_of_study').annotate(count=Count('id')).order_by('year_of_study')
    
    # Posts created by this executive
    executive_posts = Post.objects.filter(author=request.user).aggregate(
        total_posts=Count('id'),
        posts_30_days=Count('id', filter=Q(created_at__gte=thirty_days_ago)),
        total_likes=Count('likes'),
        total_comments=Count('comments')
    )
    
    # Resources uploaded by this executive
    executive_resources = Resource.objects.filter(uploaded_by=request.user).aggregate(
        total_resources=Count('id'),
        total_downloads=Count('download_count'),
        resources_30_days=Count('id', filter=Q(created_at__gte=thirty_days_ago))
    )
    
    # Tutorials created by this executive
    executive_tutorials = Tutorial.objects.filter(created_by=request.user).aggregate(
        total_tutorials=Count('id'),
        total_registrations=Count('registrations'),
        active_tutorials=Count('id', filter=Q(is_active=True))
    )
    
    # Recent executive activities
    recent_posts = Post.objects.filter(author=request.user).order_by('-created_at')[:5]
    recent_resources = Resource.objects.filter(uploaded_by=request.user).order_by('-created_at')[:5]
    recent_tutorials = Tutorial.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    
    return Response({
        'success': True,
        'dashboard': {
            'user_analytics': user_stats,
            'executive_analytics': {
                'posts': executive_posts,
                'resources': executive_resources,
                'tutorials': executive_tutorials,
            },
            'breakdowns': {
                'students_by_department': list(students_by_department),
                'students_by_year': list(students_by_year),
            },
            'recent_activities': {
                'posts': [
                    {
                        'id': post.id,
                        'title': post.title,
                        'created_at': post.created_at,
                        'likes': post.likes.count(),
                        'comments': post.comments.count()
                    } for post in recent_posts
                ],
                'resources': [
                    {
                        'id': resource.id,
                        'title': resource.title,
                        'created_at': resource.created_at,
                        'downloads': resource.download_count
                    } for resource in recent_resources
                ],
                'tutorials': [
                    {
                        'id': tutorial.id,
                        'title': tutorial.title,
                        'created_at': tutorial.created_at,
                        'registrations': tutorial.registrations.count()
                    } for tutorial in recent_tutorials
                ]
            },
            'executive_info': {
                'name': f"{request.user.first_name} {request.user.last_name}",
                'role': request.user.role,
                'executive_title': request.user.executive_title,
                'department': request.user.department
            }
        }
    })

class ExecutivePostListCreate(generics.ListCreateAPIView):
    """Executives can create and view their posts"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_public', 'tags']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostSerializer
    
    def get_queryset(self):
        # Executives can only see their own posts and public posts
        if self.request.user.role in ['Executive', 'Admin']:
            return Post.objects.filter(
                Q(author=self.request.user) | Q(is_public=True)
            ).select_related('author').prefetch_related('likes', 'comments').order_by('-created_at')
        return Post.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role in ['Executive', 'Admin']:
            serializer.save(author=self.request.user)
        else:
            raise permissions.PermissionDenied("Only executives and admins can create posts")

class ExecutivePostDetail(generics.RetrieveUpdateDestroyAPIView):
    """Executives can manage their own posts"""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role in ['Executive', 'Admin']:
            return Post.objects.filter(author=self.request.user)
        return Post.objects.none()

class ExecutiveResourceListCreate(generics.ListCreateAPIView):
    """Executives can upload and manage resources"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'file_type', 'is_public']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ResourceCreateSerializer
        return ResourceSerializer
    
    def get_queryset(self):
        if self.request.user.role in ['Executive', 'Admin']:
            return Resource.objects.filter(
                Q(uploaded_by=self.request.user) | Q(is_public=True)
            ).select_related('uploaded_by').order_by('-created_at')
        return Resource.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role in ['Executive', 'Admin']:
            serializer.save(uploaded_by=self.request.user)
        else:
            raise permissions.PermissionDenied("Only executives and admins can upload resources")

class ExecutiveResourceDetail(generics.RetrieveUpdateDestroyAPIView):
    """Executives can manage their own resources"""
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role in ['Executive', 'Admin']:
            return Resource.objects.filter(uploaded_by=self.request.user)
        return Resource.objects.none()

class ExecutiveTutorialListCreate(generics.ListCreateAPIView):
    """Executives can create and manage tutorials"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department', 'is_active']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TutorialCreateSerializer
        return TutorialSerializer
    
    def get_queryset(self):
        if self.request.user.role in ['Executive', 'Admin']:
            return Tutorial.objects.filter(created_by=self.request.user).select_related('created_by')
        return Tutorial.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role in ['Executive', 'Admin']:
            serializer.save(created_by=self.request.user)
        else:
            raise permissions.PermissionDenied("Only executives and admins can create tutorials")

class ExecutiveTutorialDetail(generics.RetrieveUpdateDestroyAPIView):
    """Executives can manage their own tutorials"""
    serializer_class = TutorialSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role in ['Executive', 'Admin']:
            return Tutorial.objects.filter(created_by=self.request.user)
        return Tutorial.objects.none()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def executive_tutorial_registrations(request, tutorial_id):
    """Executives can see registrations for their tutorials"""
    if request.user.role not in ['Executive', 'Admin']:
        return Response({
            'success': False,
            'message': 'Access denied. Executive privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        tutorial = Tutorial.objects.get(id=tutorial_id, created_by=request.user)
        registrations = TutorialRegistration.objects.filter(
            tutorial=tutorial
        ).select_related('student')
        
        registration_data = []
        for registration in registrations:
            registration_data.append({
                'id': registration.id,
                'student_name': f"{registration.student.first_name} {registration.student.last_name}",
                'student_email': registration.student.email,
                'student_department': registration.student.department,
                'student_year': registration.student.year_of_study,
                'registration_date': registration.registration_date,
                'status': registration.status
            })
        
        return Response({
            'success': True,
            'tutorial': {
                'id': tutorial.id,
                'title': tutorial.title,
                'max_students': tutorial.max_students,
                'current_registrations': tutorial.current_registrations
            },
            'registrations': registration_data
        })
    
    except Tutorial.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Tutorial not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
