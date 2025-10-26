from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
import json
from datetime import datetime
from analytics.models import Feedback
from accounts.models import User
from posts.models import Post
from resources.models import Resource
from tutorials.models import Tutorial, TutorialRegistration
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from tutorials.models import Tutorial, TutorialRegistration
from resources.models import Resource
from posts.models import Post, Comment, Like
from analytics.models import Feedback
from accounts.models import User
from django.utils import timezone

User = get_user_model()

def index(request):
    return render(request, 'index.html')
 
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect

def login_view(request):
    """
    Handle user login with automatic redirect to dashboard
    """
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            
            # Check if there's a next parameter for redirect
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            # Redirect based on user role
            if user.is_staff or user.role == 'Admin':
                return redirect('admin_dashboard')
            elif user.role == 'Executive':
                return redirect('executive_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
    
    # Get next URL for redirect after login
    next_url = request.GET.get('next', '')
    
    return render(request, 'login.html', {'next': next_url})

def login_submit(request):
    """Handle login form submission"""
    if request.method == 'POST':
        # For custom user model, use email as username
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '')
        
        print(f"Login attempt: {email}")  # Debug
        
        # Authenticate using email
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            user_role = getattr(user, 'role', 'Student')
            print(f"Login successful: {user.email}, Role: {user_role}")  # Debug
            
            # Redirect based on user role
            if next_url:
                return redirect(next_url)
            elif user.is_superuser:
                return redirect('admin-dashboard')
            elif user_role == 'Executive':
                return redirect('executive-dashboard')
            else:
                return redirect('student-dashboard')
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login-page')
    
    return redirect('login-page')

def register_page(request):
    """Handle user registration for custom User model"""
    if request.user.is_authenticated:
        return redirect('student-dashboard')
        
    if request.method == 'POST':
        try:
            # Get form data
            email = request.POST.get('email')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            gender = request.POST.get('gender', '')
            year_of_study = request.POST.get('year_of_study', '')
            zone = request.POST.get('zone', '')
            woreda = request.POST.get('woreda', '')
            college = request.POST.get('college', '')
            department = request.POST.get('department', '')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            print(f"Registration attempt - Email: {email}")  # Debug
            print(f"Zone: {zone}, Woreda: {woreda}")  # Debug
            print(f"College: {college}, Department: {department}")  # Debug
            
            # Validation
            if not all([email, password1, password2, first_name, last_name]):
                messages.error(request, 'Email, password, first name and last name are required')
                return render(request, 'register.html', get_registration_context())
            
            if password1 != password2:
                messages.error(request, 'Passwords do not match')
                return render(request, 'register.html', get_registration_context())
            
            if len(password1) < 6:
                messages.error(request, 'Password must be at least 6 characters long')
                return render(request, 'register.html', get_registration_context())
            
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return render(request, 'register.html', get_registration_context())
            
            # Create user with custom User model
            user_data = {
                'email': email,
                'password': password1,
                'first_name': first_name,
                'last_name': last_name,
                'role': 'Student',  # Default role
                'gender': gender if gender else '',
                'year_of_study': year_of_study if year_of_study else 'Fresh',
                'zone': zone if zone else '',
                'woreda': woreda if woreda else '',
                'college': college if college else '',
                'department': department if department else '',
                'is_active': True,
                'is_staff': False,
                'is_superuser': False,
            }
            
            user = User.objects.create_user(**user_data)
            
            print(f"User created successfully: {user.email}")  # Debug
            print(f"User zone: {user.zone}, woreda: {user.woreda}")  # Debug
            print(f"User college: {user.college}, department: {user.department}")  # Debug
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to MGSA Portal.')
            return redirect('student-dashboard')
            
        except Exception as e:
            print(f"Registration error: {str(e)}")  # Debug
            import traceback
            traceback.print_exc()  # Print full traceback for debugging
            messages.error(request, f'An error occurred during registration: {str(e)}')
            return render(request, 'register.html', get_registration_context())
    
    # GET request - show registration form
    return render(request, 'register.html', get_registration_context())

