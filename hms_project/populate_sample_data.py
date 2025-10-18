# populate_sample_data.py - Production Sample Data Population - FIXED
import os
import django
from datetime import date, timedelta, datetime
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hms_project.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from admin_app.models import Specialization, Staff, LoginLog
from receptionist_app.models import Patient, Appointment, BillGeneration
from doctor_app.models import Consultation, Prescription, MedicinePrescription, TestPrescription
from pharmacist_app.models import MedicineCategory, Medicine, MedicineBatch, StockMovement
from labTech_app.models import LabTest, TestResult


def clear_all_data():
    """Clear existing data"""
    print("🗑️  Clearing existing data...")
    TestResult.objects.all().delete()
    TestPrescription.objects.all().delete()
    MedicinePrescription.objects.all().delete()
    Prescription.objects.all().delete()
    Consultation.objects.all().delete()
    StockMovement.objects.all().delete()
    MedicineBatch.objects.all().delete()
    Medicine.objects.all().delete()
    MedicineCategory.objects.all().delete()
    LabTest.objects.all().delete()
    BillGeneration.objects.all().delete()
    Appointment.objects.all().delete()
    Patient.objects.all().delete()
    LoginLog.objects.all().delete()
    Staff.objects.all().delete()
    Specialization.objects.all().delete()
    print("✅ Data cleared!\n")


def populate_specializations():
    """Create specializations"""
    print("📋 Creating Specializations...")
    specializations_data = [
        {'specialization_name': 'Cardiology'},
        {'specialization_name': 'Orthopedics'},
        {'specialization_name': 'Pediatrics'},
        {'specialization_name': 'Neurology'},
        {'specialization_name': 'General Medicine'},
    ]
    
    specs = []
    for data in specializations_data:
        spec = Specialization.objects.create(**data)
        specs.append(spec)
        print(f"  ✓ Created: {spec.specialization_name}")
    
    print(f"✅ {len(specs)} Specializations created!\n")
    return specs


# JUST UPDATE THE USERNAMES IN populate_staff() function:

def populate_staff(specializations):
    """Create staff members"""
    print("👥 Creating Staff Members...")
    
    staff_data = [
        # Administrators
        {
            'staff_name': 'System Administrator',
            'username': 'admin01',  # ✅ FIXED: 6+ characters
            'password': make_password('admin123'),
            'role': 'ADMIN',
            'gender': 'M',
            'date_of_birth': date(1980, 1, 1),
            'Phone_number': '9876543210',
            'Email': 'admin@hospital.com',
            'address': 'Admin Office, Hospital Building',
            'salary': Decimal('75000.00'),
            'joining_date': date(2020, 1, 1),
        },
        # Doctors
        {
            'staff_name': 'Dr. Rajesh Kumar',
            'username': 'rajesh01',  # ✅ FIXED: 6+ characters
            'password': make_password('doctor123'),
            'role': 'DOCTOR',
            'specialization': specializations[0],  # Cardiology
            'gender': 'M',
            'date_of_birth': date(1975, 5, 15),
            'Phone_number': '9876543211',
            'Email': 'rajesh@hospital.com',
            'address': 'Doctor Quarters, Block A',
            'salary': Decimal('120000.00'),
            'joining_date': date(2020, 6, 1),
        },
        {
            'staff_name': 'Dr. Priya Sharma',
            'username': 'priya01',  # ✅ FIXED: 6+ characters
            'password': make_password('doctor123'),
            'role': 'DOCTOR',
            'specialization': specializations[2],  # Pediatrics
            'gender': 'F',
            'date_of_birth': date(1982, 8, 20),
            'Phone_number': '9876543212',
            'Email': 'priya@hospital.com',
            'address': 'Doctor Quarters, Block B',
            'salary': Decimal('110000.00'),
            'joining_date': date(2021, 3, 15),
        },
        # Receptionists
        {
            'staff_name': 'Anjali Nair',
            'username': 'anjali01',  # ✅ FIXED: 6+ characters
            'password': make_password('recep123'),
            'role': 'RECEPTIONIST',
            'gender': 'F',
            'date_of_birth': date(1990, 4, 10),
            'Phone_number': '9876543213',
            'Email': 'anjali@hospital.com',
            'address': 'Staff Quarters, Block C',
            'salary': Decimal('35000.00'),
            'joining_date': date(2021, 8, 1),
        },
        # Pharmacist
        {
            'staff_name': 'Suresh Menon',
            'username': 'suresh01',  # ✅ FIXED: 6+ characters
            'password': make_password('pharma123'),
            'role': 'PHARMACIST',
            'gender': 'M',
            'date_of_birth': date(1985, 11, 25),
            'Phone_number': '9876543214',
            'Email': 'suresh@hospital.com',
            'address': 'Staff Quarters, Block D',
            'salary': Decimal('45000.00'),
            'joining_date': date(2020, 10, 1),
        },
        # Lab Technician
        {
            'staff_name': 'Meena Joseph',
            'username': 'meena01',  # ✅ FIXED: 6+ characters
            'password': make_password('lab123'),
            'role': 'LAB_TECHNICIAN',
            'gender': 'F',
            'date_of_birth': date(1988, 7, 30),
            'Phone_number': '9876543215',
            'Email': 'meena@hospital.com',
            'address': 'Staff Quarters, Block E',
            'salary': Decimal('40000.00'),
            'joining_date': date(2021, 2, 1),
        },
    ]
    
    staff_list = []
    for data in staff_data:
        staff = Staff.objects.create(**data)
        staff_list.append(staff)
        print(f"  ✓ Created: {staff.staff_name} ({staff.role})")
    
    print(f"✅ {len(staff_list)} Staff members created!\n")
    return staff_list

    
    staff_list = []
    for data in staff_data:
        staff = Staff.objects.create(**data)
        staff_list.append(staff)
        print(f"  ✓ Created: {staff.staff_name} ({staff.role})")
    
    print(f"✅ {len(staff_list)} Staff members created!\n")
    return staff_list


