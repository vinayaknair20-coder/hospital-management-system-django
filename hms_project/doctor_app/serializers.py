# doctor_app/serializers.py - COMPLETE PRODUCTION VERSION
from rest_framework import serializers
from .models import Consultation, Prescription, MedicinePrescription, TestPrescription


class ConsultationSerializer(serializers.ModelSerializer):
    """Consultation Serializer with nested data"""
    patient_name = serializers.CharField(source='patient.Patient_name', read_only=True)
    patient_age = serializers.SerializerMethodField()
    doctor_name = serializers.CharField(source='doctor.staff_name', read_only=True)
    appointment_id = serializers.IntegerField(source='appointment.appointment_id', read_only=True)
    
    class Meta:
        model = Consultation
        fields = '__all__'
        read_only_fields = ['consultation_id', 'created_at', 'updated_at']
    
    def get_patient_age(self, obj):
        """Calculate patient age"""
        from datetime import date
        if obj.patient.Date_of_Birth:
            today = date.today()
            return today.year - obj.patient.Date_of_Birth.year
        return None


class ConsultationListSerializer(serializers.ModelSerializer):
    """Consultation List Serializer (minimal fields)"""
    patient_name = serializers.CharField(source='patient.Patient_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.staff_name', read_only=True)
    
    class Meta:
        model = Consultation
        fields = [
            'consultation_id', 'patient', 'patient_name', 'doctor', 
            'doctor_name', 'consultation_date', 'status'
        ]


class MedicinePrescriptionSerializer(serializers.ModelSerializer):
    """Medicine Prescription Serializer"""
    class Meta:
        model = MedicinePrescription
        fields = '__all__'
        read_only_fields = ['medicine_prescription_id']


class TestPrescriptionSerializer(serializers.ModelSerializer):
    """Test Prescription Serializer"""
    class Meta:
        model = TestPrescription
        fields = '__all__'
        read_only_fields = ['test_prescription_id']


class PrescriptionSerializer(serializers.ModelSerializer):
    """Prescription Serializer with nested medicines and tests"""
    patient_name = serializers.CharField(source='patient.Patient_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.staff_name', read_only=True)
    medicines = MedicinePrescriptionSerializer(many=True, read_only=True)
    tests = TestPrescriptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ['prescription_id', 'created_at']


class PrescriptionCreateSerializer(serializers.ModelSerializer):
    """Prescription Create Serializer with nested creation"""
    medicines = MedicinePrescriptionSerializer(many=True, required=False)
    tests = TestPrescriptionSerializer(many=True, required=False)
    
    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ['prescription_id', 'created_at']
    
    def create(self, validated_data):
        """Create prescription with medicines and tests"""
        medicines_data = validated_data.pop('medicines', [])
        tests_data = validated_data.pop('tests', [])
        
        prescription = Prescription.objects.create(**validated_data)
        
        # Create medicines
        for medicine_data in medicines_data:
            MedicinePrescription.objects.create(prescription=prescription, **medicine_data)
        
        # Create tests
        for test_data in tests_data:
            TestPrescription.objects.create(prescription=prescription, **test_data)
        
        return prescription
