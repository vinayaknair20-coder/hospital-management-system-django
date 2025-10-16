from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from admin_app.models import Staff
from datetime import date

# Create your models here.

class Patient(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    Patient_id = models.AutoField(primary_key=True)
    Patient_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    Gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    Blood_Group = models.CharField(max_length=5)
    Address = models.CharField(max_length=200)
    Phone_number = models.CharField(max_length=10)
    Email = models.EmailField(null=True, blank=True, unique=True)
    is_active = models.BooleanField(default=True)

    def clean(self):
        # Validate phone number
        if self.Phone_number and not self.Phone_number.isdigit():
            raise ValidationError({'Phone_number': 'Phone number must contain only digits'})
        if self.Phone_number and len(self.Phone_number) != 10:
            raise ValidationError({'Phone_number': 'Phone number must be exactly 10 digits'})
        
        # Validate DOB
        if self.date_of_birth and self.date_of_birth >= date.today():
            raise ValidationError({'date_of_birth': 'Date of birth must be in the past'})
    
    @property
    def Age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    def __str__(self):
        return f"{self.Patient_id} - {self.Patient_name}"
    
    class Meta:
        db_table = 'receptionist_patient'


class Appointment(models.Model):
    Appointment_id = models.AutoField(primary_key=True)
    Patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor_id = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='doctor_appointments')
    Appointment_date = models.DateField()
    Appointment_time = models.TimeField(auto_now_add=True)
    
    Status_choices = (
        ("booked", "Booked"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed")
    )
    status = models.CharField(max_length=20, choices=Status_choices, default="booked")

    def __str__(self):
        return f"Appointment {self.Appointment_id} - {self.Patient_id.Patient_name}"
    
    class Meta:
        db_table = 'receptionist_appointment'


class Bill_Generation(models.Model):
    Bill_id = models.AutoField(primary_key=True)
    Patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bills')
    Appointment_id = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='bills')
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Billing_date = models.DateField(auto_now_add=True)
    Token = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return f"Bill {self.Bill_id} - Token: {self.Token}"
    
    class Meta:
        db_table = 'receptionist_bill_generation'


# SIGNAL: Auto-generate Token after Bill is created
@receiver(post_save, sender=Bill_Generation)
def auto_generate_token(sender, instance, created, **kwargs):
    """Automatically generate token when bill is created"""
    if created and not instance.Token:
        token = f"PAT{instance.Bill_id:06d}-{instance.Patient_id.Patient_id:04d}"
        Bill_Generation.objects.filter(pk=instance.pk).update(Token=token)
        instance.Token = token
        print(f"✅ Token generated: {token} for Patient: {instance.Patient_id.Patient_name}")