def populate_patients(receptionist):
    """Create patients"""
    print("🏥 Creating Patients...")
    
    patients_data = [
        {
            'Patient_name': 'Arjun Pillai',
            'Date_of_Birth': date(1990, 3, 15),
            'Gender': 'M',
            'Blood_Group': 'O+',
            'Phone_number': '9123456780',
            'Email': 'arjun@example.com',
            'Address': 'MG Road, Trivandrum',
            'Emergency_Contact': '9123456781',
            'Medical_History': 'No major history',
            'Allergies': 'Penicillin',
            'registered_by': receptionist,
        },
        {
            'Patient_name': 'Lakshmi Menon',
            'Date_of_Birth': date(1985, 7, 22),
            'Gender': 'F',
            'Blood_Group': 'A+',
            'Phone_number': '9123456782',
            'Email': 'lakshmi@example.com',
            'Address': 'Pattom, Trivandrum',
            'Emergency_Contact': '9123456783',
            'Medical_History': 'Diabetes Type 2',
            'Allergies': 'None',
            'registered_by': receptionist,
        },
        {
            'Patient_name': 'Ravi Kumar',
            'Date_of_Birth': date(2010, 12, 5),
            'Gender': 'M',
            'Blood_Group': 'B+',
            'Phone_number': '9123456784',
            'Email': 'ravi.parent@example.com',
            'Address': 'Ulloor, Trivandrum',
            'Emergency_Contact': '9123456785',
            'Medical_History': 'Asthma',
            'Allergies': 'Dust',
            'registered_by': receptionist,
        },
        {
            'Patient_name': 'Deepa Nair',
            'Date_of_Birth': date(1978, 9, 10),
            'Gender': 'F',
            'Blood_Group': 'AB+',
            'Phone_number': '9123456786',
            'Email': 'deepa@example.com',
            'Address': 'Vattiyoorkavu, Trivandrum',
            'Emergency_Contact': '9123456787',
            'Medical_History': 'Hypertension',
            'Allergies': 'Sulfa drugs',
            'registered_by': receptionist,
        },
        {
            'Patient_name': 'Anil George',
            'Date_of_Birth': date(1995, 6, 18),
            'Gender': 'M',
            'Blood_Group': 'O-',
            'Phone_number': '9123456788',
            'Email': 'anil@example.com',
            'Address': 'Karamana, Trivandrum',
            'Emergency_Contact': '9123456789',
            'Medical_History': 'No major history',
            'Allergies': 'None',
            'registered_by': receptionist,
        },
    ]
    
    patients = []
    for data in patients_data:
        patient = Patient.objects.create(**data)
        patients.append(patient)
        print(f"  ✓ Created: {patient.Patient_name}")
    
    print(f"✅ {len(patients)} Patients created!\n")
    return patients


