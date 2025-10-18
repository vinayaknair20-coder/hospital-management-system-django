# labTech_app/models.py - COMPLETE PRODUCTION VERSION
from django.db import models
from django.utils import timezone
from admin_app.models import Staff
from receptionist_app.models import Patient
from doctor_app.models import Consultation


class LabTest(models.Model):
    """Lab Test Catalog"""
    
    test_id = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    normal_range = models.CharField(max_length=200, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    turnaround_time = models.CharField(max_length=100, blank=True, help_text="e.g., 24 hours")
    sample_type = models.CharField(max_length=100, blank=True, help_text="e.g., Blood, Urine")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.test_name
    
    class Meta:
        db_table = 'labtech_lab_tests'
        ordering = ['test_name']
        indexes = [
            models.Index(fields=['is_active']),
        ]


class TestResult(models.Model):
    """Lab Test Results"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    result_id = models.AutoField(primary_key=True)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='lab_results')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_results')
    lab_test = models.ForeignKey(LabTest, on_delete=models.CASCADE, related_name='results')
    test_date = models.DateField(default=timezone.now)
    result_value = models.TextField(blank=True)
    result_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    remarks = models.TextField(blank=True)
    is_normal = models.BooleanField(default=True)
    performed_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='performed_tests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.lab_test.test_name} - {self.patient.Patient_name}"
    
    class Meta:
        db_table = 'labtech_test_results'
        ordering = ['-test_date']
        indexes = [
            models.Index(fields=['result_status']),
            models.Index(fields=['test_date']),
        ]
