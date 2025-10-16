from rest_framework import serializers
from .models import Staff, Specialization
from datetime import date


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = '__all__'
        read_only_fields = ['specialization_id']
    
    def validate_specialization_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Specialization name must have at least 3 characters")
        return value.strip()


class StaffSerializer(serializers.ModelSerializer):
    specialization_name = serializers.CharField(source='specialization.specialization_name', read_only=True)
    
    class Meta:
        model = Staff
        fields = ['staff_id', 'staff_name', 'gender', 'date_of_birth', 'address', 
                  'joining_date', 'Phone_number', 'Email', 'role', 'specialization', 
                  'specialization_name', 'salary', 'is_active', 'password']
        read_only_fields = ['staff_id']
        extra_kwargs = {
            'password': {'write_only': True},
            'salary': {'write_only': True}
        }
    
    def validate_staff_name(self, value):
        """Name must have at least 3 characters"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Staff name must have at least 3 characters")
        return value.strip()
    
    def validate_Phone_number(self, value):
        """Phone number must be exactly 10 digits"""
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits")
        if len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits")
        return value
    
    def validate_Email(self, value):
        """Email validation"""
        if not '@' in value:
            raise serializers.ValidationError("Invalid email format")
        return value.lower()
    
    def validate_gender(self, value):
        """Gender must be M/F/O"""
        if value and value not in ['M', 'F', 'O']:
            raise serializers.ValidationError("Gender must be M (Male), F (Female), or O (Other)")
        return value
    
    def validate_date_of_birth(self, value):
        """DOB must be in past"""
        if value and value >= date.today():
            raise serializers.ValidationError("Date of birth must be in the past")
        return value
    
    def validate_salary(self, value):
        """Salary must be positive"""
        if value and value < 0:
            raise serializers.ValidationError("Salary must be a positive number")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        staff = Staff.objects.create(**validated_data)
        if password:
            staff.set_password(password)
            staff.save()
        return staff


class StaffUpdateSerializer(serializers.ModelSerializer):
    """Only allow editing Name, Address, and Phone"""
    class Meta:
        model = Staff
        fields = ['staff_name', 'address', 'Phone_number']
    
    def validate_staff_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Staff name must have at least 3 characters")
        return value.strip()
    
    def validate_Phone_number(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits")
        return value
