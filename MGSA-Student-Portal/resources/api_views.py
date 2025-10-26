# resources/api_views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Resource

@require_http_methods(["GET"])
def api_get_resources(request):
    """Get all resources"""
    try:
        resources = Resource.objects.filter(is_approved=True)
        resource_data = []
        for resource in resources:
            resource_data.append({
                'id': resource.id,
                'title': resource.title,
                'description': resource.description,
                'resource_type': resource.resource_type,
                'file_size': resource.file_size,
                'download_count': resource.download_count,
                'uploaded_by': {
                    'id': resource.uploaded_by.id,
                    'name': f"{resource.uploaded_by.first_name} {resource.uploaded_by.last_name}"
                },
                'upload_date': resource.upload_date.isoformat() if resource.upload_date else None,
                'file_url': resource.file.url if resource.file else None
            })
        
        return JsonResponse({
            'success': True,
            'resources': resource_data,
            'count': len(resource_data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_download_resource(request, resource_id):
    """Download a resource"""
    try:
        resource = Resource.objects.get(id=resource_id)
        resource.download_count += 1
        resource.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Download started',
            'download_url': resource.file.url if resource.file else None
        })
    except Resource.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Resource not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)