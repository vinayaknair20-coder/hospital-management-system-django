from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import date, timedelta

from admin_app.models import Staff, Specialization
from receptionist_app.models import Patient, Appointment
from doctor_app.models import Consultation


class ConsultationAPITestCase(TestCase):
    """Comprehensive test suite for Consultation API"""
    
    def setUp(self):
        """Create test data before each test"""
        self.client = APIClient()
        
        # Create Specialization
        self.specialization = Specialization.objects.create(
            specialization_name="Cardiology",
            is_active=True
        )
        
        # Create Doctor
        self.doctor = Staff.objects.create(
            username="dr_test",
            staff_name="Dr. Test Doctor",
            gender="M",
            date_of_birth=date(1980, 1, 1),
            address="123 Test St",
            joining_date=date(2020, 1, 1),
            Phone_number="1234567890",
            Email="doctor@test.com",
            role="DOCTOR",
            specialization=self.specialization,
            salary=150000.00,
            is_active=True
        )
        self.doctor.set_password("testpass123")
        self.doctor.save()
        
        # Create Patient
        self.patient = Patient.objects.create(
            Patient_name="Test Patient",
            date_of_birth=date(1990, 1, 1),
            Gender="M",
            Blood_Group="O+",
            Address="456 Patient St",
            Phone_number="9876543210",
            Email="patient@test.com",
            is_active=True
        )
        
        # Create Appointment
        self.appointment = Appointment.objects.create(
            Patient_id=self.patient,
            doctor_id=self.doctor,
            Appointment_date=timezone.now().date(),
            status="booked"
        )
        
        # Sample consultation data
        self.consultation_data = {
            "appointment": self.appointment.Appointment_id,
            "doctor": self.doctor.staff_id,
            "patient": self.patient.Patient_id,
            "consultation_date": "2025-10-17T14:00:00",
            "diagnosis": "Common cold",
            "symptoms": "Fever, cough, headache",
            "notes": "Rest for 3 days",
            "follow_up_date": "2025-10-24",
            "status": "SCHEDULED"
        }
    
    # ========================================
    # CREATE TESTS (POST)
    # ========================================
    
    def test_create_consultation_success(self):
        """Test creating a consultation successfully"""
        response = self.client.post(
            '/api/doctor/consultations/',
            self.consultation_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Consultation.objects.count(), 1)
        self.assertEqual(response.data['diagnosis'], "Common cold")
    
    def test_create_consultation_with_vitals(self):
        """Test creating consultation with vital signs"""
        data = self.consultation_data.copy()
        data.update({
            "blood_pressure": "120/80",
            "temperature": "98.6",
            "pulse_rate": "72",
            "weight": "70.5",
            "height": "175"
        })
        response = self.client.post(
            '/api/doctor/consultations/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['blood_pressure'], "120/80")
        self.assertEqual(response.data['temperature'], "98.6")
    
    def test_create_consultation_missing_required_fields(self):
        """Test creating consultation without required fields"""
        response = self.client.post(
            '/api/doctor/consultations/',
            {"appointment": self.appointment.Appointment_id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_consultation_invalid_appointment(self):
        """Test creating consultation with non-existent appointment"""
        data = self.consultation_data.copy()
        data['appointment'] = 9999
        response = self.client.post(
            '/api/doctor/consultations/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # ========================================
    # READ TESTS (GET)
    # ========================================
    
    def test_list_consultations(self):
        """Test retrieving list of all consultations"""
        # Create a consultation first
        Consultation.objects.create(
            appointment=self.appointment,
            doctor=self.doctor,
            patient=self.patient,
            consultation_date=timezone.now(),
            diagnosis="Test diagnosis",
            symptoms="Test symptoms",
            status="SCHEDULED"
        )
        
        response = self.client.get('/api/doctor/consultations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_retrieve_single_consultation(self):
        """Test retrieving a single consultation by ID"""
        consultation = Consultation.objects.create(
            appointment=self.appointment,
            doctor=self.doctor,
            patient=self.patient,
            consultation_date=timezone.now(),
            diagnosis="Test diagnosis",
            symptoms="Test symptoms",
            status="SCHEDULED"
        )
        
        response = self.client.get(
            f'/api/doctor/consultations/{consultation.consultation_id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['diagnosis'], "Test diagnosis")
    
    def test_retrieve_nonexistent_consultation(self):
        """Test retrieving a consultation that doesn't exist"""
        response = self.client.get('/api/doctor/consultations/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ========================================
    # UPDATE TESTS (PUT/PATCH)
    # ========================================
    
    def test_update_consultation_put(self):
        """Test updating entire consultation with PUT"""
        consultation = Consultation.objects.create(
            appointment=self.appointment,
            doctor=self.doctor,
            patient=self.patient,
            consultation_date=timezone.now(),
            diagnosis="Old diagnosis",
            symptoms="Old symptoms",
            status="SCHEDULED"
        )
        
        updated_data = self.consultation_data.copy()
        updated_data['diagnosis'] = "Updated diagnosis"
        updated_data['status'] = "COMPLETED"
        
        response = self.client.put(
            f'/api/doctor/consultations/{consultation.consultation_id}/',
            updated_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['diagnosis'], "Updated diagnosis")
        self.assertEqual(response.data['status'], "COMPLETED")
    
    def test_partial_update_consultation_patch(self):
        """Test partial update with PATCH"""
        consultation = Consultation.objects.create(
            appointment=self.appointment,
            doctor=self.doctor,
            patient=self.patient,
            consultation_date=timezone.now(),
            diagnosis="Original diagnosis",
            symptoms="Original symptoms",
            status="SCHEDULED"
        )
        
        response = self.client.patch(
            f'/api/doctor/consultations/{consultation.consultation_id}/',
            {"status": "COMPLETED", "notes": "Patient recovered"},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "COMPLETED")
        self.assertEqual(response.data['notes'], "Patient recovered")
        # Original fields should remain unchanged
        self.assertEqual(response.data['diagnosis'], "Original diagnosis")
    
    # ========================================
    # DELETE TESTS
    # ========================================
    
    def test_delete_consultation(self):
        """Test deleting a consultation"""
        consultation = Consultation.objects.create(
            appointment=self.appointment,
            doctor=self.doctor,
            patient=self.patient,
            consultation_date=timezone.now(),
            diagnosis="Test diagnosis",
            symptoms="Test symptoms",
            status="SCHEDULED"
        )
        
        response = self.client.delete(
            f'/api/doctor/consultations/{consultation.consultation_id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Consultation.objects.count(), 0)
    
    def test_delete_nonexistent_consultation(self):
        """Test deleting a consultation that doesn't exist"""
        response = self.client.delete('/api/doctor/consultations/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ========================================
    # VALIDATION TESTS
    # ========================================
    
    def test_invalid_status_value(self):
        """Test creating consultation with invalid status"""
        data = self.consultation_data.copy()
        data['status'] = "INVALID_STATUS"
        response = self.client.post(
            '/api/doctor/consultations/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_date_format(self):
        """Test creating consultation with invalid date format"""
        data = self.consultation_data.copy()
        # Use a completely invalid date string that cannot be parsed
        data['consultation_date'] = "this-is-not-a-valid-date-2025"
        
        response = self.client.post(
            '/api/doctor/consultations/',
            data,
            format='json'
        )
        
        # Should now properly reject with 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('consultation_date', response.data)
