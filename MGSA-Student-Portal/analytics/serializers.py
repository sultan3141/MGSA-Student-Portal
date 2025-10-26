from rest_framework import serializers
from .models import Feedback, UserActivity

class FeedbackSerializer(serializers.ModelSerializer):
    user_display = serializers.CharField(source='get_user_display', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'user', 'user_display', 'anonymous', 'feedback_type', 
            'subject', 'message', 'priority', 'status', 'admin_notes',
            'resolved_by', 'resolved_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'resolved_by', 'resolved_at']
    
    def create(self, validated_data):
        # Set user from request if not anonymous
        request = self.context.get('request')
        if request and request.user.is_authenticated and not validated_data.get('anonymous'):
            validated_data['user'] = request.user
        return super().create(validated_data)

class UserActivitySerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'user_email', 'user_name', 'activity_type',
            'description', 'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']