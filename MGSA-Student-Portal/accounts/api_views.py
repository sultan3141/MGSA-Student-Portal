# accounts/api_views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User
from posts.models import Post
from resources.models import Resource
from tutorials.models import Tutorial, TutorialRegistration
from analytics.models import Feedback

@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """API login endpoint"""
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
                    'role': user.role
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

@csrf_exempt
@require_http_methods(["POST"])
def api_logout(request):
    """API logout endpoint"""
    try:
        logout(request)
        return JsonResponse({
            'success': True,
            'message': 'Logout successful'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def api_get_current_user(request):
    """Get current user profile"""
    try:
        if request.user.is_authenticated:
            user = request.user
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'department': user.department,
                    'year_of_study': user.year_of_study,
                    'is_active': user.is_active
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Not authenticated'
            }, status=401)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def api_get_users(request):
    """Get all users (admin only)"""
    try:
        if not request.user.is_authenticated or request.user.role != 'Admin':
            return JsonResponse({
                'success': False,
                'message': 'Access denied'
            }, status=403)
            
        users = User.objects.all()
        user_data = []
        for user in users:
            user_data.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': user.role,
                'department': user.department,
                'year_of_study': user.year_of_study,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None
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

@csrf_exempt
@require_http_methods(["PATCH"])
def api_update_user_role(request, user_id):
    """Update user role (admin only)"""
    try:
        if not request.user.is_authenticated or request.user.role != 'Admin':
            return JsonResponse({
                'success': False,
                'message': 'Access denied'
            }, status=403)
            
        data = json.loads(request.body)
        role = data.get('role')
        executive_title = data.get('executive_title', '')
        
        try:
            user = User.objects.get(id=user_id)
            user.role = role
            if role == 'Executive' and executive_title:
                user.executive_title = executive_title
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': f'User role updated to {role}'
            })
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'User not found'
            }, status=404)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)