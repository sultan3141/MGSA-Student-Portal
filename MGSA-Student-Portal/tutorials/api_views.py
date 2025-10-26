# tutorials/api_views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Tutorial, TutorialRegistration

@require_http_methods(["GET"])
def api_get_tutorials(request):
    """Get all tutorials"""
    try:
        tutorials = Tutorial.objects.filter(is_active=True)
        tutorial_data = []
        for tutorial in tutorials:
            tutorial_data.append({
                'id': tutorial.id,
                'title': tutorial.title,
                'subject': tutorial.subject,
                'description': tutorial.description,
                'tutor': {
                    'id': tutorial.tutor.id,
                    'name': f"{tutorial.tutor.first_name} {tutorial.tutor.last_name}"
                },
                'department': tutorial.department.name if tutorial.department else 'General',
                'schedule': tutorial.schedule,
                'capacity': tutorial.capacity,
                'current_registrations': tutorial.current_registrations,
                'start_date': tutorial.start_date.isoformat() if tutorial.start_date else None,
                'end_date': tutorial.end_date.isoformat() if tutorial.end_date else None,
                'is_full': tutorial.is_full()
            })
        
        return JsonResponse({
            'success': True,
            'tutorials': tutorial_data,
            'count': len(tutorial_data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_register_tutorial(request):
    """Register for a tutorial"""
    try:
        data = json.loads(request.body)
        tutorial_id = data.get('tutorial')
        
        tutorial = Tutorial.objects.get(id=tutorial_id, is_active=True)
        
        if tutorial.is_full():
            return JsonResponse({
                'success': False,
                'message': 'This tutorial is already full'
            }, status=400)
        
        # Check if already registered
        existing_registration = TutorialRegistration.objects.filter(
            student=request.user, 
            tutorial=tutorial
        ).first()
        
        if existing_registration:
            if existing_registration.status == 'registered':
                return JsonResponse({
                    'success': False,
                    'message': 'You are already registered for this tutorial'
                }, status=400)
            elif existing_registration.status == 'cancelled':
                # Re-activate cancelled registration
                existing_registration.status = 'registered'
                existing_registration.save()
        else:
            # Create new registration
            TutorialRegistration.objects.create(
                student=request.user,
                tutorial=tutorial,
                status='registered'
            )
        
        # Update tutorial registration count
        tutorial.current_registrations += 1
        tutorial.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully registered for {tutorial.title}!'
        })
    except Tutorial.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Tutorial not found or not available'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
@login_required
def api_get_my_registrations(request):
    """Get current user's tutorial registrations"""
    try:
        registrations = TutorialRegistration.objects.filter(
            student=request.user
        ).select_related('tutorial')
        
        registration_data = []
        for registration in registrations:
            registration_data.append({
                'id': registration.id,
                'tutorial': {
                    'id': registration.tutorial.id,
                    'title': registration.tutorial.title,
                    'subject': registration.tutorial.subject,
                    'tutor': f"{registration.tutorial.tutor.first_name} {registration.tutorial.tutor.last_name}"
                },
                'status': registration.status,
                'registered_at': registration.registered_at.isoformat() if registration.registered_at else None
            })
        
        return JsonResponse({
            'success': True,
            'registrations': registration_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)