def get_registration_context():
    """Helper function to get registration form context"""
    collegeDepartments = {
        'College of Business & Economics': [
            'Accounting and Finance',
            'Cooperatives (Cooperative Business Management & Cooperative Accounting and Auditing)',
            'Economics',
            'Management',
            'Public Administration and Development Management'
        ],
        'College of Computing & Informatics': [
            'Computer Sciences',
            'Information Sciences',
            'Information Systems',
            'Information Technology',
            'Software Engineering',
            'Statistics'
        ],
        'College of Agriculture & Environmental Sciences': [
            'Agribusiness & Value Chain Management',
            'Agricultural Economics',
            'Animal Science',
            'Range Ecology & Biodiversity',
            'Natural Resource Management',
            'Environmental Sciences',
            'Rural Development & Agricultural Extension (Regular)',
            'Rural Development & Agricultural Extension (Mid-career)',
            'Horticultural Crop Production & Processing',
            'Sugarcane Agronomy',
            'Plant Science'
        ],
        'College of Health & Medical Sciences': [
            'Environmental Health Science',
            'Medical Laboratory Sciences',
            'Medicine',
            'Pharmacy (Clinical)',
            'Public Health',
            'Nursing (Neonatal Nursing, Emergency & Critical Care Nursing)',
            'Midwifery (Advance Standing Midwifery)',
            'Midwifery (Regular)',
            'Psychiatric Nursing',
            'Surgical Nursing',
            'Pediatric Nursing'
        ],
        'College of Social Sciences & Humanities': [
            'English Language and Literature',
            'French Language and Literature',
            'Journalism and Mass Communication',
            'Geo-Information Sciences',
            'Geography and Environmental Studies',
            'Urban Planning',
            'Gender and Development',
            'History & Heritage Management',
            'Sociology',
            'Afaan Oromo and Literature',
            'Tourism Development & Hotel Management'
        ],
        'College of Law': [
            'Law (LLB)'
        ],
        'College of Veterinary Medicine': [
            'Veterinary Medicine (DVM)',
            'Veterinary Laboratory Technology'
        ],
        'College of Natural & Computational Sciences': [
            'Biology',
            'Molecular Biology & Biotechnology (New)',
            'Chemistry',
            'Mathematics',
            'Physics'
        ],
        'Sport Science Academy': [
            'Sport Sciences'
        ],
        'Haramaya Institute of Technology': [
            'Agricultural Engineering',
            'Water Resources & Irrigation Engineering',
            'Water Supply & Environmental Engineering',
            'Hydraulics and Water Resource Engineering',
            'Food Science and Post-Harvest Technology',
            'Food Technology and Process Engineering',
            'Chemical Engineering',
            'Civil Engineering',
            'Electrical and Computer Engineering',
            'Mechanical Engineering'
        ],
        'College of Education & Behavioral Science': [
            'Adult Education & Community Development',
            'Educational Planning & Management',
            'Psychology',
            'Special Needs & Inclusive Education'
        ],
        'College of Agro Industry & Land Resources': [
            'Land Administration',
            'Dairy & Meat Technology',
            'Forest Resource Management',
            'Soil Resources & Watershed Management'
        ]
    }
    

def index(request):
    """Home page"""
    return render(request, 'index.html')


def login_page(request):
    """
    Handle user login with automatic redirect to dashboard
    """
    # If user is already authenticated, redirect to PROPER dashboard
    if request.user.is_authenticated:
        # Redirect based on user role for already authenticated users
        if request.user.is_staff or getattr(request.user, 'role', '') == 'Admin':
            return redirect('admin-dashboard')
        elif getattr(request.user, 'role', '') == 'Executive':
            return redirect('executive-dashboard')
        else:
            return redirect('student-dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            
            # Check if there's a next parameter for redirect
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            # Redirect based on user role
            if user.is_staff or user.role == 'Admin':
                return redirect('admin-dashboard')
            elif user.role == 'Executive':
                return redirect('executive-dashboard')
            else:
                return redirect('student-dashboard')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
    
    # Get next URL for redirect after login
    next_url = request.GET.get('next', '')
    
    return render(request, 'login.html', {'next': next_url})

@csrf_exempt
def login_submit(request):
    """Handle login form submission"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            
            if user.role == 'student':
                return redirect('student-dashboard')
            elif user.role == 'executive':
                return redirect('executive-dashboard')
            elif user.is_staff:
                return redirect('admin-dashboard')
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login-page')
    
    return redirect('login-page')

def register_page(request):
    """Registration page"""
    if request.user.is_authenticated:
        return redirect('student-dashboard')
    
    # Woredas by zone
    west_hararghe_woredas = [
        'Mieso', 'Doba', 'Tulo', 'Mesela', 'Chiro', 'Anchar', 'Guba Koricha', 
        'Habro', 'Daro Lebu', 'Boke', 'Kuni', 'Gemches', 'Chiro Zuria', 'Bedesa'
    ]
    
    east_hararghe_woredas = [
        'Kombolcha', 'Jarso', 'Gursum', 'Babile', 'Fedis', 'Haro Maya', 
        'Kurfa Chele', 'Kersa', 'Meta', 'Goro Gutu', 'Deder', 'Melka Belo', 
        'Bedeno', 'Midga Tola', 'Chinaksan', 'Girawa', 'Gola Oda', 'Meyu'
    ]
    
    collegeDepartments = {
        'College of Natural and Computational Sciences': [
            'Biology', 'Chemistry', 'Physics', 'Mathematics', 'Statistics', 
            'Sport Science', 'Computer Science', 'Geology'
        ],
        'College of Social Sciences and Humanities': [
            'Civics', 'Economics', 'English', 'Geography', 'History', 
            'Oromo Folklore', 'Psychology', 'Amharic'
        ],
        'College of Business and Economics': [
            'Accounting', 'Business Management', 'Economics', 'Logistics', 
            'Marketing', 'Tourism Management'
        ],
        'College of Education and Behavioral Sciences': [
            'Biology', 'Chemistry', 'Physics', 'Mathematics', 'English', 
            'Amharic', 'Oromo Folklore', 'Civics', 'Geography', 'History', 
            'Psychology', 'Special Needs', 'Early Childhood Care'
        ]
    }
    
    context = {
        'zones': ['West Hararghe', 'East Hararghe'],
        'colleges': list(collegeDepartments.keys()),
        'west_hararghe_woredas': west_hararghe_woredas,
        'east_hararghe_woredas': east_hararghe_woredas,
        'college_departments': collegeDepartments,
    }
    return render(request, 'register.html', context)

@csrf_exempt
def register_submit(request):
    """API registration endpoint for custom User model"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')
            password = data.get('password')
            password_confirm = data.get('password_confirm')
            
            # Validation
            if not all([email, password, password_confirm]):
                return JsonResponse({
                    'success': False,
                    'message': 'Email and password fields are required'
                }, status=400)
            
            if password != password_confirm:
                return JsonResponse({
                    'success': False,
                    'message': 'Passwords do not match'
                }, status=400)
            
            if len(password) < 6:
                return JsonResponse({
                    'success': False,
                    'message': 'Password must be at least 6 characters long'
                }, status=400)
            
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Email already exists'
                }, status=400)
            
            # Create user with custom User model
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='student'  # Default role
            )
            
            # Log the user in
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'message': 'Registration successful!',
                'redirect_url': '/student-dashboard/'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'An error occurred during registration: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=400)

