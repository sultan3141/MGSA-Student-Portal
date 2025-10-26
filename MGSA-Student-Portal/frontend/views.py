from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from tutorials.models import Tutorial, TutorialRegistration
from resources.models import Resource
from posts.models import Post, Comment, Like
from analytics.models import Feedback
from accounts.models import User
import json
from django.utils import timezone
from django.db.models import Count, Q

# ---------------------------
# Basic & Auth Views
# ---------------------------
def index(request):
    return render(request, 'index.html')

def login_view(request):
    return render(request, 'login.html')


@login_required
def student_dashboard(request):
    """Main student dashboard with all functionality"""
    
    # Handle POST requests for various actions
    if request.method == 'POST':
        return handle_dashboard_actions(request)
    
    # GET request - load all dashboard data
    user = request.user
    
    # Tutorials data
    tutorials = Tutorial.objects.filter(
        is_active=True, 
        start_date__gte=timezone.now()
    ).order_by('start_date')
    
    user_registrations = TutorialRegistration.objects.filter(
        user=user
    ).select_related('tutorial')
    
    user_registration_ids = user_registrations.values_list('tutorial_id', flat=True)
    
    # Enhance tutorials with additional info
    for tutorial in tutorials:
        tutorial.is_registered = tutorial.id in user_registration_ids
        tutorial.current_registrations_count = TutorialRegistration.objects.filter(
            tutorial=tutorial, 
            status='registered'
        ).count()
        tutorial.is_full = tutorial.max_registrations and \
                          tutorial.current_registrations_count >= tutorial.max_registrations
    
    # Resources data
    resources = Resource.objects.filter(is_active=True).order_by('-created_at')[:10]
    
    # Posts data with engagement info
    posts = Post.objects.filter(is_published=True).order_by('-created_at')[:10]
    
    for post in posts:
        post.comments_count = Comment.objects.filter(post=post).count()
        post.likes_count = Like.objects.filter(post=post).count()
        post.user_has_liked = Like.objects.filter(post=post, user=user).exists()
    
    # User feedback
    user_feedback = Feedback.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Stats for dashboard
    context = {
        'user': user,
        'tutorials_count': user_registrations.count(),
        'resources_count': Resource.objects.count(),
        'new_posts_count': Post.objects.filter(is_published=True).count(),
        'events_count': Post.objects.filter(post_type='event', is_published=True).count(),
        'available_tutorials': tutorials,
        'user_registrations': user_registrations,
        'user_registration_ids': list(user_registration_ids),
        'resources': resources,
        'recent_posts': posts,
        'user_feedback': user_feedback,
        'active_section': request.GET.get('section', 'overview'),
    }
    
    return render(request, 'student-dashboard.html', context)

def handle_dashboard_actions(request):
    """Handle all POST actions from dashboard"""
    action = request.POST.get('action')
    
    if action == 'update_profile':
        return update_profile(request)
    elif action == 'register_tutorial':
        return register_tutorial(request)
    elif action == 'cancel_tutorial':
        return cancel_tutorial_registration(request)
    elif action == 'submit_feedback':
        return submit_feedback(request)
    elif action == 'like_post':
        return toggle_like(request)
    elif action == 'add_comment':
        return add_comment(request)
    
    messages.error(request, 'Invalid action')
    return redirect('student-dashboard')

def update_profile(request):
    """Update user profile"""
    user = request.user
    user.first_name = request.POST.get('first_name', user.first_name)
    user.last_name = request.POST.get('last_name', user.last_name)
    user.phone = request.POST.get('phone', user.phone)
    user.department = request.POST.get('department', user.department)
    user.year_of_study = request.POST.get('year_of_study', user.year_of_study)
    user.bio = request.POST.get('bio', user.bio)
    
    try:
        user.save()
        messages.success(request, 'Profile updated successfully!')
    except Exception as e:
        messages.error(request, f'Error updating profile: {str(e)}')
    
    return redirect('student-dashboard') + '?section=profile'

