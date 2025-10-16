from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,Group,Permission
from django.forms import ValidationError
from django.utils import timezone
from .managers import ClinicUserManager


class Specialization(models.Model):
    specialization_id = models.AutoField(primary_key=True)
    specialization_name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.specialization_name


class Staff(AbstractBaseUser, PermissionsMixin):
    groups = models.ManyToManyField(
        Group,
        related_name="staff_groups",
        blank=True,
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="staff_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
    )
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        DOCTOR = "DOCTOR", "Doctor"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"
        PHARMACIST = "PHARMACIST", "Pharmacist"
        LAB_TECHNICIAN = "LAB_TECHNICIAN", "Lab Technician"
    staff_id = models.AutoField(primary_key=True)
    staff_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, blank=True, null=True)
    joining_date = models.DateField(default=timezone.now)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Roles.choices)
    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    objects = ClinicUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS =["staff_name", "role"]
    def clean(self):
        """Ensure only one ADMIN exists"""
        if self.role == self.Roles.ADMIN:
            existing_admin = Staff.objects.filter(role=self.Roles.ADMIN).exclude(pk=self.pk)
            if existing_admin.exists():
                raise ValidationError("Only one Administrator is allowed in the system.")

    def __str__(self):
        return f"{self.staff_name} ({self.role})"


class Doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, related_name="doctor_profile")
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    working_hours = models.CharField(max_length=100)  # e.g., "9am - 5pm"
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.staff.staff_name} - {self.specialization}"