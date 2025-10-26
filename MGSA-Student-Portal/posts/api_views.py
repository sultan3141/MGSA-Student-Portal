# posts/api_views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Post, Comment

@require_http_methods(["GET"])
def api_get_posts(request):
    """Get all posts"""
    try:
        posts = Post.objects.filter(is_published=True).order_by('-created_at')
        post_data = []
        for post in posts:
            post_data.append({
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'author': {
                    'id': post.author.id,
                    'name': f"{post.author.first_name} {post.author.last_name}",
                    'role': post.author.role
                },
                'post_type': post.post_type,
                'likes_count': post.likes_count,
                'comments_count': post.comments_count,
                'created_at': post.created_at.isoformat() if post.created_at else None,
                'media_url': post.media.url if post.media else None
            })
        
        return JsonResponse({
            'success': True,
            'posts': post_data,
            'count': len(post_data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_like_post(request, post_id):
    """Like/unlike a post"""
    try:
        post = Post.objects.get(id=post_id)
        user = request.user
        
        # Toggle like
        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
            
        post.likes_count = post.likes.count()
        post.save()
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': post.likes_count
        })
    except Post.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Post not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)