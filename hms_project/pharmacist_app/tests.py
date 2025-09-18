"""
PHARMACIST APP TESTS
Comprehensive test suite for pharmacy management system
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
from rest_framework.test import APITestCase
from rest_framework import status

from .models import *
from .utils import generate_stock_alerts, process_medicine_dispensing


class MedicineModelTest(TestCase):
    """Test Medicine model validation and functionality"""
    
    def setUp(self):
        self.category = MedicineCategory.objects.create(name="Antibiotics")
        
    def test_medicine_creation_valid(self):
        """Test valid medicine creation"""
        medicine = Medicine.objects.create(
            medicine_name="Amoxicillin",
            generic_name="Amoxicillin",
            company_name="Pharma Corp",
            category=self.category,
            unit_price=Decimal('25.50'),
            dosage_form="TABLET",
            strength="500mg"
        )
        
        self.assertEqual(medicine.medicine_name, "Amoxicillin")
        self.assertTrue(medicine.medicine_code.startswith("MED"))
        self.assertEqual(medicine.total_quantity, 0)
        
    def test_medicine_name_validation(self):
        """Test medicine name validation"""
        with self.assertRaises(ValidationError):
            medicine = Medicine(
                medicine_name="AB",  # Too short
                company_name="Pharma Corp",
                category=self.category,
                unit_price=Decimal('25.50')
            )
            medicine.full_clean()
    
    def test_auto_generated_medicine_code(self):
        """Test auto-generation of medicine codes"""
        medicine1 = Medicine.objects.create(
            medicine_name="Medicine 1",
            company_name="Company 1",
            category=self.category,
            unit_price=Decimal('10.00')
        )
        
        medicine2 = Medicine.objects.create(
            medicine_name="Medicine 2",
            company_name="Company 2",
            category=self.category,
            unit_price=Decimal('20.00')
        )
        
        self.assertNotEqual(medicine1.medicine_code, medicine2.medicine_code)
        self.assertTrue(medicine1.medicine_code.startswith("MED"))
        self.assertTrue(medicine2.medicine_code.startswith("MED"))


class MedicineStockModelTest(TestCase):
    """Test MedicineStock model validation and functionality"""
    
    def setUp(self):
        self.category = MedicineCategory.objects.create(name="Antibiotics")
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            contact_person="John Doe",
            phone="9876543210",
            email="supplier@test.com",
            address="123 Test Street"
        )
        self.medicine = Medicine.objects.create(
            medicine_name="Test Medicine",
            company_name="Test Company",
            category=self.category,
            unit_price=Decimal('50.00')
        )
    
    def test_stock_creation_valid(self):
        """Test valid stock creation"""
        stock = MedicineStock.objects.create(
            medicine=self.medicine,
            batch_number="BATCH001",
            supplier=self.supplier,
            quantity_received=100,
            quantity_available=100,
            unit_cost=Decimal('45.00'),
            expiry_date=timezone.now().date() + timedelta(days=365)
        )
        
        self.assertEqual(stock.batch_number, "BATCH001")
        self.assertEqual(stock.quantity_available, 100)
        self.assertFalse(stock.is_expired)
    
    def test_expiry_date_validation(self):
        """Test expiry date validation"""
        with self.assertRaises(ValidationError):
            stock = MedicineStock(
                medicine=self.medicine,
                batch_number="BATCH002",
                supplier=self.supplier,
                quantity_received=50,
                quantity_available=50,
                unit_cost=Decimal('45.00'),
                expiry_date=timezone.now().date() - timedelta(days=60)  # Too old
            )
            stock.full_clean()
    
    def test_quantity_consistency_validation(self):
        """Test quantity consistency validation"""
        with self.assertRaises(ValidationError):
            stock = MedicineStock(
                medicine=self.medicine,
                batch_number="BATCH003",
                supplier=self.supplier,
                quantity_received=50,
                quantity_available=75,  # More than received
                unit_cost=Decimal('45.00'),
                expiry_date=timezone.now().date() + timedelta(days=365)
            )
            stock.full_clean()


class StockAlertTest(TestCase):
    """Test stock alert generation"""
    
    def setUp(self):
        self.category = MedicineCategory.objects.create(name="Test Category")
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            contact_person="Test Person",
            phone="9876543210",
            email="test@supplier.com",
            address="Test Address"
        )
        
        # Low stock medicine
        self.low_stock_medicine = Medicine.objects.create(
            medicine_name="Low Stock Medicine",
            company_name="Test Company",
            category=self.category,
            unit_price=Decimal('25.00'),
            total_quantity=5,  # Below default reorder level of 10
            reorder_level=10
        )
        
        # Out of stock medicine
        self.out_of_stock_medicine = Medicine.objects.create(
            medicine_name="Out of Stock Medicine",
            company_name="Test Company",
            category=self.category,
            unit_price=Decimal('30.00'),
            total_quantity=0,
            reorder_level=10
        )
    
    def test_generate_stock_alerts(self):
        """Test stock alert generation"""
        result = generate_stock_alerts()
        
        self.assertTrue(result['success'])
        self.assertGreaterEqual(result['alerts_created'], 2)
        
        # Check that alerts were created
        low_stock_alerts = StockAlert.objects.filter(
            medicine=self.low_stock_medicine,
            alert_type='LOW_STOCK',
            is_resolved=False
        )
        self.assertTrue(low_stock_alerts.exists())
        
        out_of_stock_alerts = StockAlert.objects.filter(
            medicine=self.out_of_stock_medicine,
            alert_type='OUT_OF_STOCK',
            is_resolved=False
        )
        self.assertTrue(out_of_stock_alerts.exists())


class APITestCase(APITestCase):
    """Test API endpoints"""
    
    def setUp(self):
        # Create user and pharmacist group
        self.pharmacist_group = Group.objects.create(name='Pharmacist')
        self.user = User.objects.create_user(
            username='testpharmacist',
            email='pharmacist@test.com',
            password='testpass123'
        )
        self.user.groups.add(self.pharmacist_group)
        
        # Create test data
        self.category = MedicineCategory.objects.create(name="Test Category")
        self.medicine = Medicine.objects.create(
            medicine_name="Test Medicine",
            company_name="Test Company",
            category=self.category,
            unit_price=Decimal('50.00')
        )
    
    def test_medicine_list_api(self):
        """Test medicine list API"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/medicines/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_medicine_search_api(self):
        """Test medicine search API"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/medicines/?search=Test Medicine')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_low_stock_api(self):
        """Test low stock API endpoint"""
        self.client.force_authenticate(user=self.user)
        
        # Update medicine to have low stock
        self.medicine.total_quantity = 5
        self.medicine.reorder_level = 10
        self.medicine.save()
        
        response = self.client.get('/api/medicines/low_stock/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class ValidationTest(TestCase):
    """Test custom validation functions"""
    
    def test_phone_validation(self):
        """Test phone number validation"""
        from .models import validate_phone_number
        
        # Valid phone numbers
        self.assertEqual(validate_phone_number('9876543210'), '9876543210')
        self.assertEqual(validate_phone_number('+919876543210'), '9876543210')
        
        # Invalid phone numbers
        with self.assertRaises(ValidationError):
            validate_phone_number('0987654321')  # Starts with 0
        
        with self.assertRaises(ValidationError):
            validate_phone_number('98765432')  # Too short
    
    def test_medicine_name_validation(self):
        """Test medicine name validation"""
        from .models import validate_medicine_name
        
        # Valid names
        self.assertEqual(validate_medicine_name('Paracetamol'), 'Paracetamol')
        self.assertEqual(validate_medicine_name('amoxicillin'), 'Amoxicillin')
        
        # Invalid names
        with self.assertRaises(ValidationError):
            validate_medicine_name('AB')  # Too short
        
        with self.assertRaises(ValidationError):
            validate_medicine_name('')  # Empty
    
    def test_batch_number_validation(self):
        """Test batch number validation"""
        from .models import validate_batch_number
        
        # Valid batch numbers
        self.assertEqual(validate_batch_number('BATCH001'), 'BATCH001')
        self.assertEqual(validate_batch_number('lot-123'), 'LOT-123')
        
        # Invalid batch numbers
        with self.assertRaises(ValidationError):
            validate_batch_number('AB')  # Too short
        
        with self.assertRaises(ValidationError):
            validate_batch_number('BATCH@001')  # Invalid characters


class PrescriptionTest(TestCase):
    """Test prescription functionality"""
    
    def setUp(self):
        self.category = MedicineCategory.objects.create(name="Antibiotics")
        self.medicine = Medicine.objects.create(
            medicine_name="Amoxicillin",
            company_name="Pharma Corp",
            category=self.category,
            unit_price=Decimal('25.50')
        )
        
        self.prescription = Prescription.objects.create(
            patient_name="John Doe",
            patient_phone="9876543210",
            patient_age=35,
            doctor_name="Dr. Smith"
        )
        
        self.prescription_item = PrescriptionItem.objects.create(
            prescription=self.prescription,
            medicine=self.medicine,
            quantity_prescribed=10,
            unit_price=Decimal('25.50'),
            dosage_instructions="Take 1 tablet twice daily"
        )
    
    def test_prescription_creation(self):
        """Test prescription creation and auto-generated code"""
        self.assertTrue(self.prescription.prescription_code.startswith('RX'))
        self.assertEqual(self.prescription.status, 'PENDING')
    
    def test_prescription_item_properties(self):
        """Test prescription item calculated properties"""
        self.assertEqual(self.prescription_item.remaining_quantity, 10)
        self.assertFalse(self.prescription_item.is_fully_dispensed)
        self.assertEqual(self.prescription_item.subtotal, Decimal('0.00'))  # No quantity dispensed yet


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'rest_framework',
            'pharmacist_app',
        ],
    )
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['pharmacist_app'])
