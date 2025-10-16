from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from admin_app.models import Staff


# Create your models here.
class Patient(models.Model):
    Patient_id = models.AutoField(primary_key=True)
    Patient_name = models.CharField(max_length=100)
    Age = models.IntegerField()
    Gender = models.CharField(max_length=20)
    Blood_Group = models.CharField(max_length=5)    
    Address = models.CharField(max_length=200)
    Phone_number = models.CharField(max_length=15)
    Email = models.EmailField(null=True, unique=True)

    def __str__(self):
        return f"{self.Patient_id} - {self.Patient_name}"
    

# Doctor model for receptionist_app
class Doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    staff_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.doctor_id} - {self.staff_name}"
    
class Appointment(models.Model):
    Appointment_id = models.AutoField(primary_key=True)
    Patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor_id = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    Appointment_date = models.DateField()
    Appointment_time = models.TimeField(auto_now_add=True)
    Status_choices = ( ("booked", "booked"), ("cancelled", "cancelled"), ("completed", "completed") )
    status = models.CharField(max_length=20, choices=Status_choices, default="booked")

    def __str__(self):
        return f"Appointment {self.Appointment_id} for Patient {self.Patient_id.Patient_name} with Dr. {self.doctor_id.staff_name} on {self.Appointment_date}"
    
class Bill_Generation(models.Model):
    Bill_id = models.AutoField(primary_key=True)
    Patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE)
    Appointment_id = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Status_choices = ( ("paid", "paid"), ("unpaid", "unpaid") )
    Billing_date = models.DateField(auto_now_add=True)
    Token = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"Bill {self.Bill_id} for Appointment {self.Appointment_id.Appointment_id} - Amount: {self.Amount}"

# Signal to generate Token after Bill_Generation is created
@receiver(post_save, sender=Bill_Generation)
def generate_token(sender, instance, created, **kwargs):
    if created and not instance.Token:
        instance.Token = f"PAT{instance.Bill_id}"
        instance.save(update_fields=["Token"])
