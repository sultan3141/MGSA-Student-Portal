from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from knox.models import AuthToken
from .models import User, Zone, Woreda, College, Department
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, ZoneSerializer,
    WoredaSerializer, CollegeSerializer, DepartmentSerializer
)

# ============================================================================
# TEMPLATE VIEWS (for rendering HTML pages)
# ============================================================================

def index(request):
    """Home page"""
    if request.user.is_authenticated:
        return redirect('student-dashboard')
    return render(request, 'index.html')

def login_page(request):
    """Render login page"""
    if request.user.is_authenticated:
        return redirect('student-dashboard')
    
    # Get geographical and academic data for registration form
    try:
        zones = Zone.objects.all()
        woredas = Woreda.objects.all()
        colleges = College.objects.all()
        departments = Department.objects.all()
    except:
        zones = []
        woredas = []
        colleges = []
        departments = []
    
    context = {
        'zones': zones,
        'woredas': woredas,
        'colleges': colleges,
        'departments': departments,
    }
    return render(request, 'login.html', context)

def login_submit(request):
    """Handle login form submission"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"Login attempt: {username}")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            print(f"Login successful: {user.username}")
            
            # Redirect based on user role
            if user.is_superuser:
                return redirect('admin-dashboard')
            elif hasattr(user, 'role') and user.role == 'Executive':
                return redirect('executive-dashboard')
            else:
                return redirect('student-dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login-page')
    
    return redirect('login-page')

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

'''def register_page(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('student-dashboard')
        
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            print(f"Registration attempt - Username: {username}, Email: {email}")  # Debug
            
            # Validation
            if not all([username, email, password1, password2]):
                messages.error(request, 'All fields are required')
                return render(request, 'register.html')
            
            if password1 != password2:
                messages.error(request, 'Passwords do not match')
                return render(request, 'register.html')
            
            if len(password1) < 6:
                messages.error(request, 'Password must be at least 6 characters long')
                return render(request, 'register.html')
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return render(request, 'register.html')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return render(request, 'register.html')
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            
            print(f"User created successfully: {user.username}")  # Debug
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to MGSA Portal.')
            return redirect('student-dashboard')
            
        except Exception as e:
            print(f"Registration error: {str(e)}")  # Debug
            messages.error(request, f'An error occurred during registration: {str(e)}')
            return render(request, 'register.html')
    
    # GET request - show registration form
    return render(request, 'register.html')
'''
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
    
    context = {
        'zones': ['West Hararghe', 'East Hararghe'],
        'colleges': list(collegeDepartments.keys()),
        'west_hararghe_woredas': west_hararghe_woredas,
        'east_hararghe_woredas': east_hararghe_woredas,
        'college_departments': collegeDepartments,
    }
    return context

@csrf_exempt
def register_submit(request):
    """API registration endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            password_confirm = data.get('password_confirm')
            
            # Validation
            if not all([username, email, password, password_confirm]):
                return JsonResponse({
                    'success': False,
                    'message': 'All fields are required'
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
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Username already exists'
                }, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Email already exists'
                }, status=400)
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
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
                'message': 'An error occurred during registration'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=400)


def get_redirect_url(user):
    """Determine redirect URL based on user role"""
    if user.is_staff:
        return '/admin-dashboard/'
    elif hasattr(user, 'is_executive') and user.is_executive:
        return '/executive-dashboard/'
    else:
        return '/student-dashboard/'
    