def logout_view(request):
    """Handle logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from tutorials.models import Tutorial, TutorialRegistration
from posts.models import Post, Comment, Like
from resources.models import Resource
from analytics.models import Feedback
from django.db.models import Count

@login_required
def student_dashboard(request):
    # Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            return update_profile(request)
        elif action == 'register_tutorial':
            return register_tutorial(request)
        elif action == 'cancel_tutorial':
            return cancel_tutorial(request)
        elif action == 'like_post':
            return toggle_like(request)
        elif action == 'add_comment':
            return add_comment(request)
        elif action == 'submit_feedback':
            return submit_feedback(request)
        elif action == 'download_resource':
            return download_resource(request)
    
    # GET request - load all data
    user = request.user
    
    try:
        # Get tutorials - using student field instead of user
        tutorials = Tutorial.objects.filter(is_active=True)
        
        # FIXED: Using student instead of user
        user_registrations = TutorialRegistration.objects.filter(student=user).select_related('tutorial')
        
        # Get registered tutorial IDs for quick lookup
        registered_tutorial_ids = user_registrations.values_list('tutorial_id', flat=True)
        
        # Enhance tutorials with registration info more efficiently
        for tutorial in tutorials:
            tutorial.is_registered = tutorial.id in registered_tutorial_ids
            tutorial.available_spots = tutorial.max_students - tutorial.current_registrations
            tutorial.is_full = tutorial.current_registrations >= tutorial.max_students
        
        # Get resources
        resources = Resource.objects.all()[:10]
        
        # Get posts - using safe approach without prefetch_related
        posts = Post.objects.all().select_related('author').order_by('-created_at')[:10]
        
        # Get counts and related data efficiently
        post_ids = [post.id for post in posts]
        
        # Get comment counts
        comment_counts = Comment.objects.filter(post_id__in=post_ids).values('post_id').annotate(count=Count('id'))
        comment_count_dict = {item['post_id']: item['count'] for item in comment_counts}
        
        # Get like counts
        like_counts = Like.objects.filter(post_id__in=post_ids).values('post_id').annotate(count=Count('id'))
        like_count_dict = {item['post_id']: item['count'] for item in like_counts}
        
        # Get user likes - FIXED: Make sure this uses the correct field name
        user_likes = Like.objects.filter(post_id__in=post_ids, user=user).values_list('post_id', flat=True)
        user_likes_set = set(user_likes)
        
        # Attach data to posts
        for post in posts:
            post.comments_count = comment_count_dict.get(post.id, 0)
            post.likes_count = like_count_dict.get(post.id, 0)
            post.user_has_liked = post.id in user_likes_set
            # Get recent comments for this post
            post.recent_comments = Comment.objects.filter(post=post).select_related('user').order_by('-created_at')[:3]
        
        # Get user feedback
        user_feedback = Feedback.objects.filter(user=user).order_by('-created_at')[:5]
        
        # Stats - FIXED: Using student field
        completed_tutorials = user_registrations.filter(status='completed').count()
        
        context = {
            'user': user,
            'tutorials_count': user_registrations.count(),
            'resources_count': Resource.objects.count(),
            'posts_count': Post.objects.count(),
            'completed_tutorials': completed_tutorials,
            'available_tutorials': tutorials,
            'user_registrations': user_registrations,
            'resources': resources,
            'recent_posts': posts,
            'user_feedback': user_feedback,
            'active_section': request.GET.get('section', 'overview')
        }
        
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        context = {
            'user': user,
            'tutorials_count': 0,
            'resources_count': 0,
            'posts_count': 0,
            'completed_tutorials': 0,
            'available_tutorials': [],
            'user_registrations': [],
            'resources': [],
            'recent_posts': [],
            'user_feedback': [],
            'active_section': 'overview'
        }
    
    return render(request, 'student-dashboard.html', context)

def update_profile(request):
    user = request.user  # This is fine - different function
    user.first_name = request.POST.get('first_name', '')
    user.last_name = request.POST.get('last_name', '')
    user.phone = request.POST.get('phone', '')
    user.bio = request.POST.get('bio', '')
    
    try:
        user.save()
        messages.success(request, 'Profile updated successfully!')
    except Exception as e:
        messages.error(request, f'Error updating profile: {str(e)}')
    
    return redirect('student_dashboard') + '?section=profile'


def register_tutorial(request):
    tutorial_id = request.POST.get('tutorial_id')
    tutorial = get_object_or_404(Tutorial, id=tutorial_id)
    
    # Check if student is already registered
    if TutorialRegistration.objects.filter(student=request.user, tutorial=tutorial).exists():
        messages.warning(request, 'You are already registered for this tutorial')
        return redirect('student_dashboard') + '?section=tutorials'
    
    # Check if tutorial is full
    if tutorial.current_registrations >= tutorial.max_students:
        messages.error(request, 'This tutorial is already full')
        return redirect('student_dashboard') + '?section=tutorials'
    
    # Create registration
    TutorialRegistration.objects.create(
        student=request.user,
        tutorial=tutorial,
        status='registered'
    )
    
    # Update tutorial registration count
    tutorial.current_registrations += 1
    tutorial.save()
    
    messages.success(request, 'Successfully registered for tutorial!')
    return redirect('student_dashboard') + '?section=tutorials'


def cancel_tutorial(request):
    tutorial_id = request.POST.get('tutorial_id')
    tutorial = get_object_or_404(Tutorial, id=tutorial_id)
    
    registration = TutorialRegistration.objects.filter(
        student=request.user,
        tutorial=tutorial
    ).first()
    
    if registration:
        registration.delete()
        # Ensure current_registrations doesn't go below 0
        if tutorial.current_registrations > 0:
            tutorial.current_registrations -= 1
            tutorial.save()
        messages.success(request, 'Registration cancelled successfully')
    else:
        messages.error(request, 'Registration not found')
    
    return redirect('student_dashboard') + '?section=tutorials'


def toggle_like(request):
    post_id = request.POST.get('post_id')
    post = get_object_or_404(Post, id=post_id)
    
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    
    if not created:
        like.delete()
        messages.info(request, 'Post unliked')
    else:
        messages.success(request, 'Post liked!')
    
    return redirect('student_dashboard') + '?section=posts'


def add_comment(request):
    post_id = request.POST.get('post_id')
    content = request.POST.get('content', '').strip()
    
    if not content:
        messages.error(request, 'Comment cannot be empty')
        return redirect('student_dashboard') + '?section=posts'
    
    post = get_object_or_404(Post, id=post_id)
    Comment.objects.create(post=post, user=request.user, content=content)
    
    messages.success(request, 'Comment added successfully!')
    return redirect('student_dashboard') + '?section=posts'


def submit_feedback(request):
    feedback_type = request.POST.get('type', 'general')
    subject = request.POST.get('subject', '').strip()
    content = request.POST.get('message', '').strip()
    anonymous = request.POST.get('anonymous') == 'on'
    
    if not content:
        messages.error(request, 'Feedback message cannot be empty')
        return redirect('student_dashboard') + '?section=feedback'
    
    Feedback.objects.create(
        user=request.user if not anonymous else None,
        content=content,
        feedback_type=feedback_type,
        subject=subject
    )
    
    messages.success(request, 'Thank you for your feedback!')
    return redirect('student_dashboard') + '?section=feedback'


def download_resource(request):
    resource_id = request.POST.get('resource_id')
    resource = get_object_or_404(Resource, id=resource_id)
    
    resource.download_count += 1
    resource.save()
    
    if resource.file:
        return redirect(resource.file.url)
    elif resource.file_url:
        return redirect(resource.file_url)
    else:
        messages.error(request, 'No file available for download')
        return redirect('student_dashboard') + '?section=resources'
    
@login_required
def admin_dashboard(request):
    """Admin dashboard view"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('login-page')
    
    try:
        # Admin statistics
        total_users = User.objects.count()
        total_posts = Post.objects.count()
        total_resources = Resource.objects.count()
        total_tutorials = Tutorial.objects.count()
        total_registrations = TutorialRegistration.objects.count()
        
        context = {
            'total_users': total_users,
            'total_posts': total_posts,
            'total_resources': total_resources,
            'total_tutorials': total_tutorials,
            'total_registrations': total_registrations,
        }
        
        return render(request, 'admin-dashboard.html', context)
        
    except Exception as e:
        print(f"Error loading admin dashboard: {str(e)}")
        messages.error(request, f'Error loading admin dashboard: {str(e)}')
        return render(request, 'admin-dashboard.html')

