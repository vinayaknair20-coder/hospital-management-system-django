from django.contrib.auth.models import BaseUserManager


class ClinicUserManager(BaseUserManager):
    def create_user(self, Email, staff_name, role, password=None, **extra_fields):
        """Create and save a regular user"""
        if not Email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(Email)
        user = self.model(Email=email, staff_name=staff_name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, Email, staff_name, role='ADMIN', password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(Email, staff_name, role, password, **extra_fields)
