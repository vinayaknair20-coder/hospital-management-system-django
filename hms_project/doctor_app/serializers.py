from django.db import transaction
from rest_framework import serializers
from .models import Consultation, Prescription, TestPrescription, MedicinePrescription
from pharmacist_app.models import pharmacist_medicine


# -----------------------------
# Consultation Serializer
# -----------------------------
class ConsultationSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(
        source="appointment.patient.Patient_name", read_only=True
    )
    doctor_name = serializers.CharField(
        source="appointment.doctor.DoctorName", read_only=True
    )
    doctor_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Consultation
        fields = [
            "id",
            "appointment",
            "consultation_date",
            "symptoms",
            "diagnosis",
            "notes",
            "patient_name",
            "doctor_name",
            "doctor_id",
        ]
        read_only_fields = ["consultation_date"]

    def get_doctor_id(self, obj):
        doc = getattr(obj, "doctor", None)
        return getattr(doc, "id", None)


# -----------------------------
# Medicine Prescription Serializer
# -----------------------------
class MedicinePrescriptionSerializer(serializers.ModelSerializer):
    # write: medicine_name (doctor supplies), read: display_name (actual medicine.MedicineName)
    medicine_name = serializers.CharField(write_only=True)
    display_name = serializers.CharField(source="medicine.MedicineName", read_only=True)

    class Meta:
        model = MedicinePrescription
        fields = [
            "id",
            "medicine_name",   # doctor provides this (string)
            "display_name",    # resolved medicine name (read-only)
            "dosage",
            "quantity",
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate_dosage(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Dosage cannot be empty.")
        return value

    @staticmethod
    def _set_default_fields_on_created_medicine(medicine_obj):
        """
        If created medicine has fields like 'Stock' or 'stock' or 'price', attempt to set them.
        This is best-effort: if a field doesn't exist, it is skipped.
        """
        changed = False
        # try both capitalized and lowercase field names to maximize compatibility
        for name in ("Stock", "stock"):
            if hasattr(medicine_obj, name):
                try:
                    setattr(medicine_obj, name, 0)
                    changed = True
                except Exception:
                    pass

        for pname in ("price", "Price"):
            if hasattr(medicine_obj, pname):
                try:
                    setattr(medicine_obj, pname, 0.0)
                    changed = True
                except Exception:
                    pass
        if changed:
            medicine_obj.save()

    @staticmethod
    def get_or_create_medicine_by_name(medicine_name):
        """
        Resolve medicine by name (case-insensitive). If not found, create it and
        set default stock/price fields to zero (best-effort).
        """
        # First try case-insensitive lookup on the field name used in your pharmacist model.
        # We assume your pharmacist model uses a field named 'MedicineName' (as in your code).
        med_qs = pharmacist_medicine.objects.filter(MedicineName__iexact=medicine_name)
        if med_qs.exists():
            return med_qs.first()
        # Not found -> create
        # For creation, try to pass at least the MedicineName field.
        med_obj = pharmacist_medicine.objects.create(**{"MedicineName": medicine_name})
        # set defaults for stock/price fields if they exist on the model
        MedicinePrescriptionSerializer._set_default_fields_on_created_medicine(med_obj)
        return med_obj


# -----------------------------
# Test Prescription Serializer
# -----------------------------
class TestPrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestPrescription
        fields = ["id", "test_name", "instructions"]

    def validate_test_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Test name cannot be blank.")
        return value


# -----------------------------
# Prescription Serializer (nested)
# -----------------------------
class PrescriptionSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor.DoctorName", read_only=True)
    doctor_id = serializers.SerializerMethodField(read_only=True)
    patient_name = serializers.CharField(
        source="consultation.appointment.patient.Patient_name", read_only=True
    )

    medicines = MedicinePrescriptionSerializer(many=True, required=False)
    tests = TestPrescriptionSerializer(many=True, required=False)

    class Meta:
        model = Prescription
        fields = [
            "id",
            "consultation",
            "prescription_date",
            "doctor_name",
            "doctor_id",
            "patient_name",
            "medicines",
            "tests",
        ]
        read_only_fields = ["prescription_date"]

    def get_doctor_id(self, obj):
        doc = getattr(obj, "doctor", None)
        return getattr(doc, "id", None)

    def _create_medicine_entries(self, prescription_obj, medicines_data):
        for med in medicines_data:
            medicine_name = med.pop("medicine_name", None)
            if not medicine_name:
                raise serializers.ValidationError({"medicine_name": "Medicine name is required."})
            # resolve or create medicine
            medicine = MedicinePrescriptionSerializer.get_or_create_medicine_by_name(medicine_name)
            MedicinePrescription.objects.create(prescription=prescription_obj, medicine=medicine, **med)

    def _create_test_entries(self, prescription_obj, tests_data):
        for test in tests_data:
            TestPrescription.objects.create(prescription=prescription_obj, **test)

    @transaction.atomic
    def create(self, validated_data):
        """
        Creates Prescription, and nested MedicinePrescription & TestPrescription records
        in a single atomic transaction.
        """
        medicines_data = validated_data.pop("medicines", [])
        tests_data = validated_data.pop("tests", [])

        prescription_obj = Prescription.objects.create(**validated_data)

        # Create nested items
        self._create_medicine_entries(prescription_obj, medicines_data)
        self._create_test_entries(prescription_obj, tests_data)

        return prescription_obj

    @transaction.atomic
    def update(self, instance, validated_data):
        medicines_data = validated_data.pop("medicines", [])
        tests_data = validated_data.pop("tests", [])

        # Update consultation if provided (doctor still inferred)
        instance.consultation = validated_data.get("consultation", instance.consultation)
        instance.save()

        # Replace medicines if provided
        if medicines_data:
            instance.medicines.all().delete()
            self._create_medicine_entries(instance, medicines_data)

        # Replace tests if provided
        if tests_data:
            instance.tests.all().delete()
            self._create_test_entries(instance, tests_data)

        return instance