def populate_appointments(patients, doctors, receptionist):
    """Create appointments"""
    print("📅 Creating Appointments...")
    
    today = date.today()
    appointments_data = [
        {
            'patient': patients[0],
            'doctor': doctors[0],
            'appointment_date': today,
            'appointment_time': datetime.strptime('10:00', '%H:%M').time(),
            'token_number': 1,
            'reason': 'Chest pain and discomfort',
            'status': 'COMPLETED',
            'created_by': receptionist,
        },
        {
            'patient': patients[1],
            'doctor': doctors[0],
            'appointment_date': today,
            'appointment_time': datetime.strptime('10:30', '%H:%M').time(),
            'token_number': 2,
            'reason': 'Diabetes checkup',
            'status': 'COMPLETED',
            'created_by': receptionist,
        },
        {
            'patient': patients[2],
            'doctor': doctors[1],
            'appointment_date': today,
            'appointment_time': datetime.strptime('11:00', '%H:%M').time(),
            'token_number': 1,
            'reason': 'Breathing difficulty',
            'status': 'COMPLETED',
            'created_by': receptionist,
        },
        {
            'patient': patients[3],
            'doctor': doctors[0],
            'appointment_date': today + timedelta(days=1),
            'appointment_time': datetime.strptime('09:00', '%H:%M').time(),
            'token_number': 1,
            'reason': 'Blood pressure monitoring',
            'status': 'SCHEDULED',
            'created_by': receptionist,
        },
        {
            'patient': patients[4],
            'doctor': doctors[1],
            'appointment_date': today + timedelta(days=1),
            'appointment_time': datetime.strptime('10:00', '%H:%M').time(),
            'token_number': 2,
            'reason': 'General checkup',
            'status': 'SCHEDULED',
            'created_by': receptionist,
        },
    ]
    
    appointments = []
    for data in appointments_data:
        appointment = Appointment.objects.create(**data)
        appointments.append(appointment)
        print(f"  ✓ Created: Appointment for {appointment.patient.Patient_name}")
    
    print(f"✅ {len(appointments)} Appointments created!\n")
    return appointments


def populate_medicine_data(pharmacist):
    """Create medicine categories and medicines"""
    print("💊 Creating Medicine Data...")
    
    # Categories
    categories_data = [
        {'category_name': 'Antibiotics'},
        {'category_name': 'Analgesics'},
        {'category_name': 'Antihypertensives'},
        {'category_name': 'Antidiabetics'},
        {'category_name': 'Respiratory'},
    ]
    
    categories = []
    for data in categories_data:
        category = MedicineCategory.objects.create(**data)
        categories.append(category)
        print(f"  ✓ Category: {category.category_name}")
    
    # Medicines
    medicines_data = [
        {
            'medicine_name': 'Amoxicillin 500mg',
            'generic_name': 'Amoxicillin',
            'category': categories[0],
            'company_name': 'Cipla',
            'strength': '500mg',
            'unit_price': Decimal('15.50'),
            'quantity_in_stock': 500,
            'reorder_level': 50,
            'expiry_date': date.today() + timedelta(days=730),
            'added_by': pharmacist,
        },
        {
            'medicine_name': 'Paracetamol 650mg',
            'generic_name': 'Paracetamol',
            'category': categories[1],
            'company_name': 'Sun Pharma',
            'strength': '650mg',
            'unit_price': Decimal('5.00'),
            'quantity_in_stock': 1000,
            'reorder_level': 100,
            'expiry_date': date.today() + timedelta(days=730),
            'added_by': pharmacist,
        },
        {
            'medicine_name': 'Amlodipine 5mg',
            'generic_name': 'Amlodipine',
            'category': categories[2],
            'company_name': 'Pfizer',
            'strength': '5mg',
            'unit_price': Decimal('8.75'),
            'quantity_in_stock': 300,
            'reorder_level': 30,
            'expiry_date': date.today() + timedelta(days=730),
            'added_by': pharmacist,
        },
        {
            'medicine_name': 'Metformin 500mg',
            'generic_name': 'Metformin',
            'category': categories[3],
            'company_name': 'Dr. Reddy\'s',
            'strength': '500mg',
            'unit_price': Decimal('6.50'),
            'quantity_in_stock': 400,
            'reorder_level': 50,
            'expiry_date': date.today() + timedelta(days=730),
            'added_by': pharmacist,
        },
        {
            'medicine_name': 'Salbutamol Inhaler',
            'generic_name': 'Salbutamol',
            'category': categories[4],
            'company_name': 'GSK',
            'strength': '100mcg',
            'unit_price': Decimal('125.00'),
            'quantity_in_stock': 75,
            'reorder_level': 10,
            'expiry_date': date.today() + timedelta(days=730),
            'added_by': pharmacist,
        },
    ]
    
    medicines = []
    for data in medicines_data:
        medicine = Medicine.objects.create(**data)
        medicines.append(medicine)
        print(f"  ✓ Medicine: {medicine.medicine_name}")
    
    print(f"✅ {len(categories)} Categories and {len(medicines)} Medicines created!\n")
    return categories, medicines


