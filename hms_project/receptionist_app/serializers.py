from decimal import Decimal
from rest_framework import serializers
import re
from .models import Patient, Appointment, Bill_Generation


class PatientSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        appointments_data = validated_data.pop('appointments', None)
        patient = Patient.objects.create(**validated_data)
        if appointments_data:
            for appointment_data in appointments_data:
                Appointment.objects.create(Patient_id=patient, **appointment_data)
        return patient
    class Meta:
        model = Patient
        fields = '__all__' 
    
    def validate_Patient_name(self, value):
        # Should not start with space
        if value.lstrip() != value:
           raise serializers.ValidationError("Patient name should not start with a space.")

        # Should contain only alphabets (at least 3 letters)
        if not re.match(r'^[A-Za-z]{3,}(?: [A-Za-z]+)*$', value):
            raise serializers.ValidationError("Patient name must be at least 3 alphabetic letters and contain only alphabets.")

        return value
    def validate_Age(self, value):
        if value < 1 or value > 120:
            raise serializers.ValidationError("Age must be between 1 and 120.")
        return value
    def validate_Gender(self, value):
        allowed_genders = ["M", "F", "O","m","f","o"]  # case-sensitive
        if value not in allowed_genders:
            raise serializers.ValidationError("Gender must be one of 'M', 'F', or 'O'.")
        return value
    def validate_Blood_Group(self, value):
        allowed_blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-","a+","a-","b+","b-","ab+","ab-","o+","o-"]  # case-sensitive
        if value not in allowed_blood_groups:
            raise serializers.ValidationError("Blood Group must be one of 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', or 'O-'.")
        return value

    def validate_Phone_number(self, value):
        if not re.match(r'^[6-9]\d{9}$', value):
            raise serializers.ValidationError("Phone number must be 10 digits and start with 6, 7, 8, or 9.")
        return value
    
    def validate_Email(self, value):
        if value and not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', value):
            raise serializers.ValidationError("Invalid email format.")
        return value
    def validate_Address(self, value):
        if value[0] == " ":
            raise serializers.ValidationError("Address should not start with a space.")

        # At least 3 alphabetic characters somewhere in the string
        if not re.search(r'[A-Za-z]{3,}', value):
            raise serializers.ValidationError("Address must contain at least 3 letters.")
        return value
    def validate_emergency_contact(self, value):
        if not re.match(r'^[6-9]\d{9}$', value):
            raise serializers.ValidationError("Emergency contact number must be 10 digits and start with 6, 7, 8, or 9.")
        # Compare with phone number if both fields exist
        phone_number = self.initial_data.get('Phone_number')
        if phone_number and value == phone_number:
            raise serializers.ValidationError("Emergency contact number cannot be the same as phone number.")
        return value

class DoctorSerializer(serializers.ModelSerializer):
    specialization = serializers.CharField()
    class Meta:
        model = Doctor
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        # Support bulk creation if input is a list of dicts
        if isinstance(validated_data, list):
            appointments = [Appointment.objects.create(**item) for item in validated_data]
            return appointments
        return Appointment.objects.create(**validated_data)
    def validate(self, data):
        doctor = data.get('doctor_id')
        date = data.get('Appointment_date')
        if doctor and date:
            count = Appointment.objects.filter(doctor_id=doctor, Appointment_date=date).count()
            if count >= 25:
                raise serializers.ValidationError("This doctor has reached the maximum number of tokens (25) for the selected date.")
        return data
    specialization = serializers.CharField(source='doctor_id.specialization', read_only=True)
    def validate_Appointment_date(self, value):
        from datetime import date, timedelta
        today = date.today()
        max_date = today + timedelta(days=365)
        if value <= today:
            raise serializers.ValidationError("Appointment date must be in the future.")
        if value > max_date:
            raise serializers.ValidationError("Appointment date cannot be more than 1 year from today.")
        return value
    class Meta:
        model = Appointment
        fields = '__all__'
        extra_fields = ['specialization']

class BillGenerationSerializer(serializers.ModelSerializer):
    Token = serializers.CharField(read_only=True)
    class Meta:
        model = Bill_Generation
        fields = '__all__'

    def validate_Amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive number.") 
        return value