@login_required
def executive_dashboard(request):
    """Executive dashboard view"""
    # Check if user has executive privileges
    user_role = getattr(request.user, 'role', '').lower()
    if user_role != 'executive' and not request.user.is_staff:
        messages.error(request, 'Access denied. Executive privileges required.')
        return redirect('student-dashboard')
    
    # Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_post':
            return create_post(request)
        elif action == 'create_resource':
            return create_resource(request)
        elif action == 'create_tutorial':
            return create_tutorial(request)
        elif action == 'delete_post':
            return delete_post(request)
        elif action == 'delete_resource':
            return delete_resource(request)
        elif action == 'delete_tutorial':
            return delete_tutorial(request)
    
    # GET request - load all executive data
    user = request.user
    
    try:
        # Get executive's content
        my_posts = Post.objects.filter(author=user).order_by('-created_at')
        my_resources = Resource.objects.filter(uploaded_by=user).order_by('-created_at')
        my_tutorials = Tutorial.objects.filter(created_by=user).order_by('-created_at')
        
        # Get tutorial registrations for executive's tutorials
        tutorial_registrations = TutorialRegistration.objects.filter(
            tutorial__created_by=user
        ).select_related('student', 'tutorial').order_by('-registration_date')
        
        # Get counts and stats
        my_posts_count = my_posts.count()
        my_resources_count = my_resources.count()
        my_tutorials_count = my_tutorials.count()
        total_registrations = tutorial_registrations.count()
        
        context = {
            'user': user,
            'my_posts': my_posts,
            'my_resources': my_resources,
            'my_tutorials': my_tutorials,
            'tutorial_registrations': tutorial_registrations,
            
            # Stats
            'my_posts_count': my_posts_count,
            'my_resources_count': my_resources_count,
            'my_tutorials_count': my_tutorials_count,
            'total_registrations': total_registrations,
        }
        
    except Exception as e:
        print(f"Error loading executive dashboard: {str(e)}")
        messages.error(request, f'Error loading dashboard: {str(e)}')
        context = {
            'user': user,
            'my_posts': [],
            'my_resources': [],
            'my_tutorials': [],
            'tutorial_registrations': [],
            'my_posts_count': 0,
            'my_resources_count': 0,
            'my_tutorials_count': 0,
            'total_registrations': 0,
        }
    
    return render(request, 'executive-dashboard.html', context)

