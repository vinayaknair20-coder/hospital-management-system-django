# doctor_app/models.py - COMPLETE PRODUCTION VERSION
from django.db import models
from django.utils import timezone
from admin_app.models import Staff
from receptionist_app.models import Patient, Appointment


def get_today_date():
    return timezone.now().date()


class Consultation(models.Model):
    """Doctor Consultation Records"""
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    consultation_id = models.AutoField(primary_key=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='consultations')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    doctor = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='consultations', limit_choices_to={'role': 'DOCTOR'})
    consultation_date = models.DateField(default=get_today_date)
    consultation_time = models.TimeField(auto_now_add=True)
    
    # Vital Signs
    blood_pressure = models.CharField(max_length=20, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    pulse_rate = models.IntegerField(blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    # Medical Details
    symptoms = models.TextField()
    diagnosis = models.TextField()
    notes = models.TextField(blank=True)
    follow_up_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Consultation #{self.consultation_id} - {self.patient.Patient_name}"
    
    class Meta:
        db_table = 'doctor_consultations'
        ordering = ['-consultation_date', '-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['doctor', 'consultation_date']),
        ]


class Prescription(models.Model):
    """Prescription for Consultations"""
    
    prescription_id = models.AutoField(primary_key=True)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='prescriptions')
    prescription_date = models.DateField(default=get_today_date)
    general_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prescription #{self.prescription_id} - {self.patient.Patient_name}"
    
    class Meta:
        db_table = 'doctor_prescriptions'
        ordering = ['-prescription_date']


class MedicinePrescription(models.Model):
    """Medicine Details in Prescription"""
    
    FREQUENCY_CHOICES = [
        ('OD', 'Once Daily'),
        ('BD', 'Twice Daily'),
        ('TDS', 'Three Times Daily'),
        ('QID', 'Four Times Daily'),
        ('SOS', 'As Needed'),
    ]
    
    TIMING_CHOICES = [
        ('BEFORE_FOOD', 'Before Food'),
        ('AFTER_FOOD', 'After Food'),
        ('WITH_FOOD', 'With Food'),
        ('EMPTY_STOMACH', 'Empty Stomach'),
    ]
    
    medicine_prescription_id = models.AutoField(primary_key=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines')
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    timing = models.CharField(max_length=20, choices=TIMING_CHOICES, blank=True)
    duration = models.CharField(max_length=100)
    quantity = models.IntegerField(blank=True, null=True)
    instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.medicine_name} - {self.dosage}"
    
    class Meta:
        db_table = 'doctor_medicine_prescriptions'


class TestPrescription(models.Model):
    """Lab Test Details in Prescription"""
    
    test_prescription_id = models.AutoField(primary_key=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='tests')
    test_name = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    
    def __str__(self):
        return self.test_name
    
    class Meta:
        db_table = 'doctor_test_prescriptions'
