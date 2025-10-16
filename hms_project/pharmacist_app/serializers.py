"""
PHARMACIST APP SERIALIZERS
DRF serializers matching the models.py with comprehensive validation
"""

from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Sum
from decimal import Decimal, InvalidOperation
from datetime import timedelta, date
import re
from .models import *


class MedicineCategorySerializer(serializers.ModelSerializer):
    """Medicine category serializer with validation"""
    
    name = serializers.CharField(
        max_length=100,
        min_length=3,
        validators=[
            UniqueValidator(
                queryset=MedicineCategory.objects.all(),
                message="Category with this name already exists."
            )
        ],
        error_messages={
            'required': 'Category name is required.',
            'blank': 'Category name cannot be blank.',
            'min_length': 'Name should have at least three characters.',
            'max_length': 'Category name cannot exceed 100 characters.'
        }
    )
    
    description = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True
    )
    
    # Read-only fields
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = MedicineCategory
        fields = '__all__'
    
    def validate_name(self, value):
        """Validate category name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Category name cannot be empty.")
        
        value = value.strip().title()
        
        # Check reserved names
        reserved = ['admin', 'system', 'test', 'api']
        if value.lower() in reserved:
            raise serializers.ValidationError(f"'{value}' is a reserved name.")
        
        return value
    
    def validate_description(self, value):
        """Validate description"""
        if value and len(value.strip()) > 0:
            if len(value.strip()) < 10:
                raise serializers.ValidationError("Description must be at least 10 characters if provided.")
        
        return value.strip() if value else value


class SupplierSerializer(serializers.ModelSerializer):
    """Supplier serializer with validation"""
    
    name = serializers.CharField(
        max_length=200,
        min_length=3,
        validators=[
            UniqueValidator(
                queryset=Supplier.objects.all(),
                message="Supplier with this name already exists."
            )
        ]
    )
    
    contact_person = serializers.CharField(
        max_length=100,
        min_length=3
    )
    
    phone = serializers.CharField(
        max_length=15,
        validators=[
            UniqueValidator(
                queryset=Supplier.objects.all(),
                message="Supplier with this phone number already exists."
            )
        ]
    )
    
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=Supplier.objects.all(),
                message="Supplier with this email already exists."
            )
        ]
    )
    
    address = serializers.CharField(
        max_length=500,
        min_length=10
    )
    
    # Read-only computed fields
    total_supplies = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = '__all__'
    
    def get_total_supplies(self, obj):
        """Get total number of stock batches from this supplier"""
        return obj.medicinestock_set.count()
    
    def validate_phone(self, value):
        """Validate 10-digit phone number"""
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        
        cleaned = re.sub(r'\D', '', str(value))
        
        if len(cleaned) != 10:
            raise serializers.ValidationError("Phone number should have 10 digits.")
        
        if cleaned[0] == '0':
            raise serializers.ValidationError("Phone number cannot start with 0.")
        
        return cleaned
    
    def validate_contact_person(self, value):
        """Validate contact person name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Contact person name is required.")
        
        value = value.strip()
        
        if len(value) < 3:
            raise serializers.ValidationError("Contact person name must be at least 3 characters.")
        
        if not re.match(r'^[A-Za-z\s\.]+$', value):
            raise serializers.ValidationError("Contact person name can only contain letters, spaces, and periods.")
        
        return value.title()
    
    def validate_name(self, value):
        """Validate supplier name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Supplier name is required.")
        
        return value.strip().title()


class MedicineSerializer(serializers.ModelSerializer):
    """Medicine serializer matching PDF requirements"""
    
    # Core fields from PDF requirements
    medicine_name = serializers.CharField(
        max_length=200,
        min_length=3,
        error_messages={
            'required': 'Medicine name is required.',
            'min_length': 'Name should have at least three characters.',
            'max_length': 'Medicine name cannot exceed 200 characters.'
        }
    )
    
    generic_name = serializers.CharField(
        max_length=200,
        min_length=3,
        required=False,
        allow_blank=True
    )
    
    company_name = serializers.CharField(
        max_length=200,
        min_length=3,
        error_messages={
            'required': 'Company name is required.',
            'min_length': 'Company name should have at least three characters.'
        }
    )
    
    unit_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        error_messages={
            'required': 'Unit price is required.',
            'min_value': 'Price must be greater than zero.',
            'invalid': 'Enter a valid price.'
        }
    )
    
    total_quantity = serializers.IntegerField(
        min_value=0,
        error_messages={
            'min_value': 'Quantity cannot be negative.'
        }
    )
    
    reorder_level = serializers.IntegerField(
        min_value=1,
        max_value=1000,
        default=10
    )
    
    # Read-only fields
    medicine_code = serializers.CharField(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_low_stock = serializers.ReadOnlyField()
    is_out_of_stock = serializers.ReadOnlyField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    # Computed fields
    available_batches = serializers.SerializerMethodField()
    expired_batches = serializers.SerializerMethodField()
    
    class Meta:
        model = Medicine
        fields = '__all__'
        
        validators = [
            UniqueTogetherValidator(
                queryset=Medicine.objects.all(),
                fields=['medicine_name', 'company_name', 'strength'],
                message="Medicine with this combination already exists."
            )
        ]
    
    def get_available_batches(self, obj):
        """Get available stock batches"""
        batches = obj.stock_batches.filter(
            quantity_available__gt=0,
            is_damaged=False,
            expiry_date__gt=timezone.now().date()
        ).values('batch_number', 'quantity_available', 'expiry_date', 'supplier__name')
        return list(batches)
    
    def get_expired_batches(self, obj):
        """Get expired stock batches"""
        return obj.stock_batches.filter(
            expiry_date__lt=timezone.now().date(),
            quantity_available__gt=0
        ).count()
    
    def validate_medicine_name(self, value):
        """Validate medicine name - PDF requirement"""
        if not value or not value.strip():
            raise serializers.ValidationError("Medicine name is required.")
        
        value = value.strip()
        
        if len(value) < 3:
            raise serializers.ValidationError("Name should have at least three characters.")
        
        # Only alphanumeric, spaces, periods, hyphens, parentheses
        if not re.match(r'^[A-Za-z0-9\s\.\-\(\)]+$', value):
            raise serializers.ValidationError("Medicine name contains invalid characters.")
        
        return value.title()
    
    def validate_company_name(self, value):
        """Validate company name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Company name is required.")
        
        value = value.strip()
        
        if len(value) < 3:
            raise serializers.ValidationError("Company name should have at least three characters.")
        
        return value.title()
    
    def validate_generic_name(self, value):
        """Validate generic name if provided"""
        if value and value.strip():
            value = value.strip()
            if len(value) < 3:
                raise serializers.ValidationError("Generic name should have at least three characters.")
            return value.title()
        return value
    
    def validate(self, attrs):
        """Object-level validation"""
        # Validate category is active
        category = attrs.get('category')
        if category and not category.is_active:
            raise serializers.ValidationError({
                'category': 'Cannot assign inactive category to medicine.'
            })
        
        return attrs


