from rest_framework import serializers
from .models import Patient, Appointment, Bill_Generation
from admin_app.models import Staff
from datetime import date


class PatientSerializer(serializers.ModelSerializer):
    Age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['Patient_id', 'Age']
    
    def validate_Patient_name(self, value):
        """Name must have at least 3 characters"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Patient name must have at least 3 characters")
        return value.strip()
    
    def validate_Phone_number(self, value):
        """Phone number must be exactly 10 digits"""
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits")
        if len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits")
        return value
    
    def validate_Gender(self, value):
        """Gender must be M/F/O"""
        if value not in ['M', 'F', 'O']:
            raise serializers.ValidationError("Gender must be M (Male), F (Female), or O (Other)")
        return value
    
    def validate_date_of_birth(self, value):
        """DOB must be in past"""
        if value >= date.today():
            raise serializers.ValidationError("Date of birth must be in the past")
        return value


class PatientUpdateSerializer(serializers.ModelSerializer):
    """Only allow editing Name and Address"""
    class Meta:
        model = Patient
        fields = ['Patient_name', 'Address', 'Phone_number']
    
    def validate_Patient_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Patient name must have at least 3 characters")
        return value.strip()
    
    def validate_Phone_number(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits")
        return value


class DoctorSerializer(serializers.ModelSerializer):
    specialization_name = serializers.CharField(source='specialization.specialization_name', read_only=True)
    
    class Meta:
        model = Staff
        fields = ['staff_id', 'staff_name', 'specialization', 'specialization_name', 'Phone_number', 'Email']


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='Patient_id.Patient_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor_id.staff_name', read_only=True)
    patient_phone = serializers.CharField(source='Patient_id.Phone_number', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor_id.specialization.specialization_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['Appointment_id', 'Appointment_time']
    
    def validate_Appointment_date(self, value):
        """Appointment date cannot be in the past"""
        if value < date.today():
            raise serializers.ValidationError("Appointment date cannot be in the past")
        return value


class BillGenerationSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='Patient_id.Patient_name', read_only=True)
    patient_phone = serializers.CharField(source='Patient_id.Phone_number', read_only=True)
    appointment_date = serializers.DateField(source='Appointment_id.Appointment_date', read_only=True)
    doctor_name = serializers.CharField(source='Appointment_id.doctor_id.staff_name', read_only=True)
    
    class Meta:
        model = Bill_Generation
        fields = '__all__'
        read_only_fields = ['Bill_id', 'Billing_date', 'Token']
    
    def validate_Amount(self, value):
        """Amount must be positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value
