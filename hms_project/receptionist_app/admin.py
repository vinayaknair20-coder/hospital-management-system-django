# receptionist_app/admin.py - COMPLETE FIXED VERSION
from django.contrib import admin
from .models import Patient, Appointment, BillGeneration


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['Patient_id', 'Patient_name', 'Phone_number', 'Gender', 'is_active']
    list_filter = ['is_active', 'Gender', 'Blood_Group']
    search_fields = ['Patient_name', 'Phone_number', 'Email']
    readonly_fields = ['Patient_id', 'registration_date']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'patient', 'doctor', 'appointment_date', 'appointment_time', 'status']
    list_filter = ['status', 'appointment_date']
    search_fields = ['patient__Patient_name', 'doctor__staff_name']
    readonly_fields = ['appointment_id', 'created_at']


@admin.register(BillGeneration)
class BillGenerationAdmin(admin.ModelAdmin):
    list_display = ['bill_id', 'patient', 'bill_date', 'total_amount', 'payment_status']
    list_filter = ['payment_status', 'bill_date']
    search_fields = ['patient__Patient_name']
    readonly_fields = ['bill_id', 'total_amount']
