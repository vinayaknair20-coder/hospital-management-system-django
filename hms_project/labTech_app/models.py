from django.db import models
from django.core.exceptions import ValidationError
from receptionist_app.models import Patient


class LabTest(models.Model):
    test_id = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=200)
    test_description = models.TextField(max_length=500, blank=True)
    low_range = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    high_range = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    unit = models.CharField(max_length=50, default='mg/dL')
    test_cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.low_range and self.high_range and self.low_range >= self.high_range:
            raise ValidationError({'high_range': 'High range must be greater than low range'})
        if self.test_cost and self.test_cost < 0:
            raise ValidationError({'test_cost': 'Test cost must be positive'})
    
    def __str__(self):
        return self.test_name
    
    class Meta:
        db_table = 'labtech_labtest'


class TestResult(models.Model):
    result_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_results')
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE)
    test_date = models.DateField(auto_now_add=True)
    result_value = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.TextField(max_length=500, blank=True)
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    @property
    def is_normal(self):
        """Check if result is within normal range"""
        if self.result_value and self.test.low_range and self.test.high_range:
            return self.test.low_range <= self.result_value <= self.test.high_range
        return None
    
    def __str__(self):
        return f"{self.test.test_name} - {self.patient.Patient_name}"
    
    class Meta:
        db_table = 'labtech_testresult'