# Executive Action Handlers
def create_post(request):
    """Handle post creation"""
    try:
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        
        if not title or not content:
            messages.error(request, 'Title and content are required')
            return redirect('executive-dashboard')
        
        Post.objects.create(
            title=title,
            content=content,
            author=request.user
        )
        
        messages.success(request, 'Post created successfully!')
        
    except Exception as e:
        messages.error(request, f'Error creating post: {str(e)}')
    
    return redirect('executive-dashboard')

def create_resource(request):
    """Handle resource creation for updated Resource model with file field"""
    try:
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        resource_type = request.POST.get('resource_type', 'file')
        category = request.POST.get('category', '').strip()
        
        if not title:
            messages.error(request, 'Title is required')
            return redirect('executive-dashboard')
        
        # Prepare base resource data
        resource_data = {
            'title': title,
            'description': description,
            'uploaded_by': request.user,
            'category': category,
            'tags': [],
            'is_public': True,
        }
        
        if resource_type == 'file' and request.FILES.get('file'):
            uploaded_file = request.FILES['file']
            
            # Set file-related data
            resource_data.update({
                'file': uploaded_file,
                'file_name': uploaded_file.name,
                'file_size': uploaded_file.size,
                'file_url': '',  # Empty for file uploads
            })
            
            # Create the resource - file_type will be auto-detected in save() method
            Resource.objects.create(**resource_data)
            messages.success(request, 'Resource file uploaded successfully!')
            
        elif resource_type == 'link' and request.POST.get('file_url'):
            file_url = request.POST.get('file_url', '').strip()
            
            if not file_url:
                messages.error(request, 'URL is required for link resources')
                return redirect('executive-dashboard')
            
            # Extract file name from URL
            import urllib.parse
            import os
            parsed_url = urllib.parse.urlparse(file_url)
            file_name = os.path.basename(parsed_url.path) or f"{title}.link"
            
            # Determine file type from URL extension
            ext = os.path.splitext(file_name)[1].lower().lstrip('.')
            file_type_map = {
                'pdf': 'pdf',
                'doc': 'doc',
                'docx': 'docx',
                'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image',
                'mp4': 'video', 'avi': 'video', 'mov': 'video', 'wmv': 'video',
            }
            file_type = file_type_map.get(ext, 'other')
            
            resource_data.update({
                'file_url': file_url,
                'file_name': file_name,
                'file_type': file_type,
                'file_size': 0,  # URLs don't have file size
                'file': None,  # No file for URL resources
            })
            
            Resource.objects.create(**resource_data)
            messages.success(request, 'Resource link added successfully!')
            
        else:
            messages.error(request, 'Either file or URL is required')
            return redirect('executive-dashboard')
        
    except Exception as e:
        messages.error(request, f'Error uploading resource: {str(e)}')
    
    return redirect('executive-dashboard')

