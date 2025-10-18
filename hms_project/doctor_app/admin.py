# doctor_app/admin.py - COMPLETE VERSION
from django.contrib import admin
from .models import Consultation, Prescription, MedicinePrescription, TestPrescription


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['consultation_id', 'patient', 'doctor', 'consultation_date', 'status']
    list_filter = ['status', 'consultation_date']
    search_fields = ['patient__Patient_name', 'doctor__staff_name']
    readonly_fields = ['consultation_id', 'created_at', 'updated_at']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_id', 'patient', 'doctor', 'prescription_date']
    list_filter = ['prescription_date']
    search_fields = ['patient__Patient_name', 'doctor__staff_name']
    readonly_fields = ['prescription_id', 'created_at']


@admin.register(MedicinePrescription)
class MedicinePrescriptionAdmin(admin.ModelAdmin):
    list_display = ['medicine_prescription_id', 'prescription', 'medicine_name', 'dosage', 'frequency']
    list_filter = ['frequency', 'timing']
    search_fields = ['medicine_name']


@admin.register(TestPrescription)
class TestPrescriptionAdmin(admin.ModelAdmin):
    list_display = ['test_prescription_id', 'prescription', 'test_name']
    search_fields = ['test_name']