def logout_view(request):
    """Handle logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')

@login_required
def student_dashboard(request):
    """Student dashboard view"""
    try:
        context = {
            'user': request.user,
        }
        
        # Try to get additional data if models exist
        try:
            from posts.models import Post
            from resources.models import Resource
            from tutorials.models import Tutorial, TutorialRegistration
            from analytics.models import Feedback
            
            # Get recent posts
            recent_posts = Post.objects.filter(is_published=True).order_by('-created_at')[:5] if hasattr(Post, 'objects') else []
            
            # Get resources
            resources = Resource.objects.filter(is_approved=True)[:6] if hasattr(Resource, 'objects') else []
            
            # Get available tutorials
            available_tutorials = Tutorial.objects.filter(is_active=True, start_date__gte=timezone.now()) if hasattr(Tutorial, 'objects') else []
            
            # Get user's tutorial registrations
            user_registrations = TutorialRegistration.objects.filter(
                student=request.user, 
                status__in=['registered', 'attended']
            ) if hasattr(TutorialRegistration, 'objects') else []
            
            # Counts for stats
            new_posts_count = Post.objects.filter(is_published=True).count() if hasattr(Post, 'objects') else 0
            resources_count = Resource.objects.filter(is_approved=True).count() if hasattr(Resource, 'objects') else 0
            tutorials_count = user_registrations.count() if user_registrations else 0
            
            context.update({
                'recent_posts': recent_posts,
                'resources': resources,
                'available_tutorials': available_tutorials,
                'user_registrations': user_registrations,
                'new_posts_count': new_posts_count,
                'resources_count': resources_count,
                'tutorials_count': tutorials_count,
            })
            
        except ImportError:
            # Models don't exist yet
            pass
            
        return render(request, 'student-dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return render(request, 'student-dashboard.html')

@login_required
def admin_dashboard(request):
    """Admin dashboard view"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('student-dashboard')
    
    try:
        # Admin statistics
        total_users = User.objects.count()
        
        context = {
            'user': request.user,
            'total_users': total_users,
        }
        
        # Try to get additional statistics if models exist
        try:
            from posts.models import Post
            from resources.models import Resource
            from tutorials.models import Tutorial, TutorialRegistration
            
            total_posts = Post.objects.count() if hasattr(Post, 'objects') else 0
            total_resources = Resource.objects.count() if hasattr(Resource, 'objects') else 0
            total_tutorials = Tutorial.objects.count() if hasattr(Tutorial, 'objects') else 0
            total_registrations = TutorialRegistration.objects.count() if hasattr(TutorialRegistration, 'objects') else 0
            
            context.update({
                'total_posts': total_posts,
                'total_resources': total_resources,
                'total_tutorials': total_tutorials,
                'total_registrations': total_registrations,
            })
            
        except ImportError:
            pass
            
        return render(request, 'admin-dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading admin dashboard: {str(e)}')
        return render(request, 'admin-dashboard.html')

@login_required
def executive_dashboard(request):
    """Executive dashboard view"""
    try:
        # Check if user is executive
        if not (request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'Executive')):
            messages.error(request, 'Access denied. Executive privileges required.')
            return redirect('student-dashboard')
        
        context = {
            'user': request.user,
        }
        
        return render(request, 'executive-dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading executive dashboard: {str(e)}')
        return render(request, 'executive-dashboard.html')

@login_required
def register_tutorial(request):
    """Handle tutorial registration"""
    if request.method == 'POST':
        try:
            tutorial_id = request.POST.get('tutorial')
            
            from tutorials.models import Tutorial, TutorialRegistration
            
            tutorial = Tutorial.objects.get(id=tutorial_id, is_active=True)
            
            # Check if user is already registered
            existing_registration = TutorialRegistration.objects.filter(
                student=request.user, 
                tutorial=tutorial
            ).first()
            
            if existing_registration:
                if existing_registration.status == 'registered':
                    messages.warning(request, 'You are already registered for this tutorial.')
                elif existing_registration.status == 'cancelled':
                    existing_registration.status = 'registered'
                    existing_registration.save()
                    messages.success(request, 'Tutorial registration re-activated!')
                return redirect('student-dashboard')
            
            # Create new registration
            TutorialRegistration.objects.create(
                student=request.user,
                tutorial=tutorial,
                status='registered'
            )
            
            messages.success(request, f'Successfully registered for {tutorial.title}!')
            
        except Tutorial.DoesNotExist:
            messages.error(request, 'Tutorial not found or not available.')
        except Exception as e:
            messages.error(request, f'Error registering for tutorial: {str(e)}')
        
        return redirect('student-dashboard')
    
    return redirect('student-dashboard')

