from rest_framework import serializers
from .models import LabTest, TestResult


class LabTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTest
        fields = '__all__'
        read_only_fields = ['test_id']
    
    def validate_test_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Test name must have at least 3 characters")
        return value.strip()
    
    def validate(self, data):
        if data.get('low_range') and data.get('high_range'):
            if data['low_range'] >= data['high_range']:
                raise serializers.ValidationError({
                    "high_range": "High range must be greater than low range"
                })
        
        if data.get('test_cost') and data['test_cost'] < 0:
            raise serializers.ValidationError({
                "test_cost": "Test cost must be a positive number"
            })
        
        return data


class LabTestUpdateSerializer(serializers.ModelSerializer):
    """Only allow editing name and description"""
    class Meta:
        model = LabTest
        fields = ['test_name', 'test_description', 'test_cost']


class TestResultSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.Patient_name', read_only=True)
    test_name = serializers.CharField(source='test.test_name', read_only=True)
    is_normal = serializers.BooleanField(read_only=True)
    low_range = serializers.DecimalField(source='test.low_range', max_digits=10, decimal_places=2, read_only=True)
    high_range = serializers.DecimalField(source='test.high_range', max_digits=10, decimal_places=2, read_only=True)
    unit = serializers.CharField(source='test.unit', read_only=True)
    
    class Meta:
        model = TestResult
        fields = '__all__'
        read_only_fields = ['result_id', 'test_date', 'is_normal']
    
    def validate_result_value(self, value):
        if value < 0:
            raise serializers.ValidationError("Result value cannot be negative")
        return value
