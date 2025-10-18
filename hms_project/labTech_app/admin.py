# labTech_app/admin.py - COMPLETE VERSION
from django.contrib import admin
from .models import LabTest, TestResult


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['test_id', 'test_name', 'price', 'sample_type', 'is_active']
    list_filter = ['is_active', 'sample_type']
    search_fields = ['test_name']
    readonly_fields = ['test_id', 'created_at']


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['result_id', 'patient', 'lab_test', 'test_date', 'result_status', 'is_normal']
    list_filter = ['result_status', 'is_normal', 'test_date']
    search_fields = ['patient__Patient_name', 'lab_test__test_name']
    readonly_fields = ['result_id', 'created_at', 'updated_at']
