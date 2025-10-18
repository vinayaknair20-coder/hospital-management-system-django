# admin_app/serializers.py - COMPLETE PRODUCTION VERSION
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Staff, Specialization, LoginLog


class SpecializationSerializer(serializers.ModelSerializer):
    """Specialization Serializer"""
    class Meta:
        model = Specialization
        fields = '__all__'
        read_only_fields = ['specialization_id']


class StaffSerializer(serializers.ModelSerializer):
    """Staff Serializer with password hashing"""
    specialization_name = serializers.CharField(source='specialization.specialization_name', read_only=True)
    
    class Meta:
        model = Staff
        fields = [
            'staff_id', 'staff_name', 'username', 'password', 'gender', 
            'date_of_birth', 'address', 'joining_date', 'Phone_number', 
            'Email', 'role', 'specialization', 'specialization_name', 
            'salary', 'is_active', 'failed_login_attempts', 'locked_until'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'salary': {'write_only': True}
        }
        read_only_fields = ['staff_id', 'failed_login_attempts', 'locked_until']
    
    def create(self, validated_data):
        """Hash password when creating staff"""
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class StaffUpdateSerializer(serializers.ModelSerializer):
    """Staff Update Serializer (exclude sensitive fields)"""
    class Meta:
        model = Staff
        fields = [
            'staff_id', 'staff_name', 'gender', 'date_of_birth', 
            'address', 'Phone_number', 'Email', 'specialization', 
            'salary', 'is_active'
        ]
        read_only_fields = ['staff_id']


class LoginLogSerializer(serializers.ModelSerializer):
    """Login Log Serializer"""
    class Meta:
        model = LoginLog
        fields = '__all__'
        read_only_fields = ['log_id', 'timestamp']