def create_tutorial(request):
    """Handle tutorial creation for your specific Tutorial model"""
    try:
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        start_date = request.POST.get('start_date')
        tutor = request.POST.get('tutor', '').strip()
        department = request.POST.get('department', '').strip()
        max_students = request.POST.get('max_students')
        end_date = request.POST.get('end_date')
        time = request.POST.get('time', '').strip()
        
        # Required fields validation
        if not all([title, start_date, tutor, department, max_students, end_date, time]):
            messages.error(request, 'Title, start date, end date, tutor, department, time, and max students are required')
            return redirect('executive-dashboard')
        
        # Parse dates
        from datetime import datetime
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get days (convert from form data to JSON list)
        days = request.POST.getlist('days')  # For multiple select
        if not days:
            # If no days selected, try single day field
            single_day = request.POST.get('day')
            if single_day:
                days = [single_day]
            else:
                days = []
        
        # Create the tutorial with your model's actual fields
        Tutorial.objects.create(
            title=title,
            description=description,
            tutor=tutor,
            department=department,
            topics=[],  # Empty list for now, you can add topic input later
            start_date=start_date,
            end_date=end_date,
            days=days,
            time=time,
            max_students=int(max_students),
            current_registrations=0,  # Start with 0 registrations
            created_by=request.user,
            is_active=True
        )
        
        messages.success(request, 'Tutorial created successfully!')
        
    except Exception as e:
        messages.error(request, f'Error creating tutorial: {str(e)}')
    
    return redirect('executive-dashboard')

def delete_post(request):
    """Handle post deletion"""
    try:
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id, author=request.user)
        post.delete()
        messages.success(request, 'Post deleted successfully')
    except Exception as e:
        messages.error(request, f'Error deleting post: {str(e)}')
    
    return redirect('executive-dashboard')

def delete_resource(request):
    """Handle resource deletion"""
    try:
        resource_id = request.POST.get('resource_id')
        resource = get_object_or_404(Resource, id=resource_id, uploaded_by=request.user)
        resource.delete()
        messages.success(request, 'Resource deleted successfully')
    except Exception as e:
        messages.error(request, f'Error deleting resource: {str(e)}')
    
    return redirect('executive-dashboard')

def delete_tutorial(request):
    """Handle tutorial deletion"""
    try:
        tutorial_id = request.POST.get('tutorial_id')
        tutorial = get_object_or_404(Tutorial, id=tutorial_id, created_by=request.user)
        tutorial.delete()
        messages.success(request, 'Tutorial deleted successfully')
    except Exception as e:
        messages.error(request, f'Error deleting tutorial: {str(e)}')
    
    return redirect('executive-dashboard')

@login_required
@require_http_methods(["POST"])
def register_tutorial(request):
    """Handle tutorial registration"""
    try:
        tutorial_id = request.POST.get('tutorial_id')
        tutorial = Tutorial.objects.get(id=tutorial_id, is_active=True)
        
        # Check if already registered
        if TutorialRegistration.objects.filter(student=request.user, tutorial=tutorial).exists():
            messages.warning(request, 'You are already registered for this tutorial')
        else:
            # Check if tutorial has available spots
            if tutorial.max_students and tutorial.current_registrations >= tutorial.max_students:
                messages.error(request, 'This tutorial is full')
            else:
                TutorialRegistration.objects.create(
                    student=request.user,
                    tutorial=tutorial,
                    status='registered'
                )
                messages.success(request, 'Successfully registered for tutorial')
    
    except Tutorial.DoesNotExist:
        messages.error(request, 'Tutorial not found')
    except Exception as e:
        messages.error(request, f'Registration failed: {str(e)}')
    
    return redirect('student-dashboard')

@login_required
@require_http_methods(["POST"])
def cancel_tutorial_registration(request, registration_id):
    """Cancel tutorial registration"""
    try:
        registration = TutorialRegistration.objects.get(
            id=registration_id,
            user=request.user,
            status='registered'
        )
        registration.status = 'cancelled'
        registration.save()
        messages.success(request, 'Tutorial registration cancelled')
    except TutorialRegistration.DoesNotExist:
        messages.error(request, 'Registration not found')
    
    return redirect('student-dashboard')


