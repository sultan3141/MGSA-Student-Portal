from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Post, Like, Comment

class CommentInline(admin.TabularInline):
    """Inline comments for posts"""
    model = Comment
    extra = 0
    readonly_fields = ['user', 'content', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

class LikeInline(admin.TabularInline):
    """Inline likes for posts"""
    model = Like
    extra = 0
    readonly_fields = ['user', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'author_display', 
        'media_type_display', 
        'is_public', 
        'view_count', 
        'like_count', 
        'comment_count', 
        'created_at_display',
        'post_age'
    ]
    
    list_filter = [
        'is_public', 
        'media_type', 
        'created_at',
        'author__role'
    ]
    
    search_fields = [
        'title', 
        'content', 
        'author__first_name', 
        'author__last_name', 
        'author__email',
        'tags'
    ]
    
    readonly_fields = [
        'view_count', 
        'share_count', 
        'created_at', 
        'updated_at',
        'like_count_display',
        'comment_count_display',
        'media_preview'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 
                'content', 
                'author',
                'tags'
            )
        }),
        ('Media Content', {
            'fields': (
                'media_type',
                'media_url',
                'media_public_id',
                'media_preview'
            ),
            'classes': ('collapse',)
        }),
        ('Visibility & Statistics', {
            'fields': (
                'is_public',
                'view_count',
                'share_count',
                'like_count_display',
                'comment_count_display'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    inlines = [CommentInline, LikeInline]
    
    # Custom actions
    actions = ['make_public', 'make_private', 'reset_view_count']
    
    def author_display(self, obj):
        return f"{obj.author.get_full_name()} ({obj.author.email})"
    author_display.short_description = 'Author'
    author_display.admin_order_field = 'author__first_name'
    
    def media_type_display(self, obj):
        if obj.media_type:
            return obj.get_media_type_display()
        return "Text Only"
    media_type_display.short_description = 'Media Type'
    
    def like_count(self, obj):
        return obj.likes.count()
    like_count.short_description = 'Likes'
    
    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Comments'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at_display.short_description = 'Created'
    created_at_display.admin_order_field = 'created_at'
    
    def post_age(self, obj):
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days} day(s) ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} hour(s) ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} minute(s) ago"
        else:
            return "Just now"
    post_age.short_description = 'Age'
    
    def like_count_display(self, obj):
        return obj.likes.count()
    like_count_display.short_description = 'Total Likes'
    
    def comment_count_display(self, obj):
        return obj.comments.count()
    comment_count_display.short_description = 'Total Comments'
    
    def media_preview(self, obj):
        if obj.media_url and obj.media_type == 'image':
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.media_url
            )
        elif obj.media_url and obj.media_type == 'video':
            return format_html(
                '<a href="{}" target="_blank">View Video</a>',
                obj.media_url
            )
        return "No media"
    media_preview.short_description = 'Media Preview'
    
    # Custom actions
    def make_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} posts marked as public.')
    make_public.short_description = "Mark selected posts as public"
    
    def make_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} posts marked as private.')
    make_private.short_description = "Mark selected posts as private"
    
    def reset_view_count(self, request, queryset):
        updated = queryset.update(view_count=0)
        self.message_user(request, f'View count reset for {updated} posts.')
    reset_view_count.short_description = "Reset view count for selected posts"
    
    # Override save method to handle tags
    def save_model(self, request, obj, form, change):
        # Ensure tags are stored as list
        if isinstance(obj.tags, str):
            obj.tags = [tag.strip() for tag in obj.tags.split(',') if tag.strip()]
        super().save_model(request, obj, form, change)
    
    # Custom formfield for tags
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'tags':
            kwargs['help_text'] = 'Enter tags as comma-separated values'
        return super().formfield_for_dbfield(db_field, request, **kwargs)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = [
        'user_display',
        'post_title',
        'created_at_display'
    ]
    
    list_filter = [
        'created_at',
        'post__author'
    ]
    
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__email',
        'post__title'
    ]
    
    readonly_fields = ['created_at']
    
    def user_display(self, obj):
        return f"{obj.user.get_full_name()} ({obj.user.email})"
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user__first_name'
    
    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = 'Post'
    post_title.admin_order_field = 'post__title'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at_display.short_description = 'Liked At'
    created_at_display.admin_order_field = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'truncated_content',
        'user_display',
        'post_title',
        'is_edited',
        'created_at_display',
        'has_replies'
    ]
    
    list_filter = [
        'is_edited',
        'created_at',
        'post__author'
    ]
    
    search_fields = [
        'content',
        'user__first_name',
        'user__last_name',
        'user__email',
        'post__title'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Comment Information', {
            'fields': (
                'post',
                'user',
                'content',
                'parent_comment'
            )
        }),
        ('Status', {
            'fields': ('is_edited',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def truncated_content(self, obj):
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
    truncated_content.short_description = 'Comment'
    
    def user_display(self, obj):
        return f"{obj.user.get_full_name()} ({obj.user.email})"
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user__first_name'
    
    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = 'Post'
    post_title.admin_order_field = 'post__title'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at_display.short_description = 'Commented At'
    created_at_display.admin_order_field = 'created_at'
    
    def has_replies(self, obj):
        return obj.replies.exists()
    has_replies.short_description = 'Has Replies'
    has_replies.boolean = True
    
    # Custom actions
    actions = ['mark_as_edited', 'delete_replies']
    
    def mark_as_edited(self, request, queryset):
        updated = queryset.update(is_edited=True)
        self.message_user(request, f'{updated} comments marked as edited.')
    mark_as_edited.short_description = "Mark selected comments as edited"
    
    def delete_replies(self, request, queryset):
        for comment in queryset:
            comment.replies.all().delete()
        self.message_user(request, f'Replies deleted for {queryset.count()} comments.')
    delete_replies.short_description = "Delete replies for selected comments"

# Custom admin site configuration (optional)
class PostsAdminSite(admin.AdminSite):
    site_header = "MGSA Posts Administration"
    site_title = "MGSA Posts Admin"
    index_title = "Posts Management"


    
    # ... rest of the PostAdmin code remains the same
# If you want to register with custom admin site
# posts_admin_site = PostsAdminSite(name='posts_admin')
# posts_admin_site.register(Post, PostAdmin)
# posts_admin_site.register(Like, LikeAdmin)
# posts_admin_site.register(Comment, CommentAdmin)