def register_tutorial(request):
    """Register student for tutorial"""
    tutorial_id = request.POST.get('tutorial_id')
    tutorial = get_object_or_404(Tutorial, id=tutorial_id, is_active=True)
    
    # Check if already registered
    if TutorialRegistration.objects.filter(user=request.user, tutorial=tutorial).exists():
        messages.warning(request, f'You are already registered for {tutorial.title}')
        return redirect('student-dashboard') + '?section=tutorials'
    
    # Check capacity
    current_registrations = TutorialRegistration.objects.filter(
        tutorial=tutorial, 
        status='registered'
    ).count()
    
    if tutorial.max_registrations and current_registrations >= tutorial.max_registrations:
        messages.error(request, f'Sorry, {tutorial.title} is already full')
        return redirect('student-dashboard') + '?section=tutorials'
    
    # Create registration
    TutorialRegistration.objects.create(
        user=request.user,
        tutorial=tutorial,
        status='registered'
    )
    
    messages.success(request, f'Successfully registered for {tutorial.title}!')
    return redirect('student-dashboard') + '?section=tutorials'

def cancel_tutorial_registration(request):
    """Cancel tutorial registration"""
    registration_id = request.POST.get('registration_id')
    registration = get_object_or_404(
        TutorialRegistration, 
        id=registration_id, 
        user=request.user
    )
    
    tutorial_title = registration.tutorial.title
    registration.delete()
    
    messages.success(request, f'Registration for {tutorial_title} cancelled successfully')
    return redirect('student-dashboard') + '?section=tutorials'

def toggle_like(request):
    """Toggle like on post"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        
        like, created = Like.objects.get_or_create(
            post=post,
            user=request.user
        )
        
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        
        likes_count = Like.objects.filter(post=post).count()
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': likes_count
        })
    
    messages.error(request, 'Invalid request')
    return redirect('student-dashboard')

def add_comment(request):
    """Add comment to post"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post_id = request.POST.get('post_id')
        content = request.POST.get('content', '').strip()
        
        if not content:
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty'})
        
        post = get_object_or_404(Post, id=post_id)
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            content=content
        )
        
        comments_count = Comment.objects.filter(post=post).count()
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'author_name': comment.user.get_full_name() or comment.user.email,
                'created_at': comment.created_at.isoformat(),
                'can_delete': True
            },
            'comments_count': comments_count
        })
    
    messages.error(request, 'Invalid request')
    return redirect('student-dashboard')

def submit_feedback(request):
    """Submit feedback"""
    feedback_type = request.POST.get('type', 'general')
    subject = request.POST.get('subject', '').strip()
    message = request.POST.get('message', '').strip()
    anonymous = request.POST.get('anonymous') == 'on'
    
    if not subject or not message:
        messages.error(request, 'Please fill in all required fields')
        return redirect('student-dashboard') + '?section=feedback'
    
    Feedback.objects.create(
        user=None if anonymous else request.user,
        type=feedback_type,
        subject=subject,
        message=message,
        is_anonymous=anonymous
    )
    
    messages.success(request, 'Thank you for your feedback! We appreciate your input.')
    return redirect('student-dashboard') + '?section=feedback'

# API Views for AJAX functionality
@login_required
def api_post_comments(request, post_id):
    """Get comments for a post"""
    if request.method == 'GET':
        post = get_object_or_404(Post, id=post_id)
        comments = Comment.objects.filter(post=post).select_related('user').order_by('-created_at')
        
        comments_data = []
        for comment in comments:
            comments_data.append({
                'id': comment.id,
                'content': comment.content,
                'author_name': comment.user.get_full_name() or comment.user.email,
                'created_at': comment.created_at.isoformat(),
                'can_delete': comment.user == request.user
            })
        
        return JsonResponse(comments_data, safe=False)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def api_like_post(request, post_id):
    """Like/unlike a post"""
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        
        like, created = Like.objects.get_or_create(
            post=post,
            user=request.user
        )
        
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        
        likes_count = Like.objects.filter(post=post).count()
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': likes_count
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
# ---------------------------
# Other Dashboard Views
# ---------------------------
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('student-dashboard')
    return render(request, 'admin-dashboard.html')

@login_required
def executive_dashboard(request):
    if not hasattr(request.user, 'executive_profile') and not request.user.is_superuser:
        messages.error(request, 'Access denied. Executive privileges required.')
        return redirect('student-dashboard')
    return render(request, 'executive-dashboard.html')