@login_required
def contact_feedback(request):
    """Contact and feedback page - handles both GET and POST"""
    if request.method == 'POST':
        # Handle feedback submission
        try:
            feedback_type = request.POST.get('type', 'general')
            subject = request.POST.get('subject', '').strip()
            message = request.POST.get('message', '').strip()
            anonymous = request.POST.get('anonymous') == 'on'
            
            if not message:
                messages.error(request, 'Feedback message cannot be empty')
                return render(request, 'contact_feedback.html')
            
            # Create feedback with correct field names for your model
            Feedback.objects.create(
                user=request.user if not anonymous else None,
                anonymous=anonymous,  # Correct field name
                feedback_type=feedback_type,  # Correct field name
                subject=subject,
                message=message  # Correct field name
            )
            
            messages.success(request, 'Thank you for your feedback! We will review it soon.')
            return redirect('contact_feedback')
            
        except Exception as e:
            messages.error(request, f'Failed to submit feedback: {str(e)}')
            return render(request, 'contact_feedback.html')
    
    # GET request - show the contact/feedback page
    return render(request, 'contact_feedback.html')

@login_required
@require_http_methods(["POST"])
def submit_feedback(request):
    """Handle feedback submission"""
    try:
        feedback_type = request.POST.get('type')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        anonymous = request.POST.get('anonymous') == 'on'
        
        Feedback.objects.create(
            user=request.user if not anonymous else None,
            type=feedback_type,
            subject=subject,
            message=message,
            is_anonymous=anonymous
        )
        
        messages.success(request, 'Thank you for your feedback!')
    
    except Exception as e:
        messages.error(request, f'Failed to submit feedback: {str(e)}')
    
    return redirect('student-dashboard')

@login_required
@require_http_methods(["POST"])
def update_profile(request):
    """Update user profile"""
    try:
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        user.department = request.POST.get('department', user.department)
        user.year_of_study = request.POST.get('year_of_study', user.year_of_study)
        user.bio = request.POST.get('bio', user.bio)
        user.save()
        
        messages.success(request, 'Profile updated successfully')
    
    except Exception as e:
        messages.error(request, f'Failed to update profile: {str(e)}')
    
    return redirect('student-dashboard')

def force_logout(request):
    """Force logout for session management"""
    logout(request)
    return JsonResponse({'success': True})

