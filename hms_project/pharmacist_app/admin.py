from django.contrib import admin
from .models import Medicine, MedicineStock


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['medicine_id', 'medicine_name', 'company_name', 'unit_price', 
                    'quantity_in_stock', 'reorder_level', 'needs_reorder', 'is_active']
    list_filter = ['is_active', 'company_name']
    search_fields = ['medicine_name', 'generic_name', 'company_name']
    
    def needs_reorder(self, obj):
        return '⚠️ Yes' if obj.needs_reorder else '✓ No'
    needs_reorder.short_description = 'Needs Reorder'


@admin.register(MedicineStock)
class MedicineStockAdmin(admin.ModelAdmin):
    list_display = ['stock_id', 'get_medicine_name', 'batch_number', 'quantity', 
                    'expiry_date', 'is_expired', 'received_date']
    list_filter = ['expiry_date', 'received_date']
    search_fields = ['batch_number', 'medicine__medicine_name']
    
    def get_medicine_name(self, obj):
        return obj.medicine.medicine_name
    get_medicine_name.short_description = 'Medicine'
    
    def is_expired(self, obj):
        return '❌ Expired' if obj.is_expired else '✓ Valid'
    is_expired.short_description = 'Status'
