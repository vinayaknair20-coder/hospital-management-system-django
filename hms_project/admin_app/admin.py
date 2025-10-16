from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Staff, Specialization


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['specialization_id', 'specialization_name', 'is_active']
    search_fields = ['specialization_name']
    list_filter = ['is_active']


@admin.register(Staff)
class StaffAdmin(UserAdmin):
    list_display = ['staff_id', 'staff_name', 'Email', 'role', 'Phone_number', 'is_active']
    list_filter = ['role', 'is_active', 'specialization']
    search_fields = ['staff_name', 'Email', 'Phone_number']
    ordering = ['staff_name']
    
    fieldsets = (
        ('Personal Info', {
            'fields': ('staff_name', 'Email', 'gender', 'date_of_birth', 'Phone_number', 'address')
        }),
        ('Work Info', {
            'fields': ('role', 'specialization', 'joining_date', 'salary')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('Email', 'staff_name', 'role', 'password1', 'password2', 'Phone_number'),
        }),
    )