def populate_consultations(appointments, doctors):
    """Create consultations"""
    print("🩺 Creating Consultations...")
    
    consultations_data = [
        {
            'appointment': appointments[0],
            'patient': appointments[0].patient,
            'doctor': doctors[0],
            'blood_pressure': '140/90',
            'temperature': Decimal('98.6'),
            'pulse_rate': 78,
            'symptoms': 'Chest pain, difficulty breathing',
            'diagnosis': 'Hypertension, possible cardiac issue',
            'status': 'COMPLETED',
        },
        {
            'appointment': appointments[1],
            'patient': appointments[1].patient,
            'doctor': doctors[0],
            'blood_pressure': '130/85',
            'temperature': Decimal('98.4'),
            'pulse_rate': 72,
            'symptoms': 'High blood sugar levels',
            'diagnosis': 'Type 2 Diabetes - under control',
            'status': 'COMPLETED',
        },
        {
            'appointment': appointments[2],
            'patient': appointments[2].patient,
            'doctor': doctors[1],
            'temperature': Decimal('99.2'),
            'pulse_rate': 85,
            'symptoms': 'Wheezing, shortness of breath',
            'diagnosis': 'Asthma exacerbation',
            'status': 'COMPLETED',
        },
    ]
    
    consultations = []
    for data in consultations_data:
        consultation = Consultation.objects.create(**data)
        consultations.append(consultation)
        print(f"  ✓ Created: Consultation for {consultation.patient.Patient_name}")
    
    print(f"✅ {len(consultations)} Consultations created!\n")
    return consultations


def populate_prescriptions(consultations, medicines):
    """Create prescriptions"""
    print("📝 Creating Prescriptions...")
    
    prescriptions = []
    
    # Prescription 1 - Hypertension patient
    p1 = Prescription.objects.create(
        consultation=consultations[0],
        patient=consultations[0].patient,
        doctor=consultations[0].doctor,
        general_instructions='Take medications regularly, avoid salt'
    )
    MedicinePrescription.objects.create(
        prescription=p1,
        medicine_name='Amlodipine 5mg',
        dosage='1 tablet',
        frequency='OD',
        timing='AFTER_FOOD',
        duration='30 days',
        quantity=30
    )
    prescriptions.append(p1)
    print(f"  ✓ Prescription for {p1.patient.Patient_name}")
    
    # Prescription 2 - Diabetes patient
    p2 = Prescription.objects.create(
        consultation=consultations[1],
        patient=consultations[1].patient,
        doctor=consultations[1].doctor,
        general_instructions='Monitor blood sugar daily, maintain diet'
    )
    MedicinePrescription.objects.create(
        prescription=p2,
        medicine_name='Metformin 500mg',
        dosage='1 tablet',
        frequency='BD',
        timing='AFTER_FOOD',
        duration='60 days',
        quantity=120
    )
    prescriptions.append(p2)
    print(f"  ✓ Prescription for {p2.patient.Patient_name}")
    
    # Prescription 3 - Asthma patient
    p3 = Prescription.objects.create(
        consultation=consultations[2],
        patient=consultations[2].patient,
        doctor=consultations[2].doctor,
        general_instructions='Use inhaler as needed, avoid triggers'
    )
    MedicinePrescription.objects.create(
        prescription=p3,
        medicine_name='Salbutamol Inhaler',
        dosage='2 puffs',
        frequency='SOS',
        timing='WITH_FOOD',
        duration='As needed',
        quantity=1
    )
    prescriptions.append(p3)
    print(f"  ✓ Prescription for {p3.patient.Patient_name}")
    
    print(f"✅ {len(prescriptions)} Prescriptions created!\n")
    return prescriptions


