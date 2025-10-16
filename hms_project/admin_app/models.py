from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from .managers import ClinicUserManager


class Specialization(models.Model):
    specialization_id = models.AutoField(primary_key=True)
    specialization_name = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.specialization_name
    
    class Meta:
        db_table = 'admin_specialization'


class Staff(AbstractBaseUser, PermissionsMixin):
    groups = models.ManyToManyField(
        Group,
        related_name='staff_groups',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='staff_permissions',
        blank=True,
    )
    
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        DOCTOR = 'DOCTOR', 'Doctor'
        RECEPTIONIST = 'RECEPTIONIST', 'Receptionist'
        PHARMACIST = 'PHARMACIST', 'Pharmacist'
        LAB_TECHNICIAN = 'LAB_TECHNICIAN', 'Lab Technician'
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    staff_id = models.AutoField(primary_key=True)
    staff_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=500, blank=True)
    joining_date = models.DateField(default=timezone.now)
    Phone_number = models.CharField(max_length=10)
    Email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Roles.choices)
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = ClinicUserManager()
    
    USERNAME_FIELD = 'Email'
    REQUIRED_FIELDS = ['staff_name', 'role']
    
    def clean(self):
        # Validate phone number
        if self.Phone_number and not self.Phone_number.isdigit():
            raise ValidationError({'Phone_number': 'Phone number must contain only digits'})
        if self.Phone_number and len(self.Phone_number) != 10:
            raise ValidationError({'Phone_number': 'Phone number must be exactly 10 digits'})
        
        # Validate date of birth
        if self.date_of_birth and self.date_of_birth >= date.today():
            raise ValidationError({'date_of_birth': 'Date of birth must be in the past'})
    
    def __str__(self):
        return f"{self.staff_name} ({self.role})"
    
    class Meta:
        db_table = 'admin_staff'
