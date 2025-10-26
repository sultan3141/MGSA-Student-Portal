# admin.py (in the same app as your Resource model)
from django.contrib import admin
from django.utils.html import format_html
from .models import Resource

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'file_type_display',
        'category',
        'uploaded_by',
        'download_count',
        'is_public',
        'file_size_display',
        'created_at'
    ]
    
    list_filter = [
        'file_type',
        'category',
        'is_public',
        'created_at'
    ]
    
    search_fields = [
        'title',
        'description',
        'category',
        'uploaded_by__email',
        'uploaded_by__first_name',
        'uploaded_by__last_name'
    ]
    
    readonly_fields = [
        'download_count',
        'created_at',
        'updated_at',
        'file_preview'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title',
                'description',
                'category',
                'tags'
            )
        }),
        ('File Details', {
            'fields': (
                'file',
                'file_url',
                'file_name',
                'file_type',
                'file_size',
                'file_preview'
            )
        }),
        ('Access Control', {
            'fields': (
                'is_public',
                'download_count'
            )
        }),
        ('Metadata', {
            'fields': (
                'uploaded_by',
                'created_at',
                'updated_at'
            )
        }),
    )
    
    def file_type_display(self, obj):
        color_map = {
            'pdf': '#FF6B6B',
            'doc': '#4ECDC4',
            'docx': '#45B7D1',
            'video': '#96CEB4',
            'image': '#FECA57',
            'other': '#778CA3'
        }
        color = color_map.get(obj.file_type, '#778CA3')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_file_type_display().upper()
        )
    file_type_display.short_description = 'File Type'
    
    def file_size_display(self, obj):
        """Convert bytes to human readable format"""
        if obj.file_size:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if obj.file_size < 1024.0:
                    return f"{obj.file_size:.1f} {unit}"
                obj.file_size /= 1024.0
            return f"{obj.file_size:.1f} TB"
        return "0 B"
    file_size_display.short_description = 'File Size'
    
    def file_preview(self, obj):
        """Show file preview or link"""
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank">View File</a>',
                obj.file.url
            )
        elif obj.file_url:
            return format_html(
                '<a href="{}" target="_blank">View External File</a>',
                obj.file_url
            )
        return "No file available"
    file_preview.short_description = 'File Preview'
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('uploaded_by')
