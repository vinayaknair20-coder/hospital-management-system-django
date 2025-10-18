# receptionist_app/serializers.py - COMPLETE FIXED VERSION
from rest_framework import serializers
from .models import Patient, Appointment,BillGeneration


class PatientSerializer(serializers.ModelSerializer):
    """Patient Serializer"""
    age = serializers.SerializerMethodField()
    registered_by_name = serializers.CharField(source='registered_by.staff_name', read_only=True)
    
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['Patient_id', 'registration_date']
    
    def get_age(self, obj):
        """Calculate patient age"""
        from datetime import date
        if obj.Date_of_Birth:
            today = date.today()
            return today.year - obj.Date_of_Birth.year - (
                (today.month, today.day) < (obj.Date_of_Birth.month, obj.Date_of_Birth.day)
            )
        return None


class PatientListSerializer(serializers.ModelSerializer):
    """Patient List Serializer (minimal fields)"""
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = ['Patient_id', 'Patient_name', 'Phone_number', 'Gender', 'age', 'is_active']
    
    def get_age(self, obj):
        from datetime import date
        if obj.Date_of_Birth:
            today = date.today()
            return today.year - obj.Date_of_Birth.year
        return None


class PatientUpdateSerializer(serializers.ModelSerializer):
    """Patient Update Serializer"""
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['Patient_id', 'registration_date', 'registered_by']


class AppointmentSerializer(serializers.ModelSerializer):
    """Appointment Serializer with nested data"""
    patient_name = serializers.CharField(source='patient.Patient_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.Phone_number', read_only=True)
    doctor_name = serializers.CharField(source='doctor.staff_name', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization.specialization_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.staff_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['appointment_id', 'created_at']


class AppointmentListSerializer(serializers.ModelSerializer):
    """Appointment List Serializer (minimal fields)"""
    patient_name = serializers.CharField(source='patient.Patient_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.staff_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'appointment_id', 'patient', 'patient_name', 'doctor', 
            'doctor_name', 'appointment_date', 'appointment_time', 
            'token_number', 'status'
        ]


class BillGenerationSerializer(serializers.ModelSerializer):
    """Bill Generation Serializer"""
    patient_name = serializers.CharField(source='patient.Patient_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.Phone_number', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.staff_name', read_only=True)
    balance = serializers.SerializerMethodField()
    
    class Meta:
        model = BillGeneration
        fields = '__all__'
        read_only_fields = ['bill_id', 'total_amount']
    
    def get_balance(self, obj):
        """Calculate remaining balance"""
        return obj.total_amount - obj.amount_paid
# Add to receptionist_app/serializers.py

