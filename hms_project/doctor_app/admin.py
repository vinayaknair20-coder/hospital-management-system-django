from django.contrib import admin
from .models import Consultation, Prescription, MedicinePrescription, TestPrescription


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['consultation_id', 'get_patient_name', 'get_doctor_name', 'consultation_date', 'diagnosis']
    list_filter = ['consultation_date']
    search_fields = ['symptoms', 'diagnosis', 'appointment__Patient_id__Patient_name']
    
    def get_patient_name(self, obj):
        return obj.appointment.Patient_id.Patient_name
    get_patient_name.short_description = 'Patient'
    
    def get_doctor_name(self, obj):
        return obj.appointment.doctor_id.staff_name
    get_doctor_name.short_description = 'Doctor'


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_id', 'get_patient_name', 'prescription_date']
    list_filter = ['prescription_date']
    
    def get_patient_name(self, obj):
        return obj.consultation.appointment.Patient_id.Patient_name
    get_patient_name.short_description = 'Patient'


@admin.register(MedicinePrescription)
class MedicinePrescriptionAdmin(admin.ModelAdmin):
    list_display = ['medicine_prescription_id', 'medicine_name', 'dosage', 'quantity']
    search_fields = ['medicine_name']


@admin.register(TestPrescription)
class TestPrescriptionAdmin(admin.ModelAdmin):
    list_display = ['test_prescription_id', 'test_name']
    search_fields = ['test_name']
