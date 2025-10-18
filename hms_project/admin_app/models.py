# admin_app/models.py - COMPLETE FILE
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from .managers import ClinicUserManager


class Specialization(models.Model):
    """Doctor Specializations"""
    specialization_id = models.AutoField(primary_key=True)
    specialization_name = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.specialization_name
    
    class Meta:
        db_table = 'admin_specialization'
        ordering = ['specialization_name']


class Staff(AbstractBaseUser, PermissionsMixin):
    """Hospital Staff Model with JWT support"""
    
    # Many-to-Many relationships for Django permissions
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
    
    # Role Choices
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        DOCTOR = 'DOCTOR', 'Doctor'
        RECEPTIONIST = 'RECEPTIONIST', 'Receptionist'
        PHARMACIST = 'PHARMACIST', 'Pharmacist'
        LAB_TECHNICIAN = 'LAB_TECHNICIAN', 'Lab Technician'
    
    # Gender Choices
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    # Primary Fields
    staff_id = models.AutoField(primary_key=True)
    staff_name = models.CharField(max_length=200)
    username = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=500, blank=True)
    joining_date = models.DateField(default=timezone.now)
    Phone_number = models.CharField(max_length=10)
    Email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Roles.choices)
    specialization = models.ForeignKey(
        Specialization, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='doctors'
    )
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Security Fields
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    # Custom Manager
    objects = ClinicUserManager()
    
    # Django Authentication Settings
    USERNAME_FIELD = 'Email'
    REQUIRED_FIELDS = ['staff_name', 'role', 'username']
    
    # ✅ CRITICAL: JWT Compatibility Property
    @property
    def id(self):
        """Alias staff_id as id for JWT token generation"""
        return self.staff_id
    
    def is_locked(self):
        """Check if account is currently locked"""
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False
    
    def clean(self):
        """Validate model fields"""
        # Validate username length
        if self.username and len(self.username) < 6:
            raise ValidationError({'username': 'Username must be at least 6 characters'})
        
        # Validate staff name
        if self.staff_name and len(self.staff_name.strip()) < 3:
            raise ValidationError({'staff_name': 'Name must be at least 3 characters'})
        
        # Validate phone number
        if self.Phone_number:
            if not self.Phone_number.isdigit():
                raise ValidationError({'Phone_number': 'Phone number must contain only digits'})
            if len(self.Phone_number) != 10:
                raise ValidationError({'Phone_number': 'Phone number must be exactly 10 digits'})
        
        # Validate date of birth
        if self.date_of_birth and self.date_of_birth >= date.today():
            raise ValidationError({'date_of_birth': 'Date of birth must be in the past'})
        
        # Validate email
        if self.Email and '@' not in self.Email:
            raise ValidationError({'Email': 'Invalid email format'})
    
    def save(self, *args, **kwargs):
        """Override save to run validations"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.staff_name} ({self.role})"
    
    class Meta:
        db_table = 'admin_staff'
        ordering = ['staff_name']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['Email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]


class LoginLog(models.Model):
    """Track all login attempts for security audit"""
    
    LOG_TYPE_CHOICES = [
        ('SUCCESS', 'Successful Login'),
        ('FAILED', 'Failed Login'),
        ('LOCKED', 'Account Locked'),
    ]
    
    log_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    log_type = models.CharField(max_length=10, choices=LOG_TYPE_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    success = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.username} - {self.log_type} at {self.timestamp}"
    
    class Meta:
        db_table = 'admin_login_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['log_type']),
            models.Index(fields=['-timestamp']),
        ]
