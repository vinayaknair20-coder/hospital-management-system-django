# receptionist_app/models.py - COMPLETE PRODUCTION VERSION
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from admin_app.models import Staff


class Patient(models.Model):
    """Patient Management"""
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    )
    
    Patient_id = models.AutoField(primary_key=True)
    Patient_name = models.CharField(max_length=200)
    Date_of_Birth = models.DateField()
    Gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    Blood_Group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    Phone_number = models.CharField(max_length=10)
    Email = models.EmailField(blank=True)
    Address = models.TextField()
    Emergency_Contact = models.CharField(max_length=10)
    Medical_History = models.TextField(blank=True)
    Allergies = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='registered_patients')
    registration_date = models.DateField(default=timezone.now)
    
    def clean(self):
        if self.Phone_number and len(self.Phone_number) != 10:
            raise ValidationError({'Phone_number': 'Must be 10 digits'})
        if self.Emergency_Contact and len(self.Emergency_Contact) != 10:
            raise ValidationError({'Emergency_Contact': 'Must be 10 digits'})
        if self.Date_of_Birth and self.Date_of_Birth >= date.today():
            raise ValidationError({'Date_of_Birth': 'Must be in the past'})
    
    def __str__(self):
        return f"{self.Patient_name} - {self.Patient_id}"
    
    class Meta:
        db_table = 'receptionist_patients'
        ordering = ['Patient_name']
        indexes = [
            models.Index(fields=['Phone_number']),
            models.Index(fields=['is_active']),
        ]


class Appointment(models.Model):
    """Appointment Scheduling"""
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]
    
    appointment_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='appointments', limit_choices_to={'role': 'DOCTOR'})
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    token_number = models.IntegerField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='created_appointments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Appointment #{self.appointment_id} - {self.patient.Patient_name}"
    
    class Meta:
        db_table = 'receptionist_appointments'
        ordering = ['-appointment_date', '-appointment_time']
        unique_together = [['doctor', 'appointment_date', 'token_number']]
        indexes = [
            models.Index(fields=['appointment_date', 'status']),
            models.Index(fields=['doctor', 'appointment_date']),
        ]


class BillGeneration(models.Model):
    """Billing Management"""
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partial'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
        ('INSURANCE', 'Insurance'),
    ]
    
    bill_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bills')
    bill_date = models.DateField(default=timezone.now)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medicine_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lab_test_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    generated_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='generated_bills')
    
    def save(self, *args, **kwargs):
        # Auto-calculate total
        self.total_amount = (
            self.consultation_fee + 
            self.medicine_cost + 
            self.lab_test_cost + 
            self.other_charges - 
            self.discount
        )
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Bill #{self.bill_id} - {self.patient.Patient_name}"
    
    class Meta:
        db_table = 'receptionist_bills'
        ordering = ['-bill_date']
# Add to receptionist_app/models.py

