"""
PHARMACIST APP ADMIN
Django admin configuration with comprehensive functionality
"""

from django.contrib import admin
from django.db.models import Sum, Count, Q
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import csv

from .models import *
from .utils import generate_stock_alerts


@admin.register(MedicineCategory)
class MedicineCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'medicine_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    def medicine_count(self, obj):
        count = obj.medicine_set.filter(is_active=True).count()
        return format_html(f'<strong>{count}</strong>')
    medicine_count.short_description = 'Active Medicines'
    
    actions = ['activate_categories', 'deactivate_categories']
    
    def activate_categories(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} categories activated.')
    activate_categories.short_description = 'Activate selected categories'
    
    def deactivate_categories(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} categories deactivated.')
    deactivate_categories.short_description = 'Deactivate selected categories'


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email', 'supplies_count', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'contact_person', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'contact_person', 'is_active')
        }),
        ('Contact Details', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def supplies_count(self, obj):
        count = obj.medicinestock_set.count()
        return format_html(f'<strong>{count}</strong>')
    supplies_count.short_description = 'Total Supplies'


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = [
        'medicine_code', 'medicine_name', 'company_name', 'category', 
        'unit_price', 'total_quantity', 'stock_status', 'is_active'
    ]
    list_filter = [
        'category', 'dosage_form', 'is_prescription_required', 
        'is_active', 'created_at'
    ]
    search_fields = [
        'medicine_code', 'medicine_name', 'generic_name', 'company_name'
    ]
    readonly_fields = ['medicine_code', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'medicine_code', 'medicine_name', 'generic_name', 
                'company_name', 'category'
            )
        }),
        ('Details', {
            'fields': (
                'dosage_form', 'strength', 'is_prescription_required'
            )
        }),
        ('Stock & Pricing', {
            'fields': (
                'unit_price', 'total_quantity', 'reorder_level'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def stock_status(self, obj):
        if obj.is_out_of_stock:
            return format_html('<span style="color: red; font-weight: bold;">OUT OF STOCK</span>')
        elif obj.is_low_stock:
            return format_html('<span style="color: orange; font-weight: bold;">LOW STOCK</span>')
        else:
            return format_html('<span style="color: green;">Normal</span>')
    stock_status.short_description = 'Stock Status'
    
    actions = ['activate_medicines', 'deactivate_medicines', 'generate_stock_report']
    
    def activate_medicines(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} medicines activated.')
    activate_medicines.short_description = 'Activate selected medicines'
    
    def deactivate_medicines(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} medicines deactivated.')
    deactivate_medicines.short_description = 'Deactivate selected medicines'
    
    def generate_stock_report(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="medicines_stock_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Medicine Code', 'Medicine Name', 'Company', 'Category',
            'Unit Price', 'Total Quantity', 'Reorder Level', 'Status'
        ])
        
        for medicine in queryset:
            status = 'Out of Stock' if medicine.is_out_of_stock else 'Low Stock' if medicine.is_low_stock else 'Normal'
            writer.writerow([
                medicine.medicine_code, medicine.medicine_name, medicine.company_name,
                medicine.category.name, medicine.unit_price, medicine.total_quantity,
                medicine.reorder_level, status
            ])
        
        return response
    generate_stock_report.short_description = 'Export stock report (CSV)'


@admin.register(MedicineStock)
class MedicineStockAdmin(admin.ModelAdmin):
    list_display = [
        'medicine_name', 'batch_number', 'supplier_name', 
        'quantity_available', 'expiry_date', 'expiry_status', 'is_damaged'
    ]
    list_filter = [
        'supplier', 'is_damaged', 'received_date', 
        ('expiry_date', admin.DateFieldListFilter)
    ]
    search_fields = [
        'medicine__medicine_name', 'batch_number', 'supplier__name'
    ]
    readonly_fields = ['received_date']
    
    fieldsets = (
        ('Medicine & Supplier', {
            'fields': ('medicine', 'supplier')
        }),
        ('Batch Information', {
            'fields': (
                'batch_number', 'quantity_received', 'quantity_available',
                'unit_cost', 'manufacturing_date', 'expiry_date'
            )
        }),
        ('Status', {
            'fields': ('is_damaged', 'damage_notes')
        }),
        ('Timestamps', {
            'fields': ('received_date',),
            'classes': ('collapse',)
        })
    )
    
    def medicine_name(self, obj):
        return obj.medicine.medicine_name
    medicine_name.short_description = 'Medicine'
    
    def supplier_name(self, obj):
        return obj.supplier.name
    supplier_name.short_description = 'Supplier'
    
    def expiry_status(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red; font-weight: bold;">EXPIRED</span>')
        elif obj.is_expiring_soon:
            return format_html('<span style="color: orange; font-weight: bold;">EXPIRING SOON</span>')
        else:
            return format_html('<span style="color: green;">Valid</span>')
    expiry_status.short_description = 'Expiry Status'
    
    actions = ['mark_as_damaged', 'export_expiry_report']
    
    def mark_as_damaged(self, request, queryset):
        count = queryset.update(is_damaged=True)
        self.message_user(request, f'{count} stock batches marked as damaged.')
    mark_as_damaged.short_description = 'Mark selected batches as damaged'


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = [
        'medicine_name', 'alert_type', 'message_preview', 
        'is_resolved', 'created_at'
    ]
    list_filter = ['alert_type', 'is_resolved', 'created_at']
    search_fields = ['medicine__medicine_name', 'message']
    readonly_fields = ['created_at']
    
    def medicine_name(self, obj):
        return obj.medicine.medicine_name
    medicine_name.short_description = 'Medicine'
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
    
    actions = ['resolve_alerts', 'generate_alerts']
    
    def resolve_alerts(self, request, queryset):
        count = queryset.update(
            is_resolved=True, 
            resolved_at=timezone.now(),
            resolved_by=request.user
        )
        self.message_user(request, f'{count} alerts resolved.')
    resolve_alerts.short_description = 'Resolve selected alerts'
    
    def generate_alerts(self, request, queryset):
        result = generate_stock_alerts()
        if result['success']:
            self.message_user(request, f"Generated {result['alerts_created']} new alerts.")
        else:
            self.message_user(request, f"Error generating alerts: {result['error']}", level='ERROR')
    generate_alerts.short_description = 'Generate stock alerts'


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = [
        'prescription_code', 'patient_name', 'doctor_name', 
        'patient_age', 'status', 'total_amount', 'prescription_date'
    ]
    list_filter = ['status', 'prescription_date', 'patient_age']
    search_fields = [
        'prescription_code', 'patient_name', 'doctor_name', 'patient_phone'
    ]
    readonly_fields = ['prescription_code', 'prescription_date']
    
    fieldsets = (
        ('Prescription Details', {
            'fields': ('prescription_code', 'status')
        }),
        ('Patient Information', {
            'fields': ('patient_name', 'patient_phone', 'patient_age')
        }),
        ('Doctor Information', {
            'fields': ('doctor_name',)
        }),
        ('Financial', {
            'fields': ('total_amount',)
        }),
        ('Timestamps', {
            'fields': ('prescription_date',),
            'classes': ('collapse',)
        })
    )
    
    inlines = []  # Could add PrescriptionItemInline here


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = [
        'sale_code', 'customer_name', 'pharmacist_name', 
        'total_amount', 'payment_method', 'is_completed', 'sale_date'
    ]
    list_filter = ['payment_method', 'is_completed', 'sale_date']
    search_fields = ['sale_code', 'customer_name', 'customer_phone']
    readonly_fields = ['sale_code', 'sale_date']
    
    def pharmacist_name(self, obj):
        return obj.pharmacist.get_full_name() or obj.pharmacist.username
    pharmacist_name.short_description = 'Pharmacist'
    
    fieldsets = (
        ('Sale Information', {
            'fields': ('sale_code', 'prescription', 'pharmacist')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_phone')
        }),
        ('Financial Details', {
            'fields': (
                'subtotal', 'discount_amount', 'tax_amount', 
                'total_amount', 'payment_method'
            )
        }),
        ('Status', {
            'fields': ('is_completed',)
        }),
        ('Timestamps', {
            'fields': ('sale_date',),
            'classes': ('collapse',)
        })
    )


# Custom admin views
class PharmacyDashboard(admin.AdminSite):
    site_header = 'Pharmacy Management System'
    site_title = 'Pharmacy Admin'
    index_title = 'Pharmacy Dashboard'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='pharmacy-dashboard'),
            path('generate-alerts/', self.admin_view(self.generate_alerts_view), name='generate-alerts'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        """Custom dashboard view"""
        context = {
            'title': 'Pharmacy Dashboard',
            'medicines_count': Medicine.objects.filter(is_active=True).count(),
            'low_stock_count': Medicine.objects.filter(
                is_active=True, 
                total_quantity__lte=F('reorder_level')
            ).count(),
            'active_alerts': StockAlert.objects.filter(is_resolved=False).count(),
            'today_sales': Sale.objects.filter(
                sale_date__date=timezone.now().date()
            ).count(),
        }
        return render(request, 'admin/pharmacy_dashboard.html', context)
    
    def generate_alerts_view(self, request):
        """Generate stock alerts view"""
        if request.method == 'POST':
            result = generate_stock_alerts()
            context = {
                'title': 'Generate Stock Alerts',
                'result': result
            }
        else:
            context = {'title': 'Generate Stock Alerts'}
        
        return render(request, 'admin/generate_alerts.html', context)


# Register custom admin site
pharmacy_admin = PharmacyDashboard(name='pharmacy_admin')

# Register all models with custom admin site
pharmacy_admin.register(MedicineCategory, MedicineCategoryAdmin)
pharmacy_admin.register(Supplier, SupplierAdmin)
pharmacy_admin.register(Medicine, MedicineAdmin)
pharmacy_admin.register(MedicineStock, MedicineStockAdmin)
pharmacy_admin.register(StockAlert, StockAlertAdmin)
pharmacy_admin.register(Prescription, PrescriptionAdmin)
pharmacy_admin.register(Sale, SaleAdmin)
