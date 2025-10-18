# admin_app/admin.py - COMPLETE VERSION
from django.contrib import admin
from .models import Staff, Specialization, LoginLog


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['specialization_id', 'specialization_name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['specialization_name']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['staff_id', 'staff_name', 'username', 'role', 'Email', 'is_active']
    list_filter = ['role', 'is_active', 'gender']
    search_fields = ['staff_name', 'username', 'Email']
    readonly_fields = ['staff_id', 'failed_login_attempts', 'locked_until']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('staff_id', 'staff_name', 'username', 'password')
        }),
        ('Personal Details', {
            'fields': ('gender', 'date_of_birth', 'address', 'Phone_number', 'Email')
        }),
        ('Employment', {
            'fields': ('role', 'specialization', 'salary', 'joining_date', 'is_active')
        }),
        ('Security', {
            'fields': ('failed_login_attempts', 'locked_until')
        }),
    )


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ['log_id', 'username', 'log_type', 'ip_address', 'timestamp', 'success']
    list_filter = ['log_type', 'success', 'timestamp']
    search_fields = ['username', 'ip_address']
    readonly_fields = ['log_id', 'timestamp']
    date_hierarchy = 'timestamp'
