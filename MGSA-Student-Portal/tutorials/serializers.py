from rest_framework import serializers
from .models import Tutorial, TutorialRegistration
from accounts.serializers import UserSerializer

class TutorialSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    is_full = serializers.ReadOnlyField()
    current_registrations_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Tutorial
        fields = '__all__'
        read_only_fields = ('created_by', 'current_registrations', 'created_at', 'updated_at')

class TutorialCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutorial
        fields = ('title', 'description', 'tutor', 'department', 'topics', 
                 'start_date', 'end_date', 'days', 'time', 'max_students', 'is_active')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class TutorialRegistrationSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    tutorial = TutorialSerializer(read_only=True)
    
    class Meta:
        model = TutorialRegistration
        fields = '__all__'
        read_only_fields = ('student', 'registration_date')

class TutorialRegistrationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorialRegistration
        fields = ('tutorial',)
    
    def validate(self, attrs):
        tutorial = attrs['tutorial']
        
        # Check if tutorial is active
        if not tutorial.is_active:
            raise serializers.ValidationError("This tutorial is not active")
        
        # Check if tutorial is full
        if tutorial.is_full():
            raise serializers.ValidationError("This tutorial is full")
        
        # Check if student is already registered
        if TutorialRegistration.objects.filter(
            student=self.context['request'].user,
            tutorial=tutorial
        ).exists():
            raise serializers.ValidationError("You are already registered for this tutorial")
        
        return attrs
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        
        # Increment tutorial registration count
        tutorial = validated_data['tutorial']
        tutorial.current_registrations += 1
        tutorial.save()
        
        return super().create(validated_data)