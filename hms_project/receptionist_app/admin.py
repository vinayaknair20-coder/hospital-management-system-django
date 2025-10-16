from django.contrib import admin
from .models import Patient, Appointment, Bill_Generation


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['Patient_id', 'Patient_name', 'Age', 'Gender', 'Blood_Group', 'Phone_number']
    search_fields = ['Patient_name', 'Phone_number', 'Email']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['Appointment_id', 'get_patient_name', 'get_doctor_name', 'Appointment_date', 'status']
    list_filter = ['status', 'Appointment_date']
    
    def get_patient_name(self, obj):
        return obj.Patient_id.Patient_name
    get_patient_name.short_description = 'Patient'
    
    def get_doctor_name(self, obj):
        return obj.doctor_id.staff_name
    get_doctor_name.short_description = 'Doctor'


@admin.register(Bill_Generation)
class BillGenerationAdmin(admin.ModelAdmin):
    list_display = ['Bill_id', 'Token', 'get_patient_name', 'Amount', 'Billing_date']
    readonly_fields = ['Token', 'Billing_date']
    
    def get_patient_name(self, obj):
        return obj.Patient_id.Patient_name
    get_patient_name.short_description = 'Patient'
