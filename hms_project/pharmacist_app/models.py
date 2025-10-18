# pharmacist_app/models.py - COMPLETE PRODUCTION VERSION
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from admin_app.models import Staff


class MedicineCategory(models.Model):
    """Medicine Categories"""
    
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.category_name
    
    class Meta:
        db_table = 'pharmacist_medicine_categories'
        ordering = ['category_name']
        verbose_name_plural = 'Medicine Categories'


class Medicine(models.Model):
    """Medicine Inventory"""
    
    medicine_id = models.AutoField(primary_key=True)
    medicine_name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(MedicineCategory, on_delete=models.SET_NULL, null=True, related_name='medicines')
    company_name = models.CharField(max_length=200)
    strength = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    expiry_date = models.DateField()
    description = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    added_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='added_medicines')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        if self.expiry_date and self.expiry_date < date.today():
            raise ValidationError({'expiry_date': 'Expiry date cannot be in the past'})
    
    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level
    
    @property
    def is_expired(self):
        return self.expiry_date < date.today()
    
    def __str__(self):
        return f"{self.medicine_name} ({self.strength})"
    
    class Meta:
        db_table = 'pharmacist_medicines'
        ordering = ['medicine_name']
        indexes = [
            models.Index(fields=['medicine_name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['expiry_date']),
        ]


class MedicineBatch(models.Model):
    """Medicine Batch Tracking"""
    
    batch_id = models.AutoField(primary_key=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=50)
    manufacturing_date = models.DateField()
    expiry_date = models.DateField()
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.medicine.medicine_name} - Batch {self.batch_number}"
    
    class Meta:
        db_table = 'pharmacist_medicine_batches'
        ordering = ['-expiry_date']
        unique_together = [['medicine', 'batch_number']]


class StockMovement(models.Model):
    """Track Medicine Stock Changes"""
    
    MOVEMENT_TYPE_CHOICES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('RETURN', 'Return'),
        ('EXPIRED', 'Expired'),
        ('DAMAGED', 'Damaged'),
    ]
    
    movement_id = models.AutoField(primary_key=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.IntegerField()
    movement_date = models.DateField(default=timezone.now)
    movement_time = models.TimeField(auto_now_add=True)
    reason = models.TextField(blank=True)
    performed_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='stock_movements')
    
    def __str__(self):
        return f"{self.movement_type} - {self.medicine.medicine_name}"
    
    class Meta:
        db_table = 'pharmacist_stock_movements'
        ordering = ['-movement_date', '-movement_time']
