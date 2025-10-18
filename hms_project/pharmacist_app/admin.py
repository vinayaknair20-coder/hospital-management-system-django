# pharmacist_app/admin.py - COMPLETE VERSION
from django.contrib import admin
from .models import MedicineCategory, Medicine, MedicineBatch, StockMovement


@admin.register(MedicineCategory)
class MedicineCategoryAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'category_name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['category_name']


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['medicine_id', 'medicine_name', 'company_name', 'unit_price', 'quantity_in_stock', 'is_active']
    list_filter = ['is_active', 'category', 'expiry_date']
    search_fields = ['medicine_name', 'generic_name', 'company_name']
    readonly_fields = ['medicine_id', 'created_at', 'updated_at']


@admin.register(MedicineBatch)
class MedicineBatchAdmin(admin.ModelAdmin):
    list_display = ['batch_id', 'medicine', 'batch_number', 'expiry_date', 'quantity', 'is_active']
    list_filter = ['is_active', 'expiry_date']
    search_fields = ['batch_number', 'medicine__medicine_name']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['movement_id', 'medicine', 'movement_type', 'quantity', 'movement_date']
    list_filter = ['movement_type', 'movement_date']
    search_fields = ['medicine__medicine_name']
    readonly_fields = ['movement_id', 'movement_time']
