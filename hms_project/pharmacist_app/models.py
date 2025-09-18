"""
PHARMACIST APP MODELS
Comprehensive Django models for pharmacy management system with extensive validation
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (
    MinValueValidator, MaxValueValidator, RegexValidator, 
    EmailValidator, MinLengthValidator, MaxLengthValidator
)
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal, InvalidOperation
import re


# ===========================
# CUSTOM VALIDATORS
# ===========================

def validate_phone_number(value):
    """Validates 10-digit phone number as per PDF requirements"""
    if not value:
        raise ValidationError("Phone number is required.")
    
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', str(value))
    
    # Must be exactly 10 digits as per PDF requirements
    if len(cleaned) != 10:
        raise ValidationError("Phone number should have 10 digits.")
    
    # First digit cannot be 0
    if cleaned[0] == '0':
        raise ValidationError("Phone number cannot start with 0.")
    
    return cleaned


def validate_medicine_name(value):
    """Validates medicine name - minimum 3 characters as per PDF"""
    if not value or not str(value).strip():
        raise ValidationError("Medicine name is required.")
    
    cleaned_name = str(value).strip()
    
    # Minimum 3 characters as per PDF requirement
    if len(cleaned_name) < 3:
        raise ValidationError("Name should have at least three characters.")
    
    # Maximum reasonable length
    if len(cleaned_name) > 200:
        raise ValidationError("Medicine name cannot exceed 200 characters.")
    
    # Only letters, numbers, spaces, hyphens, periods allowed
    if not re.match(r'^[A-Za-z0-9\s\.\-\(\)]+$', cleaned_name):
        raise ValidationError("Medicine name can only contain letters, numbers, spaces, periods, hyphens, and parentheses.")
    
    return cleaned_name.title()


def validate_generic_name(value):
    """Validates generic name"""
    if value and str(value).strip():
        cleaned = str(value).strip()
        if len(cleaned) < 3:
            raise ValidationError("Generic name should have at least three characters.")
        if len(cleaned) > 200:
            raise ValidationError("Generic name cannot exceed 200 characters.")
        return cleaned.title()
    return value


def validate_company_name(value):
    """Validates company/manufacturer name"""
    if not value or not str(value).strip():
        raise ValidationError("Company name is required.")
    
    cleaned = str(value).strip()
    
    if len(cleaned) < 3:
        raise ValidationError("Company name should have at least three characters.")
    
    if len(cleaned) > 200:
        raise ValidationError("Company name cannot exceed 200 characters.")
    
    return cleaned.title()


def validate_positive_quantity(value):
    """Validates positive quantity values"""
    try:
        quantity = int(value)
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        if quantity > 999999:
            raise ValidationError("Quantity cannot exceed 999,999.")
        return quantity
    except (ValueError, TypeError):
        raise ValidationError("Quantity must be a valid number.")


def validate_positive_price(value):
    """Validates positive price values"""
    try:
        price = Decimal(str(value))
        if price <= 0:
            raise ValidationError("Price must be greater than zero.")
        if price > Decimal('999999.99'):
            raise ValidationError("Price cannot exceed 999,999.99.")
        return price
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError("Price must be a valid decimal number.")


def validate_batch_number(value):
    """Validates batch/lot number format"""
    if not value or not str(value).strip():
        raise ValidationError("Batch number is required.")
    
    cleaned = str(value).strip()
    
    if len(cleaned) < 3:
        raise ValidationError("Batch number must be at least 3 characters.")
    
    if len(cleaned) > 50:
        raise ValidationError("Batch number cannot exceed 50 characters.")
    
    # Alphanumeric, hyphens, underscores only
    if not re.match(r'^[A-Za-z0-9\-_]+$', cleaned):
        raise ValidationError("Batch number can only contain letters, numbers, hyphens, and underscores.")
    
    return cleaned.upper()


def validate_expiry_date(value):
    """Validates medicine expiry date"""
    if not value:
        raise ValidationError("Expiry date is required.")
    
    if not isinstance(value, date):
        raise ValidationError("Invalid date format.")
    
    today = timezone.now().date()
    
    # Cannot be too old
    if value < today - timedelta(days=30):
        raise ValidationError("Expiry date cannot be more than 30 days in the past.")
    
    # Cannot be too far in future
    if value > today + timedelta(days=3650):  # 10 years
        raise ValidationError("Expiry date cannot be more than 10 years in the future.")
    
    return value


# ===========================
# MAIN MODELS
# ===========================

class MedicineCategory(models.Model):
    """Medicine categories for organization"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[validate_medicine_name],
        help_text="Category name (minimum 3 characters)"
    )
    
    description = models.TextField(
        max_length=500,
        blank=True,
        help_text="Optional category description"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Is this category active?"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Medicine Categories"
        ordering = ['name']
        db_table = 'pharmacist_medicine_category'
    
    def clean(self):
        """Model-level validation"""
        super().clean()
        
        if self.name:
            self.name = self.name.strip().title()
            
            # Check for reserved names
            reserved_names = ['admin', 'system', 'test', 'api']
            if self.name.lower() in reserved_names:
                raise ValidationError({
                    'name': f"'{self.name}' is a reserved name and cannot be used."
                })
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Medicine suppliers/vendors"""
    
    name = models.CharField(
        max_length=200,
        unique=True,
        validators=[validate_company_name],
        help_text="Supplier company name"
    )
    
    contact_person = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(3, "Contact person name must be at least 3 characters."),
            RegexValidator(
                regex=r'^[A-Za-z\s\.]+$',
                message="Contact person name can only contain letters, spaces, and periods."
            )
        ],
        help_text="Primary contact person"
    )
    
    phone = models.CharField(
        max_length=15,
        unique=True,
        validators=[validate_phone_number],
        help_text="10-digit contact number"
    )
    
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(message="Enter a valid email address.")],
        help_text="Contact email address"
    )
    
    address = models.TextField(
        max_length=500,
        validators=[
            MinLengthValidator(10, "Address must be at least 10 characters.")
        ],
        help_text="Complete business address"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Is this supplier active?"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        db_table = 'pharmacist_supplier'
    
    def clean(self):
        """Model-level validation"""
        super().clean()
        
        if self.name:
            self.name = self.name.strip().title()
        
        if self.contact_person:
            self.contact_person = self.contact_person.strip().title()
        
        if self.email:
            self.email = self.email.lower().strip()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.contact_person}"


class Medicine(models.Model):
    """
    Core Medicine model based on PDF requirements:
    - Medicine Name, Generic Name, Company Name, Quantity, Price
    - Search by Medicine Code and Medicine Name
    - Edit only Quantity and Price
    """
    
    # Auto-generated medicine code (as per PDF search requirement)
    medicine_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Auto-generated medicine code"
    )
    
    # Core fields from PDF
    medicine_name = models.CharField(
        max_length=200,
        validators=[validate_medicine_name],
        help_text="Brand name of medicine (minimum 3 characters)",
        db_index=True  # For search optimization
    )
    
    generic_name = models.CharField(
        max_length=200,
        validators=[validate_generic_name],
        blank=True,
        help_text="Generic/chemical name"
    )
    
    company_name = models.CharField(
        max_length=200,
        validators=[validate_company_name],
        help_text="Manufacturing company name"
    )
    
    # Enhanced fields for modern pharmacy
    category = models.ForeignKey(
        MedicineCategory,
        on_delete=models.PROTECT,
        help_text="Medicine category"
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validate_positive_price],
        help_text="Price per unit"
    )
    
    # Stock tracking
    total_quantity = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total quantity in stock (sum of all batches)"
    )
    
    reorder_level = models.PositiveIntegerField(
        default=10,
        validators=[
            MinValueValidator(1, "Reorder level must be at least 1."),
            MaxValueValidator(1000, "Reorder level cannot exceed 1000.")
        ],
        help_text="Minimum stock level before reorder alert"
    )
    
    # Medicine details
    dosage_form = models.CharField(
        max_length=50,
        choices=[
            ('TABLET', 'Tablet'),
            ('CAPSULE', 'Capsule'),
            ('SYRUP', 'Syrup'),
            ('INJECTION', 'Injection'),
            ('CREAM', 'Cream'),
            ('DROPS', 'Drops'),
            ('INHALER', 'Inhaler'),
            ('OINTMENT', 'Ointment'),
        ],
        default='TABLET',
        help_text="Medicine form/type"
    )
    
    strength = models.CharField(
        max_length=50,
        blank=True,
        help_text="Medicine strength (e.g., 500mg, 10ml)"
    )
    
    is_prescription_required = models.BooleanField(
        default=True,
        help_text="Is prescription required?"
    )
    
    # Status fields
    is_active = models.BooleanField(
        default=True,
        help_text="Is medicine active? (as per PDF disable functionality)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['medicine_name']
        db_table = 'pharmacist_medicine'
        
        # Ensure unique combination
        constraints = [
            models.UniqueConstraint(
                fields=['medicine_name', 'company_name', 'strength'],
                name='unique_medicine_combination'
            ),
            models.CheckConstraint(
                check=models.Q(unit_price__gt=0),
                name='positive_unit_price'
            ),
            models.CheckConstraint(
                check=models.Q(total_quantity__gte=0),
                name='non_negative_quantity'
            )
        ]
    
    def clean(self):
        """Comprehensive model validation"""
        super().clean()
        
        # Normalize names
        if self.medicine_name:
            self.medicine_name = validate_medicine_name(self.medicine_name)
        
        if self.generic_name:
            self.generic_name = validate_generic_name(self.generic_name)
        
        if self.company_name:
            self.company_name = validate_company_name(self.company_name)
        
        # Check for duplicate combinations
        existing = Medicine.objects.filter(
            medicine_name__iexact=self.medicine_name,
            company_name__iexact=self.company_name,
            strength__iexact=self.strength or ''
        ).exclude(pk=self.pk)
        
        if existing.exists():
            raise ValidationError(
                "Medicine with this name, company, and strength already exists."
            )
        
        # Validate category is active
        if self.category and not self.category.is_active:
            raise ValidationError({
                'category': "Cannot assign inactive category to medicine."
            })
    
    def save(self, *args, **kwargs):
        """Auto-generate medicine code and validate"""
        if not self.medicine_code:
            # Auto-generate medicine code (MED + 6 digits)
            last_medicine = Medicine.objects.order_by('id').last()
            if last_medicine:
                next_id = last_medicine.id + 1
            else:
                next_id = 1
            self.medicine_code = f"MED{str(next_id).zfill(6)}"
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_low_stock(self):
        """Check if medicine is below reorder level"""
        return self.total_quantity <= self.reorder_level
    
    @property
    def is_out_of_stock(self):
        """Check if medicine is out of stock"""
        return self.total_quantity == 0
    
    def __str__(self):
        return f"{self.medicine_name} - {self.company_name}"


class MedicineStock(models.Model):
    """
    Individual stock batches with expiry tracking
    Links to Medicine model for inventory management
    """
    
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name='stock_batches',
        help_text="Associated medicine"
    )
    
    batch_number = models.CharField(
        max_length=50,
        validators=[validate_batch_number],
        help_text="Batch/lot number"
    )
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        help_text="Medicine supplier"
    )
    
    quantity_received = models.PositiveIntegerField(
        validators=[validate_positive_quantity],
        help_text="Initial quantity received"
    )
    
    quantity_available = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        help_text="Current available quantity"
    )
    
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validate_positive_price],
        help_text="Cost price per unit"
    )
    
    expiry_date = models.DateField(
        validators=[validate_expiry_date],
        help_text="Medicine expiry date"
    )
    
    manufacturing_date = models.DateField(
        null=True,
        blank=True,
        help_text="Manufacturing date"
    )
    
    received_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date when stock was received"
    )
    
    # Status fields
    is_damaged = models.BooleanField(
        default=False,
        help_text="Is this batch damaged?"
    )
    
    damage_notes = models.TextField(
        max_length=500,
        blank=True,
        help_text="Notes about damage (if any)"
    )
    
    class Meta:
        ordering = ['expiry_date', 'batch_number']
        db_table = 'pharmacist_medicine_stock'
        
        constraints = [
            models.UniqueConstraint(
                fields=['medicine', 'batch_number', 'supplier'],
                name='unique_batch_per_supplier'
            ),
            models.CheckConstraint(
                check=models.Q(quantity_available__lte=models.F('quantity_received')),
                name='available_lte_received'
            ),
            models.CheckConstraint(
                check=models.Q(unit_cost__gt=0),
                name='positive_unit_cost'
            )
        ]
    
    def clean(self):
        """Comprehensive stock validation"""
        super().clean()
        
        # Validate batch number
        if self.batch_number:
            self.batch_number = validate_batch_number(self.batch_number)
        
        # Validate quantity consistency
        if self.quantity_available > self.quantity_received:
            raise ValidationError({
                'quantity_available': "Available quantity cannot exceed received quantity."
            })
        
        # Validate date consistency
        if self.manufacturing_date and self.expiry_date:
            if self.manufacturing_date >= self.expiry_date:
                raise ValidationError({
                    'manufacturing_date': "Manufacturing date must be before expiry date."
                })
        
        # Validate manufacturing date not in future
        if self.manufacturing_date and self.manufacturing_date > timezone.now().date():
            raise ValidationError({
                'manufacturing_date': "Manufacturing date cannot be in the future."
            })
        
        # Validate supplier is active
        if self.supplier and not self.supplier.is_active:
            raise ValidationError({
                'supplier': "Cannot use inactive supplier."
            })
        
        # Validate medicine is active
        if self.medicine and not self.medicine.is_active:
            raise ValidationError({
                'medicine': "Cannot add stock for inactive medicine."
            })
        
        # Validate damage notes
        if self.is_damaged and not self.damage_notes.strip():
            raise ValidationError({
                'damage_notes': "Damage notes required when stock is marked as damaged."
            })
    
    def save(self, *args, **kwargs):
        """Save with validation and stock update"""
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Update medicine total quantity
        self.update_medicine_total_quantity()
    
    def update_medicine_total_quantity(self):
        """Update total quantity in medicine model"""
        if self.medicine:
            total = self.medicine.stock_batches.filter(
                quantity_available__gt=0,
                is_damaged=False,
                expiry_date__gt=timezone.now().date()
            ).aggregate(
                total=models.Sum('quantity_available')
            )['total'] or 0
            
            self.medicine.total_quantity = total
            self.medicine.save(update_fields=['total_quantity'])
    
    @property
    def is_expired(self):
        """Check if stock is expired"""
        return self.expiry_date < timezone.now().date()
    
    @property
    def days_to_expiry(self):
        """Get days until expiry"""
        return (self.expiry_date - timezone.now().date()).days
    
    @property
    def is_expiring_soon(self):
        """Check if expiring within 30 days"""
        return 0 <= self.days_to_expiry <= 30
    
    def __str__(self):
        return f"{self.medicine.medicine_name} - Batch: {self.batch_number}"


class StockAlert(models.Model):
    """Stock alerts for low stock, expiry, etc."""
    
    ALERT_TYPE_CHOICES = [
        ('LOW_STOCK', 'Low Stock'),
        ('OUT_OF_STOCK', 'Out of Stock'),
        ('EXPIRING_SOON', 'Expiring Soon'),
        ('EXPIRED', 'Expired Stock'),
        ('DAMAGED', 'Damaged Stock'),
    ]
    
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        help_text="Medicine with alert"
    )
    
    stock_batch = models.ForeignKey(
        MedicineStock,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Specific stock batch (if applicable)"
    )
    
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPE_CHOICES,
        help_text="Type of alert"
    )
    
    message = models.TextField(
        max_length=500,
        help_text="Alert message"
    )
    
    is_resolved = models.BooleanField(
        default=False,
        help_text="Has this alert been resolved?"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who resolved the alert"
    )
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'pharmacist_stock_alert'
    
    def clean(self):
        """Alert validation"""
        super().clean()
        
        if not self.message.strip():
            raise ValidationError({
                'message': "Alert message is required."
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.alert_type} - {self.medicine.medicine_name}"


class Prescription(models.Model):
    """Patient prescriptions for medicine dispensing"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIALLY_DISPENSED', 'Partially Dispensed'),
        ('FULLY_DISPENSED', 'Fully Dispensed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    prescription_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Auto-generated prescription code"
    )
    
    patient_name = models.CharField(
        max_length=200,
        validators=[validate_medicine_name],  # Same 3-char minimum rule
        help_text="Patient full name"
    )
    
    patient_phone = models.CharField(
        max_length=15,
        validators=[validate_phone_number],
        help_text="Patient 10-digit phone number"
    )
    
    patient_age = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(150)
        ],
        help_text="Patient age in years"
    )
    
    doctor_name = models.CharField(
        max_length=200,
        validators=[validate_medicine_name],
        help_text="Prescribing doctor name"
    )
    
    prescription_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date prescription was created"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Prescription status"
    )
    
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total prescription amount"
    )
    
    class Meta:
        ordering = ['-prescription_date']
        db_table = 'pharmacist_prescription'
    
    def clean(self):
        """Prescription validation"""
        super().clean()
        
        if self.patient_name:
            self.patient_name = self.patient_name.strip().title()
        
        if self.doctor_name:
            self.doctor_name = self.doctor_name.strip().title()
    
    def save(self, *args, **kwargs):
        """Auto-generate prescription code"""
        if not self.prescription_code:
            last_prescription = Prescription.objects.order_by('id').last()
            if last_prescription:
                next_id = last_prescription.id + 1
            else:
                next_id = 1
            self.prescription_code = f"RX{str(next_id).zfill(6)}"
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Prescription {self.prescription_code} - {self.patient_name}"