def populate_lab_tests(labtech):
    """Create lab tests"""
    print("🔬 Creating Lab Tests...")
    
    tests_data = [
        {
            'test_name': 'Complete Blood Count (CBC)',
            'description': 'Full blood analysis',
            'normal_range': 'WBC: 4-11K, RBC: 4.5-5.5M',
            'unit': 'cells/mcL',
            'price': Decimal('450.00'),
            'sample_type': 'Blood',
            'turnaround_time': '6 hours',
        },
        {
            'test_name': 'Blood Sugar (Fasting)',
            'description': 'Fasting blood glucose test',
            'normal_range': '70-100 mg/dL',
            'unit': 'mg/dL',
            'price': Decimal('150.00'),
            'sample_type': 'Blood',
            'turnaround_time': '2 hours',
        },
        {
            'test_name': 'Lipid Profile',
            'description': 'Cholesterol and triglycerides',
            'normal_range': 'Total: <200, HDL: >40',
            'unit': 'mg/dL',
            'price': Decimal('550.00'),
            'sample_type': 'Blood',
            'turnaround_time': '12 hours',
        },
        {
            'test_name': 'ECG',
            'description': 'Electrocardiogram',
            'normal_range': 'Normal sinus rhythm',
            'unit': 'N/A',
            'price': Decimal('300.00'),
            'sample_type': 'Non-invasive',
            'turnaround_time': '30 minutes',
        },
    ]
    
    tests = []
    for data in tests_data:
        test = LabTest.objects.create(**data)
        tests.append(test)
        print(f"  ✓ Created: {test.test_name}")
    
    print(f"✅ {len(tests)} Lab Tests created!\n")
    return tests


def populate_bills(patients, receptionist):
    """Create bills"""
    print("💰 Creating Bills...")
    
    bills_data = [
        {
            'patient': patients[0],
            'consultation_fee': Decimal('500.00'),
            'medicine_cost': Decimal('262.50'),
            'lab_test_cost': Decimal('300.00'),
            'total_amount': Decimal('1062.50'),
            'amount_paid': Decimal('1062.50'),
            'payment_status': 'PAID',
            'payment_method': 'CARD',
            'generated_by': receptionist,
        },
        {
            'patient': patients[1],
            'consultation_fee': Decimal('500.00'),
            'medicine_cost': Decimal('780.00'),
            'lab_test_cost': Decimal('150.00'),
            'total_amount': Decimal('1430.00'),
            'amount_paid': Decimal('1430.00'),
            'payment_status': 'PAID',
            'payment_method': 'UPI',
            'generated_by': receptionist,
        },
        {
            'patient': patients[2],
            'consultation_fee': Decimal('500.00'),
            'medicine_cost': Decimal('125.00'),
            'total_amount': Decimal('625.00'),
            'amount_paid': Decimal('625.00'),
            'payment_status': 'PAID',
            'payment_method': 'CASH',
            'generated_by': receptionist,
        },
    ]
    
    bills = []
    for data in bills_data:
        bill = BillGeneration.objects.create(**data)
        bills.append(bill)
        print(f"  ✓ Bill for {bill.patient.Patient_name}: ₹{bill.total_amount}")
    
    print(f"✅ {len(bills)} Bills created!\n")
    return bills


def main():
    """Main population function"""
    print("\n" + "="*60)
    print("🏥 HOSPITAL MANAGEMENT SYSTEM - SAMPLE DATA POPULATION")
    print("="*60 + "\n")
    
    # Clear existing data
    clear_all_data()
    
    # Populate data
    specializations = populate_specializations()
    staff = populate_staff(specializations)
    
    # Extract specific staff
    admin = staff[0]
    doctors = [staff[1], staff[2]]
    receptionist = staff[3]
    pharmacist = staff[4]
    labtech = staff[5]
    
    patients = populate_patients(receptionist)
    appointments = populate_appointments(patients, doctors, receptionist)
    categories, medicines = populate_medicine_data(pharmacist)
    consultations = populate_consultations(appointments, doctors)
    prescriptions = populate_prescriptions(consultations, medicines)
    lab_tests = populate_lab_tests(labtech)
    bills = populate_bills(patients, receptionist)
    
    print("\n" + "="*60)
    print("✅ SAMPLE DATA POPULATION COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"  • Specializations: {len(specializations)}")
    print(f"  • Staff Members: {len(staff)}")
    print(f"  • Patients: {len(patients)}")
    print(f"  • Appointments: {len(appointments)}")
    print(f"  • Medicine Categories: {len(categories)}")
    print(f"  • Medicines: {len(medicines)}")
    print(f"  • Consultations: {len(consultations)}")
    print(f"  • Prescriptions: {len(prescriptions)}")
    print(f"  • Lab Tests: {len(lab_tests)}")
    print(f"  • Bills: {len(bills)}")
    
    print(f"\n🔐 Login Credentials:")
    print(f"  Admin: username='admin01', password='admin123'")
    print(f"  Doctor: username='rajesh01', password='doctor123'")
    print(f"  Receptionist: username='anjali01', password='recep123'")
    print(f"  Pharmacist: username='suresh01', password='pharma123'")
    print(f"  Lab Tech: username='meena01', password='lab123'")
    print("\n")



if __name__ == '__main__':
    main()
