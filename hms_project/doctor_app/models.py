from django.db import models
from receptionist_app.models import Appointment


class Consultation(models.Model):
    consultation_id = models.AutoField(primary_key=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='consultations')
    consultation_date = models.DateField(auto_now_add=True)
    symptoms = models.CharField(max_length=500)
    diagnosis = models.CharField(max_length=500)
    notes = models.TextField(max_length=1000, blank=True)
    
    def __str__(self):
        return f"Consultation {self.consultation_id} - {self.appointment.Patient_id.Patient_name}"
    
    class Meta:
        db_table = 'doctor_consultation'


class Prescription(models.Model):
    prescription_id = models.AutoField(primary_key=True)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='prescriptions')
    prescription_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Prescription {self.prescription_id}"
    
    class Meta:
        db_table = 'doctor_prescription'


class MedicinePrescription(models.Model):
    medicine_prescription_id = models.AutoField(primary_key=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines')
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    instructions = models.TextField(max_length=500, blank=True)
    
    def __str__(self):
        return f"{self.medicine_name} - {self.dosage}"
    
    class Meta:
        db_table = 'doctor_medicine_prescription'


class TestPrescription(models.Model):
    test_prescription_id = models.AutoField(primary_key=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='tests')
    test_name = models.CharField(max_length=200)
    instructions = models.CharField(max_length=500, null=True, blank=True)
    
    def __str__(self):
        return f"Test: {self.test_name}"
    
    class Meta:
        db_table = 'doctor_test_prescription'