class PrescriptionItem(models.Model):
    """Individual medicines in a prescription"""
    
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Associated prescription"
    )
    
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.PROTECT,
        help_text="Prescribed medicine"
    )
    
    quantity_prescribed = models.PositiveIntegerField(
        validators=[validate_positive_quantity],
        help_text="Quantity prescribed by doctor"
    )
    
    quantity_dispensed = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Quantity already dispensed"
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validate_positive_price],
        help_text="Price per unit at time of prescription"
    )
    
    dosage_instructions = models.TextField(
        max_length=500,
        help_text="How to take the medicine"
    )
    
    class Meta:
        db_table = 'pharmacist_prescription_item'
        
        constraints = [
            models.UniqueConstraint(
                fields=['prescription', 'medicine'],
                name='unique_medicine_per_prescription'
            ),
            models.CheckConstraint(
                check=models.Q(quantity_dispensed__lte=models.F('quantity_prescribed')),
                name='dispensed_lte_prescribed'
            )
        ]
    
    def clean(self):
        """Prescription item validation"""
        super().clean()
        
        # Validate dispensed quantity
        if self.quantity_dispensed > self.quantity_prescribed:
            raise ValidationError({
                'quantity_dispensed': f"Cannot dispense {self.quantity_dispensed}. Only {self.quantity_prescribed} prescribed."
            })
        
        # Validate medicine is active
        if self.medicine and not self.medicine.is_active:
            raise ValidationError({
                'medicine': "Cannot prescribe inactive medicine."
            })
        
        # Validate dosage instructions
        if not self.dosage_instructions.strip():
            raise ValidationError({
                'dosage_instructions': "Dosage instructions are required."
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def subtotal(self):
        """Calculate subtotal for dispensed quantity"""
        return self.quantity_dispensed * self.unit_price
    
    @property
    def is_fully_dispensed(self):
        """Check if fully dispensed"""
        return self.quantity_dispensed >= self.quantity_prescribed
    
    @property
    def remaining_quantity(self):
        """Get remaining quantity to dispense"""
        return self.quantity_prescribed - self.quantity_dispensed
    
    def __str__(self):
        return f"{self.medicine.medicine_name} x {self.quantity_prescribed}"


class Sale(models.Model):
    """Sales transactions for medicine dispensing"""
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
        ('INSURANCE', 'Insurance'),
    ]
    
    sale_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Auto-generated sale code"
    )
    
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Associated prescription (if any)"
    )
    
    customer_name = models.CharField(
        max_length=200,
        validators=[validate_medicine_name],
        help_text="Customer name"
    )
    
    customer_phone = models.CharField(
        max_length=15,
        validators=[validate_phone_number],
        help_text="Customer phone number"
    )
    
    pharmacist = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        help_text="Pharmacist who processed the sale"
    )
    
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Subtotal before tax and discount"
    )
    
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Discount amount"
    )
    
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Tax amount"
    )
    
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Final total amount"
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='CASH',
        help_text="Payment method used"
    )
    
    is_completed = models.BooleanField(
        default=False,
        help_text="Is sale completed?"
    )
    
    sale_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of sale"
    )
    
    class Meta:
        ordering = ['-sale_date']
        db_table = 'pharmacist_sale'
        
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_amount__gt=0),
                name='positive_total_amount'
            )
        ]
    
    def clean(self):
        """Sale validation"""
        super().clean()
        
        if self.customer_name:
            self.customer_name = self.customer_name.strip().title()
        
        # Validate total calculation
        expected_total = self.subtotal + self.tax_amount - self.discount_amount
        if abs(self.total_amount - expected_total) > Decimal('0.01'):
            raise ValidationError({
                'total_amount': f"Total amount should be {expected_total}."
            })
    
    def save(self, *args, **kwargs):
        """Auto-generate sale code"""
        if not self.sale_code:
            last_sale = Sale.objects.order_by('id').last()
            if last_sale:
                next_id = last_sale.id + 1
            else:
                next_id = 1
            self.sale_code = f"SALE{str(next_id).zfill(6)}"
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Sale {self.sale_code} - {self.customer_name} - ₹{self.total_amount}"


