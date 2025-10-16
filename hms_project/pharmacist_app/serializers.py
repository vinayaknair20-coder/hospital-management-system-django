from rest_framework import serializers
from .models import Medicine, MedicineStock
from datetime import date


class MedicineSerializer(serializers.ModelSerializer):
    needs_reorder = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Medicine
        fields = '__all__'
        read_only_fields = ['medicine_id']
    
    def validate_medicine_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Medicine name must have at least 3 characters")
        return value.strip()
    
    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Unit price must be positive")
        return value
    
    def validate_quantity_in_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value


class MedicineUpdateSerializer(serializers.ModelSerializer):
    """Only allow editing name and price"""
    class Meta:
        model = Medicine
        fields = ['medicine_name', 'unit_price', 'reorder_level']


class MedicineStockSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.medicine_name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = MedicineStock
        fields = '__all__'
        read_only_fields = ['stock_id', 'received_date']
    
    def validate_expiry_date(self, value):
        if value <= date.today():
            raise serializers.ValidationError("Expiry date must be in the future")
        return value
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value
