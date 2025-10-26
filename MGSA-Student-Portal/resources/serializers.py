from rest_framework import serializers
from .models import Resource
from accounts.serializers import UserSerializer

class ResourceSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Resource
        fields = '__all__'
        read_only_fields = ('uploaded_by', 'download_count', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)

class ResourceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ('title', 'description', 'file_url', 'file_name', 'file_type', 'file_size', 'category', 'tags', 'is_public')