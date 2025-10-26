from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Zone, Woreda, College, Department

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'middle_name', 'last_name', 'gender',
            'zone', 'woreda', 'college', 'department', 'year_of_study',
            'email', 'student_id', 'password', 'password_confirm'
        )
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password')
            if not user.is_active:
                raise serializers.ValidationError('Account is deactivated')
        else:
            raise serializers.ValidationError('Email and password are required')
        
        attrs['user'] = user
        return attrs

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'middle_name', 'last_name', 'full_name',
            'gender', 'zone', 'woreda', 'college', 'department', 
            'year_of_study', 'email', 'student_id', 'role', 
            'executive_title', 'profile_picture', 'preferred_language',
            'preferred_theme', 'last_login', 'date_joined'
        )
        read_only_fields = ('id', 'date_joined', 'last_login')
    
    def get_full_name(self, obj):
        return obj.get_full_name()

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'middle_name', 'last_name', 'gender',
            'zone', 'woreda', 'college', 'department', 'year_of_study',
            'profile_picture', 'preferred_language', 'preferred_theme'
        )

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'

class WoredaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Woreda
        fields = '__all__'

class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'