# Executive API Views
@login_required
@require_http_methods(["POST"])
def api_create_post(request):
    """API endpoint for creating posts"""
    try:
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if not title or not content:
            return JsonResponse({
                'success': False,
                'error': 'Title and content are required'
            })
        
        post = Post.objects.create(
            title=title,
            content=content,
            author=request.user
        )
        
        return JsonResponse({
            'success': True,
            'post_id': post.id,
            'message': 'Post created successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_http_methods(["POST"])
def api_create_resource(request):
    """API endpoint for creating resources"""
    try:
        title = request.POST.get('title')
        description = request.POST.get('description')
        resource_type = request.POST.get('resource_type', 'file')
        
        if not title:
            return JsonResponse({
                'success': False,
                'error': 'Title is required'
            })
        
        resource = Resource.objects.create(
            title=title,
            description=description,
            uploaded_by=request.user
        )
        
        if resource_type == 'file' and request.FILES.get('file'):
            resource.file = request.FILES['file']
        elif resource_type == 'link' and request.POST.get('file_url'):
            resource.file_url = request.POST['file_url']
        else:
            return JsonResponse({
                'success': False,
                'error': 'Either file or URL is required'
            })
        
        resource.save()
        
        return JsonResponse({
            'success': True,
            'resource_id': resource.id,
            'message': 'Resource uploaded successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_http_methods(["POST"])
def api_create_tutorial(request):
    """API endpoint for creating tutorials"""
    try:
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        duration = request.POST.get('duration')
        max_registrations = request.POST.get('max_registrations')
        
        if not title or not start_date:
            return JsonResponse({
                'success': False,
                'error': 'Title and start date are required'
            })
        
        # Parse datetime
        try:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid date format'
            })
        
        tutorial = Tutorial.objects.create(
            title=title,
            description=description,
            start_date=start_date,
            duration=duration,
            max_registrations=max_registrations or None,
            created_by=request.user,
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'tutorial_id': tutorial.id,
            'message': 'Tutorial created successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_http_methods(["POST"])
def api_delete_post(request, post_id):
    """API endpoint for deleting posts"""
    try:
        post = Post.objects.get(id=post_id, author=request.user)
        post.delete()
        return JsonResponse({'success': True, 'message': 'Post deleted successfully'})
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Post not found'})

@login_required
@require_http_methods(["POST"])
def api_delete_resource(request, resource_id):
    """API endpoint for deleting resources"""
    try:
        resource = Resource.objects.get(id=resource_id, uploaded_by=request.user)
        resource.delete()
        return JsonResponse({'success': True, 'message': 'Resource deleted successfully'})
    except Resource.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Resource not found'})

@login_required
@require_http_methods(["POST"])
def api_delete_tutorial(request, tutorial_id):
    """API endpoint for deleting tutorials"""
    try:
        tutorial = Tutorial.objects.get(id=tutorial_id, created_by=request.user)
        tutorial.delete()
        return JsonResponse({'success': True, 'message': 'Tutorial deleted successfully'})
    except Tutorial.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tutorial not found'})

def register_page(request):
    """Registration page"""
    if request.user.is_authenticated:
        return redirect('student-dashboard')
    
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            zone = request.POST.get('zone')
            woreda = request.POST.get('woreda')
            college = request.POST.get('college')
            department = request.POST.get('department')
            gender = request.POST.get('gender')
            year_of_study = request.POST.get('year_of_study')
            
            # Validation
            if not all([email, first_name, last_name, password1, password2]):
                messages.error(request, 'All required fields must be filled')
                return render(request, 'register.html', {
                    'zones': ['West Hararghe', 'East Hararghe'],
                    'colleges': list(collegeDepartments.keys()),
                    'west_hararghe_woredas': west_hararghe_woredas,
                    'east_hararghe_woredas': east_hararghe_woredas,
                    'college_departments': collegeDepartments,
                })
            
            if password1 != password2:
                messages.error(request, 'Passwords do not match')
                return render(request, 'register.html', {
                    'zones': ['West Hararghe', 'East Hararghe'],
                    'colleges': list(collegeDepartments.keys()),
                    'west_hararghe_woredas': west_hararghe_woredas,
                    'east_hararghe_woredas': east_hararghe_woredas,
                    'college_departments': collegeDepartments,
                })
            
            if len(password1) < 6:
                messages.error(request, 'Password must be at least 6 characters long')
                return render(request, 'register.html', {
                    'zones': ['West Hararghe', 'East Hararghe'],
                    'colleges': list(collegeDepartments.keys()),
                    'west_hararghe_woredas': west_hararghe_woredas,
                    'east_hararghe_woredas': east_hararghe_woredas,
                    'college_departments': collegeDepartments,
                })
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return render(request, 'register.html', {
                    'zones': ['West Hararghe', 'East Hararghe'],
                    'colleges': list(collegeDepartments.keys()),
                    'west_hararghe_woredas': west_hararghe_woredas,
                    'east_hararghe_woredas': east_hararghe_woredas,
                    'college_departments': collegeDepartments,
                })
            
            # Create user
            user = User.objects.create_user(
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                role='student',
                zone=zone,
                woreda=woreda,
                college=college,
                department=department,
                gender=gender,
                year_of_study=year_of_study
            )
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to MGSA Portal.')
            return redirect('student-dashboard')
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'register.html', {
                'zones': ['West Hararghe', 'East Hararghe'],
                'colleges': list(collegeDepartments.keys()),
                'west_hararghe_woredas': west_hararghe_woredas,
                'east_hararghe_woredas': east_hararghe_woredas,
                'college_departments': collegeDepartments,
            })
    
    # Woredas by zone
    west_hararghe_woredas = [
        'Mieso', 'Doba', 'Tulo', 'Mesela', 'Chiro', 'Anchar', 'Guba Koricha', 
        'Habro', 'Daro Lebu', 'Boke', 'Kuni', 'Gemches', 'Chiro Zuria', 'Bedesa'
    ]
    
    east_hararghe_woredas = [
        'Kombolcha', 'Jarso', 'Gursum', 'Babile', 'Fedis', 'Haro Maya', 
        'Kurfa Chele', 'Kersa', 'Meta', 'Goro Gutu', 'Deder', 'Melka Belo', 
        'Bedeno', 'Midga Tola', 'Chinaksan', 'Girawa', 'Gola Oda', 'Meyu'
    ]
    
    collegeDepartments = {
        'College of Business & Economics': [
            'Accounting and Finance',
            'Cooperatives (Cooperative Business Management & Cooperative Accounting and Auditing)',
            'Economics',
            'Management',
            'Public Administration and Development Management'
        ],
        'College of Computing & Informatics': [
            'Computer Sciences',
            'Information Sciences',
            'Information Systems',
            'Information Technology',
            'Software Engineering',
            'Statistics'
        ],
        # ... include all your colleges from the template
    }
    
    context = {
        'zones': ['West Hararghe', 'East Hararghe'],
        'colleges': list(collegeDepartments.keys()),
        'west_hararghe_woredas': west_hararghe_woredas,
        'east_hararghe_woredas': east_hararghe_woredas,
        'college_departments': collegeDepartments,
    }
    return render(request, 'register.html', context)
