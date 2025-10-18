# labTech_app/serializers.py - COMPLETE PRODUCTION VERSION
from rest_framework import serializers
from .models import LabTest, TestResult


class LabTestSerializer(serializers.ModelSerializer):
    """Lab Test Serializer"""
    total_tests_conducted = serializers.SerializerMethodField()
    
    class Meta:
        model = LabTest
        fields = '__all__'
        read_only_fields = ['test_id', 'created_at']
    
    def get_total_tests_conducted(self, obj):
        """Count total tests conducted"""
        return obj.results.filter(result_status='COMPLETED').count()


class LabTestListSerializer(serializers.ModelSerializer):
    """Lab Test List Serializer (minimal fields)"""
    class Meta:
        model = LabTest
        fields = ['test_id', 'test_name', 'price', 'sample_type', 'is_active']


class TestResultSerializer(serializers.ModelSerializer):
    """Test Result Serializer with nested data"""
    patient_name = serializers.CharField(source='patient.Patient_name', read_only=True)
    patient_age = serializers.SerializerMethodField()
    test_name = serializers.CharField(source='lab_test.test_name', read_only=True)
    test_normal_range = serializers.CharField(source='lab_test.normal_range', read_only=True)
    test_unit = serializers.CharField(source='lab_test.unit', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.staff_name', read_only=True)
    
    class Meta:
        model = TestResult
        fields = '__all__'
        read_only_fields = ['result_id', 'created_at', 'updated_at']
    
    def get_patient_age(self, obj):
        """Calculate patient age"""
        from datetime import date
        if obj.patient.Date_of_Birth:
            today = date.today()
            return today.year - obj.patient.Date_of_Birth.year
        return None


class TestResultListSerializer(serializers.ModelSerializer):
    """Test Result List Serializer (minimal fields)"""
    patient_name = serializers.CharField(source='patient.Patient_name', read_only=True)
    test_name = serializers.CharField(source='lab_test.test_name', read_only=True)
    
    class Meta:
        model = TestResult
        fields = [
            'result_id', 'patient', 'patient_name', 'lab_test', 
            'test_name', 'test_date', 'result_status', 'is_normal'
        ]
class LabTestUpdateSerializer(serializers.ModelSerializer):
    """Lab Test Update Serializer"""
    class Meta:
        model = LabTest
        fields = '__all__'
        read_only_fields = ['test_id', 'created_at']


class TestResultUpdateSerializer(serializers.ModelSerializer):
    """Test Result Update Serializer"""
    class Meta:
        model = TestResult
        fields = '__all__'
        read_only_fields = ['result_id', 'created_at', 'updated_at']