from django.db import models

# Create your models here.
from django.db import models
from receptionist_app.models import Appointment
from pharmacist_app.models import pharmacist_medicine
from admin_app.models import Doctor


class Consultation(models.Model):
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="consultations"
    )
    consultation_date = models.DateField(auto_now_add=True)
    symptoms = models.CharField(max_length=100)
    diagnosis = models.CharField(max_length=200)
    notes = models.TextField(max_length=500)

    @property
    def doctor(self):
        """Get the doctor from the appointment"""
        return getattr(self.appointment, "doctor", None)

    def __str__(self):
        patient_name = getattr(self.appointment.patient, "Patient_name", "Unknown")
        doc_name = getattr(self.doctor, "DoctorName", "Unknown")
        return f'{patient_name} - {doc_name} - {self.consultation_date}'


class Prescription(models.Model):
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name="prescriptions"
    )
    prescription_date = models.DateField(auto_now_add=True)

    @property
    def doctor(self):
        """Automatically get the doctor from consultation"""
        return self.consultation.doctor

    def __str__(self):
        doc_name = getattr(self.doctor, "DoctorName", "Unknown")
        return f'Prescription {self.id} on {self.prescription_date} from {doc_name}'


class MedicinePrescription(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='medicines'
    )
    medicine = models.ForeignKey(
        pharmacist_medicine,
        on_delete=models.CASCADE,
        related_name="prescriptions"
    )
    dosage = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.medicine.MedicineName} ({self.dosage}, Qty: {self.quantity})'


class TestPrescription(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="tests"
    )
    test_name = models.CharField(max_length=100)
    instructions = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f'Prescription {self.prescription.id} includes test: {self.test_name}'
