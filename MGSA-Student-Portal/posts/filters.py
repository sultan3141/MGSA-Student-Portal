# posts/filters.py
import django_filters
from django.db.models import JSONField
from .models import Post

class PostFilter(django_filters.FilterSet):
    class Meta:
        model = Post
        fields = ['title', 'tags', 'author', 'is_public']
        filter_overrides = {
            JSONField: {
                'filter_class': django_filters.CharFilter,  # treat JSONField as CharFilter
                'extra': lambda f: {'lookup_expr': 'icontains'}  # search with icontains
            }
        }