class MedicineStockSerializer(serializers.ModelSerializer):
    """Medicine stock serializer with comprehensive validation"""
    
    batch_number = serializers.CharField(
        max_length=50,
        min_length=3,
        error_messages={
            'required': 'Batch number is required.',
            'min_length': 'Batch number must be at least 3 characters.',
            'max_length': 'Batch number cannot exceed 50 characters.'
        }
    )
    
    quantity_received = serializers.IntegerField(
        min_value=1,
        max_value=999999,
        error_messages={
            'required': 'Quantity received is required.',
            'min_value': 'Quantity received must be at least 1.',
            'max_value': 'Quantity received cannot exceed 999,999.'
        }
    )
    
    quantity_available = serializers.IntegerField(
        min_value=0,
        max_value=999999
    )
    
    unit_cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        error_messages={
            'required': 'Unit cost is required.',
            'min_value': 'Unit cost must be greater than 0.'
        }
    )
    
    expiry_date = serializers.DateField(
        error_messages={
            'required': 'Expiry date is required.',
            'invalid': 'Enter a valid expiry date.'
        }
    )
    
    manufacturing_date = serializers.DateField(
        required=False,
        allow_null=True
    )
    
    # Read-only fields
    medicine_name = serializers.CharField(source='medicine.medicine_name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    days_to_expiry = serializers.ReadOnlyField()
    is_expiring_soon = serializers.ReadOnlyField()
    received_date = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = MedicineStock
        fields = '__all__'
        
        validators = [
            UniqueTogetherValidator(
                queryset=MedicineStock.objects.all(),
                fields=['medicine', 'batch_number', 'supplier'],
                message="Stock with this batch number already exists for this medicine from this supplier."
            )
        ]
    
    def validate_batch_number(self, value):
        """Validate batch number format"""
        if not value or not value.strip():
            raise serializers.ValidationError("Batch number is required.")
        
        value = value.strip()
        
        if not re.match(r'^[A-Za-z0-9\-_]+$', value):
            raise serializers.ValidationError("Batch number can only contain letters, numbers, hyphens, and underscores.")
        
        return value.upper()
    
    def validate_expiry_date(self, value):
        """Validate expiry date"""
        if not value:
            raise serializers.ValidationError("Expiry date is required.")
        
        today = timezone.now().date()
        
        if value < today - timedelta(days=30):
            raise serializers.ValidationError("Expiry date cannot be more than 30 days in the past.")
        
        if value > today + timedelta(days=3650):
            raise serializers.ValidationError("Expiry date cannot be more than 10 years in the future.")
        
        return value
    
    def validate_manufacturing_date(self, value):
        """Validate manufacturing date if provided"""
        if value:
            today = timezone.now().date()
            
            if value > today:
                raise serializers.ValidationError("Manufacturing date cannot be in the future.")
            
            if value < today - timedelta(days=3650):
                raise serializers.ValidationError("Manufacturing date cannot be more than 10 years old.")
        
        return value
    
    def validate(self, attrs):
        """Object-level validation"""
        # Validate quantity consistency
        quantity_received = attrs.get('quantity_received')
        quantity_available = attrs.get('quantity_available')
        
        if quantity_available > quantity_received:
            raise serializers.ValidationError({
                'quantity_available': 'Available quantity cannot exceed received quantity.'
            })
        
        # Validate date consistency
        manufacturing_date = attrs.get('manufacturing_date')
        expiry_date = attrs.get('expiry_date')
        
        if manufacturing_date and expiry_date:
            if manufacturing_date >= expiry_date:
                raise serializers.ValidationError({
                    'manufacturing_date': 'Manufacturing date must be before expiry date.'
                })
        
        # Validate supplier and medicine are active
        supplier = attrs.get('supplier')
        if supplier and not supplier.is_active:
            raise serializers.ValidationError({
                'supplier': 'Cannot use inactive supplier.'
            })
        
        medicine = attrs.get('medicine')
        if medicine and not medicine.is_active:
            raise serializers.ValidationError({
                'medicine': 'Cannot add stock for inactive medicine.'
            })
        
        # Validate damage fields
        is_damaged = attrs.get('is_damaged', False)
        damage_notes = attrs.get('damage_notes', '')
        
        if is_damaged and not damage_notes.strip():
            raise serializers.ValidationError({
                'damage_notes': 'Damage notes required when stock is marked as damaged.'
            })
        
        return attrs


class StockAlertSerializer(serializers.ModelSerializer):
    """Stock alert serializer"""
    
    message = serializers.CharField(
        max_length=500,
        min_length=10
    )
    
    # Read-only fields
    medicine_name = serializers.CharField(source='medicine.medicine_name', read_only=True)
    batch_number = serializers.CharField(source='stock_batch.batch_number', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    resolved_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = StockAlert
        fields = '__all__'
        read_only_fields = ['created_at', 'resolved_at']
    
    def validate_message(self, value):
        """Validate alert message"""
        if not value or not value.strip():
            raise serializers.ValidationError("Alert message is required.")
        
        return value.strip()


class PrescriptionItemSerializer(serializers.ModelSerializer):
    """Prescription item serializer"""
    
    quantity_prescribed = serializers.IntegerField(
        min_value=1,
        max_value=9999
    )
    
    quantity_dispensed = serializers.IntegerField(
        min_value=0,
        max_value=9999,
        default=0
    )
    
    unit_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    
    dosage_instructions = serializers.CharField(
        max_length=500,
        min_length=5
    )
    
    # Read-only fields
    medicine_name = serializers.CharField(source='medicine.medicine_name', read_only=True)
    subtotal = serializers.ReadOnlyField()
    is_fully_dispensed = serializers.ReadOnlyField()
    remaining_quantity = serializers.ReadOnlyField()
    
    class Meta:
        model = PrescriptionItem
        fields = '__all__'
        
        validators = [
            UniqueTogetherValidator(
                queryset=PrescriptionItem.objects.all(),
                fields=['prescription', 'medicine'],
                message="This medicine is already prescribed in this prescription."
            )
        ]
    
    def validate_dosage_instructions(self, value):
        """Validate dosage instructions"""
        if not value or not value.strip():
            raise serializers.ValidationError("Dosage instructions are required.")
        
        return value.strip()
    
    def validate(self, attrs):
        """Object-level validation"""
        quantity_prescribed = attrs.get('quantity_prescribed')
        quantity_dispensed = attrs.get('quantity_dispensed', 0)
        
        if quantity_dispensed > quantity_prescribed:
            raise serializers.ValidationError({
                'quantity_dispensed': f'Cannot dispense {quantity_dispensed}. Only {quantity_prescribed} prescribed.'
            })
        
        medicine = attrs.get('medicine')
        if medicine and not medicine.is_active:
            raise serializers.ValidationError({
                'medicine': 'Cannot prescribe inactive medicine.'
            })
        
        return attrs


class PrescriptionSerializer(serializers.ModelSerializer):
    """Prescription serializer"""
    
    patient_name = serializers.CharField(
        max_length=200,
        min_length=3
    )
    
    patient_phone = serializers.CharField(max_length=15)
    
    patient_age = serializers.IntegerField(
        min_value=0,
        max_value=150
    )
    
    doctor_name = serializers.CharField(
        max_length=200,
        min_length=3
    )
    
    # Nested serializer for items
    items = PrescriptionItemSerializer(many=True, read_only=True)
    
    # Read-only fields
    prescription_code = serializers.CharField(read_only=True)
    prescription_date = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Prescription
        fields = '__all__'
    
    def validate_patient_name(self, value):
        """Validate patient name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Patient name is required.")
        
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Name should have at least three characters.")
        
        return value.title()
    
    def validate_doctor_name(self, value):
        """Validate doctor name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Doctor name is required.")
        
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Doctor name should have at least three characters.")
        
        return value.title()
    
    def validate_patient_phone(self, value):
        """Validate patient phone"""
        if not value:
            raise serializers.ValidationError("Patient phone number is required.")
        
        cleaned = re.sub(r'\D', '', str(value))
        
        if len(cleaned) != 10:
            raise serializers.ValidationError("Phone number should have 10 digits.")
        
        if cleaned[0] == '0':
            raise serializers.ValidationError("Phone number cannot start with 0.")
        
        return cleaned


class SaleItemSerializer(serializers.ModelSerializer):
    """Sale item serializer"""
    
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=9999
    )
    
    unit_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    
    # Read-only fields
    medicine_name = serializers.CharField(source='medicine.medicine_name', read_only=True)
    batch_number = serializers.CharField(source='stock_batch.batch_number', read_only=True)
    
    class Meta:
        model = SaleItem
        fields = '__all__'
    
    def validate(self, attrs):
        """Object-level validation"""
        quantity = attrs.get('quantity')
        unit_price = attrs.get('unit_price')
        subtotal = attrs.get('subtotal')
        
        # Validate subtotal calculation
        if quantity and unit_price and subtotal:
            expected_subtotal = quantity * unit_price
            if abs(subtotal - expected_subtotal) > Decimal('0.01'):
                raise serializers.ValidationError({
                    'subtotal': f'Subtotal should be {expected_subtotal}.'
                })
        
        # Validate stock availability
        stock_batch = attrs.get('stock_batch')
        if stock_batch and quantity:
            if quantity > stock_batch.quantity_available:
                raise serializers.ValidationError({
                    'quantity': f'Only {stock_batch.quantity_available} units available.'
                })
            
            if stock_batch.is_expired:
                raise serializers.ValidationError({
                    'stock_batch': 'Cannot sell expired medicine.'
                })
        
        return attrs


class SaleSerializer(serializers.ModelSerializer):
    """Sale serializer"""
    
    customer_name = serializers.CharField(
        max_length=200,
        min_length=3
    )
    
    customer_phone = serializers.CharField(max_length=15)
    
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    
    total_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    
    # Nested serializer for items
    items = SaleItemSerializer(many=True, read_only=True)
    
    # Read-only fields
    sale_code = serializers.CharField(read_only=True)
    sale_date = serializers.DateTimeField(read_only=True)
    pharmacist_name = serializers.CharField(source='pharmacist.get_full_name', read_only=True)
    
    class Meta:
        model = Sale
        fields = '__all__'
    
    def validate_customer_name(self, value):
        """Validate customer name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Customer name is required.")
        
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Name should have at least three characters.")
        
        return value.title()
    
    def validate_customer_phone(self, value):
        """Validate customer phone"""
        if not value:
            raise serializers.ValidationError("Customer phone number is required.")
        
        cleaned = re.sub(r'\D', '', str(value))
        
        if len(cleaned) != 10:
            raise serializers.ValidationError("Phone number should have 10 digits.")
        
        return cleaned
    
    def validate(self, attrs):
        """Object-level validation"""
        # Validate total calculation
        subtotal = attrs.get('subtotal', Decimal('0.00'))
        discount_amount = attrs.get('discount_amount', Decimal('0.00'))
        tax_amount = attrs.get('tax_amount', Decimal('0.00'))
        total_amount = attrs.get('total_amount', Decimal('0.00'))
        
        expected_total = subtotal + tax_amount - discount_amount
        if abs(total_amount - expected_total) > Decimal('0.01'):
            raise serializers.ValidationError({
                'total_amount': f'Total amount should be {expected_total}.'
            })
        
        return attrs


# Utility serializers
class DispenseMedicineSerializer(serializers.Serializer):
    """Serializer for dispensing medicine from prescription"""
    
    prescription_item_id = serializers.IntegerField(min_value=1)
    quantity_to_dispense = serializers.IntegerField(min_value=1, max_value=9999)
    batch_number = serializers.CharField(max_length=50, min_length=3)
    
    def validate_batch_number(self, value):
        """Validate batch number format"""
        if not value or not value.strip():
            raise serializers.ValidationError("Batch number is required.")
        
        value = value.strip()
        
        if not re.match(r'^[A-Za-z0-9\-_]+$', value):
            raise serializers.ValidationError("Batch number format is invalid.")
        
        return value.upper()
    
    def validate(self, attrs):
        """Validate dispensing operation"""
        prescription_item_id = attrs.get('prescription_item_id')
        quantity_to_dispense = attrs.get('quantity_to_dispense')
        batch_number = attrs.get('batch_number')
        
        try:
            prescription_item = PrescriptionItem.objects.get(id=prescription_item_id)
            
            # Check remaining quantity
            remaining = prescription_item.remaining_quantity
            if quantity_to_dispense > remaining:
                raise serializers.ValidationError({
                    'quantity_to_dispense': f'Cannot dispense {quantity_to_dispense}. Only {remaining} remaining.'
                })
            
            # Check stock availability
            try:
                stock = MedicineStock.objects.get(
                    medicine=prescription_item.medicine,
                    batch_number=batch_number,
                    quantity_available__gte=quantity_to_dispense
                )
                
                if stock.is_expired:
                    raise serializers.ValidationError({
                        'batch_number': f'Stock with batch {batch_number} is expired.'
                    })
                    
            except MedicineStock.DoesNotExist:
                raise serializers.ValidationError({
                    'batch_number': f'Insufficient stock for batch {batch_number}.'
                })
                
        except PrescriptionItem.DoesNotExist:
            raise serializers.ValidationError({
                'prescription_item_id': 'Invalid prescription item ID.'
            })
        
        return attrs
