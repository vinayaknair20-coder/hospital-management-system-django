# pharmacist_app/serializers.py - COMPLETE WITH MedicineUpdateSerializer
from rest_framework import serializers
from .models import MedicineCategory, Medicine, MedicineBatch, StockMovement


class MedicineCategorySerializer(serializers.ModelSerializer):
    """Medicine Category Serializer"""
    medicine_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicineCategory
        fields = '__all__'
        read_only_fields = ['category_id']
    
    def get_medicine_count(self, obj):
        """Count medicines in category"""
        return obj.medicines.filter(is_active=True).count()


class MedicineSerializer(serializers.ModelSerializer):
    """Medicine Serializer with computed fields"""
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    added_by_name = serializers.CharField(source='added_by.staff_name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Medicine
        fields = '__all__'
        read_only_fields = ['medicine_id', 'created_at', 'updated_at']
    
    def get_stock_status(self, obj):
        """Return stock status string"""
        if obj.is_expired:
            return 'EXPIRED'
        elif obj.quantity_in_stock == 0:
            return 'OUT_OF_STOCK'
        elif obj.is_low_stock:
            return 'LOW_STOCK'
        return 'IN_STOCK'


class MedicineUpdateSerializer(serializers.ModelSerializer):
    """Medicine Update Serializer"""
    class Meta:
        model = Medicine
        fields = '__all__'
        read_only_fields = ['medicine_id', 'created_at', 'updated_at', 'added_by']


class MedicineListSerializer(serializers.ModelSerializer):
    """Medicine List Serializer (minimal fields)"""
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    
    class Meta:
        model = Medicine
        fields = [
            'medicine_id', 'medicine_name', 'company_name', 'strength',
            'category_name', 'unit_price', 'quantity_in_stock', 'is_active'
        ]


class MedicineBatchSerializer(serializers.ModelSerializer):
    """Medicine Batch Serializer"""
    medicine_name = serializers.CharField(source='medicine.medicine_name', read_only=True)
    
    class Meta:
        model = MedicineBatch
        fields = '__all__'
        read_only_fields = ['batch_id']


class StockMovementSerializer(serializers.ModelSerializer):
    """Stock Movement Serializer"""
    medicine_name = serializers.CharField(source='medicine.medicine_name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.staff_name', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = '__all__'
        read_only_fields = ['movement_id', 'movement_time']


class MedicineDetailSerializer(serializers.ModelSerializer):
    """Medicine Detail Serializer (full details)"""
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    added_by_name = serializers.CharField(source='added_by.staff_name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    stock_status = serializers.SerializerMethodField()
    batches = MedicineBatchSerializer(many=True, read_only=True)
    
    class Meta:
        model = Medicine
        fields = '__all__'
    
    def get_stock_status(self, obj):
        if obj.is_expired:
            return 'EXPIRED'
        elif obj.quantity_in_stock == 0:
            return 'OUT_OF_STOCK'
        elif obj.is_low_stock:
            return 'LOW_STOCK'
        return 'IN_STOCK'
