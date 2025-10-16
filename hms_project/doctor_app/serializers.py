from rest_framework import serializers
from .models import Consultation, Prescription, MedicinePrescription, TestPrescription


class ConsultationSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='appointment.Patient_id.Patient_name', read_only=True)
    doctor_name = serializers.CharField(source='appointment.doctor_id.staff_name', read_only=True)
    appointment_date = serializers.DateField(source='appointment.Appointment_date', read_only=True)
    
    class Meta:
        model = Consultation
        fields = '__all__'
        read_only_fields = ['consultation_id', 'consultation_date']
    
    def validate_symptoms(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Symptoms must have at least 3 characters")
        return value.strip()
    
    def validate_diagnosis(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Diagnosis must have at least 3 characters")
        return value.strip()


class MedicinePrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicinePrescription
        fields = '__all__'
        read_only_fields = ['medicine_prescription_id']
    
    def validate_medicine_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Medicine name must have at least 3 characters")
        return value.strip()
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class TestPrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestPrescription
        fields = '__all__'
        read_only_fields = ['test_prescription_id']
    
    def validate_test_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Test name must have at least 3 characters")
        return value.strip()


class PrescriptionSerializer(serializers.ModelSerializer):
    medicines = MedicinePrescriptionSerializer(many=True, read_only=True)
    tests = TestPrescriptionSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source='consultation.appointment.Patient_id.Patient_name', read_only=True)
    doctor_name = serializers.CharField(source='consultation.appointment.doctor_id.staff_name', read_only=True)
    
    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ['prescription_id', 'prescription_date']
