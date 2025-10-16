import re
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Staff, Doctor, Specialization


# ==============================
# Staff Serializer
# ==============================
class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = [
            "staff_id",
            "staff_name",
            "gender",
            "joining_date",
            "mobile_number",
            "email",
            "role",
            "is_active",
        ]

    def validate_staff_name(self, value):
        """Ensure full name only has letters and spaces."""
        if not re.match(r"^[A-Za-z\s]+$", value):
            raise serializers.ValidationError("Name must contain only letters and spaces.")
        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long.")
        return value.strip()

    def validate_mobile_number(self, value):
        """Validate phone number format (10 digits)."""
        if not re.match(r"^\+?\d{10}$", value):
            raise serializers.ValidationError(
                "Enter a valid phone number with 10 digits (optional leading +)."
            )
        return value

    def validate_email(self, value):
        """Ensure email is unique and contains @ and .com"""
        value = value.lower().strip()
        if "@" not in value or ".com" not in value:
            raise serializers.ValidationError("Email must contain '@' and end with '.com'.")
        if Staff.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_gender(self, value):
        """Ensure gender is one of Male, Female, Other."""
        allowed = ["Male", "Female", "Other"]
        if value not in allowed:
            raise serializers.ValidationError(f"Gender must be one of {allowed}.")
        return value

    def validate_role(self, value):
        """Ensure role is one of the defined choices."""
        allowed_roles = [choice[0] for choice in Staff.Roles.choices]
        if value not in allowed_roles:
            raise serializers.ValidationError(f"Role must be one of {allowed_roles}.")
        return value

    def validate_joining_date(self, value):
        """Ensure joining date is not in the future."""
        if value > timezone.now().date():
            raise serializers.ValidationError("Joining date cannot be in the future.")
        return value


# ==============================
# Specialization Serializer
# ==============================
class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ["specialization_id", "specialization_name"]


# ==============================
# Doctor Serializer
# ==============================
class DoctorSerializer(serializers.ModelSerializer):
    staff_id = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.filter(role=Staff.Roles.DOCTOR),
        source="staff",
        write_only=True,
    )
    specialization_name = serializers.CharField(write_only=True)  # accept name
    specialization = serializers.SerializerMethodField(read_only=True)
    staff = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Doctor
        fields = [
            "doctor_id",
            "staff_id",
            "specialization_name",
            "specialization",
            "staff",
            "consultation_fee",
            "working_hours",
            "is_active",
        ]

    def get_staff(self, obj):
        return {
            "staff_id": obj.staff.pk,
            "staff_name": obj.staff.staff_name,
            "email": obj.staff.email,
        }

    def get_specialization(self, obj):
        if obj.specialization:
            return {
                "specialization_id": obj.specialization.pk,
                "specialization_name": obj.specialization.specialization_name,
            }
        return None

    def create(self, validated_data):
        specialization_name = validated_data.pop("specialization_name")
        specialization, created = Specialization.objects.get_or_create(
            specialization_name=specialization_name
        )
        doctor = Doctor.objects.create(
            specialization=specialization,
            **validated_data
        )
        return doctor


    def validate_consultation_fee(self, value):
        """Ensure consultation fee is between 1 and 1000."""
        if value <= 0 or value > 1000:
            raise serializers.ValidationError("Consultation fee must be between 1 and 1000.")
        return value

    def validate_working_hours(self, value):
        """Basic validation for working hours format (e.g., '9am - 5pm')."""
        if not re.match(r"^\d{1,2}(am|pm)?\s*-\s*\d{1,2}(am|pm)?$", value):
            raise serializers.ValidationError("Working hours must be in format '9am - 5pm'.")
        return value


# ==============================
# Custom Token Serializer
# ==============================
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["staff_id"] = user.pk
        token["role"] = user.role
        token["email"] = user.email
        token["staff_name"] = user.staff_name
        return token

    def validate(self, attrs):
        # Let SimpleJWT handle authentication (uses USERNAME_FIELD=email)
        data = super().validate(attrs)

        # Add user info to response
        data.update({
            "staff_id": self.user.pk,
            "staff_name": self.user.staff_name,
            "email": self.user.email,
            "role": self.user.role,
        })
        return data
    def create(self, validated_data):
        if not validated_data.get("username"):
            # use email prefix as username
            validated_data["username"] = validated_data["email"].split("@")[0]
        return Staff.objects.create_user(**validated_data)
    