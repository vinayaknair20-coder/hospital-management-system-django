from django.contrib import admin
from .models import LabTest, TestResult


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['test_id', 'test_name', 'test_cost']
    search_fields = ['test_name']


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['result_id', 'get_patient_name', 'get_test_name', 'test_date', 'status']
    list_filter = ['status', 'test_date']
    
    def get_patient_name(self, obj):
        return obj.patient.Patient_name
    get_patient_name.short_description = 'Patient'
    
    def get_test_name(self, obj):
        return obj.test.test_name
    get_test_name.short_description = 'Test'
