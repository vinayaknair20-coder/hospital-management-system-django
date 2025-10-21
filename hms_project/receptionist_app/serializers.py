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
    Appointment_id = serializers.IntegerField(read_only=True)
    patient_name = serializers.CharField(source='Patient_id.Patient_name', read_only=True)
    doctor = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'Appointment_id',
            'Patient_id',
            'doctor_id',
            'patient_name',
            'doctor',
            'Appointment_date',
            'Appointment_time',
            'status'
        ]
        read_only_fields = ['Appointment_id', 'patient_name', 'doctor']

    def get_doctor(self, obj):
        if obj.doctor_id:
            return {
                'doctor_id': obj.doctor_id.staff_id,
                'doctor_name': obj.doctor_id.staff_name,
                'specialization': getattr(obj.doctor_id.specialization, 'specialization_name', None)
            }
        return None

    def create(self, validated_data):
        patient = validated_data.pop('Patient_id')
        doctor = validated_data.pop('doctor_id')
        appointment = Appointment.objects.create(
            Patient_id=patient,
            doctor_id=doctor,
            **validated_data
        )
        return appointment



class BillGenerationSerializer(serializers.ModelSerializer):
    """Bill Generation Serializer"""
    patient_name = serializers.CharField(source='patient.Patient_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.Phone_number', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.staff_name', read_only=True)
    balance = serializers.SerializerMethodField()
    
    class Meta:
        model = Bill_Generation
        fields = ['Bill_id', 'Appointment_id', 'Patient_id', 'patient_name', 'patient_phone', 'appointment_date', 'doctor_name', 'Amount', 'Billing_date', 'Token']
        read_only_fields = ['Bill_id', 'Billing_date', 'Token']
    
    def get_balance(self, obj):
        """Calculate remaining balance"""
        return obj.total_amount - obj.amount_paid
# Add to receptionist_app/serializers.py

