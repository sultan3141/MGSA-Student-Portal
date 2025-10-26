# analytics/api_views.py
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from accounts.models import User
from posts.models import Post
from resources.models import Resource
from tutorials.models import Tutorial, TutorialRegistration
from .models import Feedback

@require_http_methods(["GET"])
@login_required
def api_dashboard_stats(request):
    """Get dashboard statistics"""
    try:
        if request.user.role != 'Admin':
            return JsonResponse({
                'success': False,
                'message': 'Access denied'
            }, status=403)
            
        stats = {
            'total_users': User.objects.count(),
            'total_students': User.objects.filter(role='Student').count(),
            'executives_count': User.objects.filter(role='Executive').count(),
            'active_posts': Post.objects.filter(is_published=True).count(),
            'total_resources': Resource.objects.filter(is_approved=True).count(),
            'total_tutorials': Tutorial.objects.filter(is_active=True).count(),
            'total_registrations': TutorialRegistration.objects.count(),
            'pending_feedback': Feedback.objects.filter(status='pending').count()
        }
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def api_get_feedback(request):
    """Get all feedback"""
    try:
        if not request.user.is_authenticated or request.user.role != 'Admin':
            return JsonResponse({
                'success': False,
                'message': 'Access denied'
            }, status=403)
            
        feedback_list = Feedback.objects.all().order_by('-created_at')
        feedback_data = []
        for feedback in feedback_list:
            feedback_data.append({
                'id': feedback.id,
                'user': {
                    'id': feedback.user.id if feedback.user else None,
                    'first_name': feedback.user.first_name if feedback.user else 'Anonymous',
                    'last_name': feedback.user.last_name if feedback.user else '',
                    'email': feedback.user.email if feedback.user else 'N/A'
                },
                'type': feedback.feedback_type,
                'subject': feedback.subject,
                'message': feedback.message,
                'status': feedback.status,
                'created_at': feedback.created_at.isoformat() if feedback.created_at else None
            })
        
        return JsonResponse({
            'success': True,
            'feedback': feedback_data,
            'count': len(feedback_data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)