@login_required
def cancel_tutorial_registration(request, registration_id):
    """Cancel tutorial registration"""
    try:
        from tutorials.models import TutorialRegistration
        
        registration = TutorialRegistration.objects.get(
            id=registration_id, 
            student=request.user,
            status='registered'
        )
        
        registration.status = 'cancelled'
        registration.save()
        
        messages.success(request, 'Tutorial registration cancelled successfully.')
        
    except TutorialRegistration.DoesNotExist:
        messages.error(request, 'Registration not found.')
    except Exception as e:
        messages.error(request, f'Error cancelling registration: {str(e)}')
    
    return redirect('student-dashboard')

def contact_feedback(request):
    """Contact and feedback page"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            feedback_type = request.POST.get('type')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            
            from analytics.models import Feedback
            
            Feedback.objects.create(
                user=request.user if request.user.is_authenticated else None,
                feedback_type=feedback_type,
                subject=subject,
                message=message,
                anonymous=bool(request.POST.get('anonymous', False)),
                status='submitted'
            )
            
            messages.success(request, 'Thank you for your feedback! We will review it soon.')
            
        except Exception as e:
            messages.error(request, 'Error submitting feedback. Please try again.')
        
        return redirect('index')
    
    return render(request, 'feedback.html')

# ============================================================================
# API VIEWS (for REST API endpoints)
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_api(request):
    """API registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate token
        _, token = AuthToken.objects.create(user)
        
        return Response({
            'success': True,
            'message': 'Registration successful!',
            'user': UserSerializer(user).data,
            'token': token
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': 'Registration failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_api(request):
    """API login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        
        # Generate token for API
        _, token = AuthToken.objects.create(user)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'token': token
        })
    
    return Response({
        'success': False,
        'message': 'Login failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout_api(request):
    """API logout endpoint"""
    request._auth.delete()
    return Response({
        'success': True,
        'message': 'Logout successful'
    })

@api_view(['GET'])
def get_current_user(request):
    """Get current user data"""
    serializer = UserSerializer(request.user)
    return Response({
        'success': True,
        'user': serializer.data
    })

class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class UserUpdateView(generics.UpdateAPIView):
    """User update view"""
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'user': UserSerializer(instance).data
        })

@api_view(['POST'])
def change_password(request):
    """Change password endpoint"""
    serializer = PasswordChangeSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        
        if not user.check_password(serializer.validated_data['current_password']):
            return Response({
                'success': False,
                'message': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        })
    
    return Response({
        'success': False,
        'message': 'Password change failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

# Admin views for user management
class UserListView(generics.ListAPIView):
    """User list view for admin"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role', 'department', 'year_of_study', 'zone']
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.none()

class UserRoleUpdateView(generics.UpdateAPIView):
    """User role update view for admin"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    
    def update(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({
                'success': False,
                'message': 'Access denied. Admin privileges required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        role = request.data.get('role')
        executive_title = request.data.get('executive_title')
        
        if role:
            user.role = role
        if executive_title:
            user.executive_title = executive_title
        
        user.save()
        
        return Response({
            'success': True,
            'message': 'User role updated successfully',
            'user': UserSerializer(user).data
        })

# Geographical and academic data views
class ZoneListView(generics.ListAPIView):
    """Zone list view"""
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [permissions.AllowAny]

class WoredaListView(generics.ListAPIView):
    """Woreda list view"""
    serializer_class = WoredaSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        zone_id = self.request.query_params.get('zone_id')
        if zone_id:
            return Woreda.objects.filter(zone_id=zone_id)
        return Woreda.objects.all()

class CollegeListView(generics.ListAPIView):
    """College list view"""
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [permissions.AllowAny]

class DepartmentListView(generics.ListAPIView):
    """Department list view"""
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        college_id = self.request.query_params.get('college_id')
        if college_id:
            return Department.objects.filter(college_id=college_id)
        return Department.objects.all()

# Additional API endpoints
@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """API login endpoint for AJAX requests"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': getattr(user, 'role', 'Student')
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid credentials'
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def api_get_users(request):
    """API endpoint to get users"""
    try:
        users = User.objects.all()
        user_data = []
        for user in users:
            user_data.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': getattr(user, 'role', 'Student'),
                'department': getattr(user, 'department', ''),
                'year_of_study': getattr(user, 'year_of_study', ''),
                'is_active': user.is_active
            })
        
        return JsonResponse({
            'success': True,
            'users': user_data,
            'count': len(user_data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)