class SaleItem(models.Model):
    """Individual items in a sale"""
    
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Associated sale"
    )
    
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.PROTECT,
        help_text="Medicine sold"
    )
    
    stock_batch = models.ForeignKey(
        MedicineStock,
        on_delete=models.PROTECT,
        help_text="Stock batch used"
    )
    
    quantity = models.PositiveIntegerField(
        validators=[validate_positive_quantity],
        help_text="Quantity sold"
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validate_positive_price],
        help_text="Unit price at time of sale"
    )
    
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Line item subtotal"
    )
    
    class Meta:
        db_table = 'pharmacist_sale_item'
        
        constraints = [
            models.CheckConstraint(
                check=models.Q(subtotal__gt=0),
                name='positive_item_subtotal'
            )
        ]
    
    def clean(self):
        """Sale item validation"""
        super().clean()
        
        # Validate subtotal calculation
        expected_subtotal = self.quantity * self.unit_price
        if abs(self.subtotal - expected_subtotal) > Decimal('0.01'):
            raise ValidationError({
                'subtotal': f"Subtotal should be {expected_subtotal}."
            })
        
        # Validate stock availability
        if self.stock_batch and self.quantity > self.stock_batch.quantity_available:
            raise ValidationError({
                'quantity': f"Only {self.stock_batch.quantity_available} units available in stock."
            })
        
        # Validate stock is not expired
        if self.stock_batch and self.stock_batch.is_expired:
            raise ValidationError({
                'stock_batch': "Cannot sell expired medicine."
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Update stock quantity
        if self.stock_batch:
            self.stock_batch.quantity_available -= self.quantity
            self.stock_batch.save()
    
    def __str__(self):
        return f"{self.medicine.medicine_name} x {self.quantity}"
