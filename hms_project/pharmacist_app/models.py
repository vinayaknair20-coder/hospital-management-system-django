from django.db import models
from django.core.exceptions import ValidationError


class Medicine(models.Model):
    medicine_id = models.AutoField(primary_key=True)
    medicine_name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    company_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    
    def clean(self):
        if self.unit_price and self.unit_price < 0:
            raise ValidationError({'unit_price': 'Unit price must be positive'})
        if self.reorder_level and self.reorder_level < 0:
            raise ValidationError({'reorder_level': 'Reorder level must be positive'})
    
    @property
    def needs_reorder(self):
        """Check if medicine needs to be reordered"""
        return self.quantity_in_stock <= self.reorder_level
    
    def __str__(self):
        return f"{self.medicine_name} - {self.company_name}"
    
    class Meta:
        db_table = 'pharmacist_medicine'


class MedicineStock(models.Model):
    stock_id = models.AutoField(primary_key=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='stock_batches')
    batch_number = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()
    received_date = models.DateField(auto_now_add=True)
    
    def clean(self):
        from datetime import date
        if self.expiry_date and self.expiry_date <= date.today():
            raise ValidationError({'expiry_date': 'Expiry date must be in the future'})
    
    @property
    def is_expired(self):
        """Check if medicine batch is expired"""
        from datetime import date
        return self.expiry_date <= date.today()
    
    def __str__(self):
        return f"{self.medicine.medicine_name} - Batch: {self.batch_number}"
    
    class Meta:
        db_table = 'pharmacist_medicine_stock'
