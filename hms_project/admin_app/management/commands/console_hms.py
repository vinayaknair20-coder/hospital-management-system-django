"""
Django Management Command for Console HMS Interface
This provides the console UI screens as required in the project specifications.
"""

import os
import sys
import getpass
from datetime import datetime, date
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
from django.core.exceptions import ValidationError

# Import models
from admin_app.models import Staff, LoginLog, Specialization
from receptionist_app.models import Patient, Appointment, Bill_Generation
from pharmacist_app.models import Medicine, MedicineCategory
from labTech_app.models import LabTest, TestResult


class ConsoleHMS:
    """Console HMS Interface following the 3-layer architecture"""
    
    def __init__(self):
        self.current_user = None
        self.failed_attempts = 0
        self.max_attempts = 3
        
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Print formatted header"""
        print("=" * 60)
        print(f"  {title}")
        print("=" * 60)
    
    def print_menu(self, options):
        """Print formatted menu"""
        print("\n" + "-" * 40)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        print("-" * 40)
    
    def get_user_input(self, prompt, required=True):
        """Get user input with validation"""
        while True:
            value = input(f"{prompt}: ").strip()
            if not required or value:
                return value
            print("❌ This field is required. Please try again.")
    
    def validate_username(self, username):
        """Validate username (min 6 characters)"""
        if len(username) < 6:
            print("❌ Username must be at least 6 characters long")
            return False
        return True
    
    def validate_password(self, password):
        """Validate password (min 6 characters)"""
        if len(password) < 6:
            print("❌ Password must be at least 6 characters long")
            return False
        return True
    
    def validate_name(self, name):
        """Validate name (min 3 characters)"""
        if len(name.strip()) < 3:
            print("❌ Name must be at least 3 characters long")
            return False
        return True
    
    def validate_phone(self, phone):
        """Validate phone number (exactly 10 digits)"""
        if not phone.isdigit() or len(phone) != 10:
            print("❌ Phone number must be exactly 10 digits")
            return False
        return True
    
    def validate_date(self, date_str, field_name="Date"):
        """Validate date format (dd-mm-yyyy)"""
        try:
            datetime.strptime(date_str, '%d-%m-%Y')
            return True
        except ValueError:
            print(f"❌ {field_name} must be in format 'dd-mm-yyyy'")
            return False
    
    def log_activity(self, username, log_type, message):
        """Log activity to database"""
        try:
            LoginLog.objects.create(
                username=username,
                log_type=log_type,
                message=message
            )
        except Exception as e:
            print(f"⚠️  Warning: Could not log activity - {e}")
    
    def login_screen(self):
        """Screen 1: Login Screen"""
        self.clear_screen()
        self.print_header("CLINIC MANAGEMENT SYSTEM - LOGIN")
        
        print("\n🔐 Please enter your credentials to login")
        print("   (Username and Password must be at least 6 characters)")
        
        while self.failed_attempts < self.max_attempts:
            print(f"\n📝 Attempt {self.failed_attempts + 1} of {self.max_attempts}")
            
            username = self.get_user_input("Username")
            if not self.validate_username(username):
                continue
                
            password = getpass.getpass("Password: ")
            if not self.validate_password(password):
                continue
            
            # Check credentials
            try:
                staff = Staff.objects.get(username=username)
                if check_password(password, staff.password) and staff.is_active:
                    self.current_user = staff
                    self.log_activity(username, 'SUCCESS', f'Successful login for {staff.role}')
                    print(f"\n✅ Welcome, {staff.staff_name}!")
                    print(f"   Role: {staff.role}")
                    return True
                else:
                    self.failed_attempts += 1
                    self.log_activity(username, 'FAILED', f'Failed login attempt')
                    print("❌ Wrong username or password")
            except Staff.DoesNotExist:
                self.failed_attempts += 1
                self.log_activity(username, 'FAILED', f'Failed login for non-existent user')
                print("❌ Wrong username or password")
            
            if self.failed_attempts < self.max_attempts:
                print(f"   {self.max_attempts - self.failed_attempts} attempts remaining...")
        
        # Max attempts reached
        self.log_activity(username, 'LOCKED', f'Account locked after {self.max_attempts} failed attempts')
        print(f"\n🚫 Three wrong attempts. The application will close.")
        print("   Please see the log for details.")
        return False
    
    def main_menu_screen(self):
        """Screen 2: After Login - Main Menu"""
        self.clear_screen()
        self.print_header(f"WELCOME - {self.current_user.staff_name.upper()}")
        print(f"Role: {self.current_user.role}")
        print(f"Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Role-based menu options
        if self.current_user.role == 'ADMIN':
            options = [
                "Manage Staff",
                "Manage Patients", 
                "Manage Medicines",
                "Manage Lab Tests",
                "View Reports",
                "Logout"
            ]
        elif self.current_user.role == 'RECEPTIONIST':
            options = [
                "Manage Patients",
                "Manage Appointments",
                "Generate Bills",
                "Logout"
            ]
        elif self.current_user.role == 'PHARMACIST':
            options = [
                "Manage Medicines",
                "View Stock",
                "Logout"
            ]
        elif self.current_user.role == 'LAB_TECHNICIAN':
            options = [
                "Manage Lab Tests",
                "Manage Test Results",
                "Logout"
            ]
        else:
            options = ["Logout"]
        
        self.print_menu(options)
        
        while True:
            try:
                choice = int(self.get_user_input("Enter your choice"))
                if 1 <= choice <= len(options):
                    return choice, options[choice-1]
                else:
                    print("❌ Invalid choice. Please select a valid option.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def patient_management_screen(self):
        """Screen 3: Patient Management"""
        while True:
            self.clear_screen()
            self.print_header("PATIENT MANAGEMENT")
            
            options = [
                "Add Patient",
                "List All Patients", 
                "Search Patient",
                "Go to Main Menu"
            ]
            self.print_menu(options)
            
            choice = int(self.get_user_input("Enter your choice"))
            
            if choice == 1:
                self.add_patient()
            elif choice == 2:
                self.list_patients()
            elif choice == 3:
                self.search_patient()
            elif choice == 4:
                break
            else:
                print("❌ Invalid choice. Please try again.")
                input("Press Enter to continue...")
    
    def add_patient(self):
        """Add new patient"""
        self.clear_screen()
        self.print_header("ADD NEW PATIENT")
        
        try:
            with transaction.atomic():
                # Get patient details
                patient_name = self.get_user_input("Full Name")
                if not self.validate_name(patient_name):
                    input("Press Enter to continue...")
                    return
                
                dob_str = self.get_user_input("Date of Birth (dd-mm-yyyy)")
                if not self.validate_date(dob_str, "Date of Birth"):
                    input("Press Enter to continue...")
                    return
                
                dob = datetime.strptime(dob_str, '%d-%m-%Y').date()
                
                print("Gender (M/F/O):")
                gender = self.get_user_input("Gender").upper()
                if gender not in ['M', 'F', 'O']:
                    print("❌ Gender must be M, F, or O")
                    input("Press Enter to continue...")
                    return
                
                blood_group = self.get_user_input("Blood Group")
                phone = self.get_user_input("Phone Number")
                if not self.validate_phone(phone):
                    input("Press Enter to continue...")
                    return
                
                address = self.get_user_input("Address")
                
                # Create patient
                patient = Patient.objects.create(
                    Patient_name=patient_name,
                    date_of_birth=dob,
                    Gender=gender,
                    Blood_Group=blood_group,
                    Phone_number=phone,
                    Address=address
                )
                
                print(f"\n✅ Successfully added!")
                print(f"   Patient Registration Number: {patient.Patient_id}")
                print(f"   Patient Name: {patient.Patient_name}")
                
        except ValidationError as e:
            print(f"❌ Validation Error: {e}")
        except Exception as e:
            print(f"❌ Error adding patient: {e}")
        
        input("\nPress Enter to continue...")
    
    def list_patients(self):
        """List all patients"""
        self.clear_screen()
        self.print_header("LIST OF PATIENTS")
        
        patients = Patient.objects.filter(is_active=True).order_by('Patient_name')
        
        if not patients.exists():
            print("No patients found.")
        else:
            print(f"\n{'ID':<8} {'Name':<25} {'Phone':<12} {'Blood Group':<12} {'Age':<5}")
            print("-" * 70)
            for patient in patients:
                print(f"{patient.Patient_id:<8} {patient.Patient_name:<25} {patient.Phone_number:<12} {patient.Blood_Group:<12} {patient.Age or 'N/A':<5}")
        
        input("\nPress Enter to continue...")
    
    def search_patient(self):
        """Search patient by ID or phone"""
        self.clear_screen()
        self.print_header("SEARCH PATIENT")
        
        print("How would you like to search for the patient?")
        options = [
            "By Patient Registration Number",
            "By Phone Number", 
            "Go to Manage Patient Menu"
        ]
        self.print_menu(options)
        
        choice = int(self.get_user_input("Enter your choice"))
        
        if choice == 1:
            # Search by ID
            try:
                patient_id = int(self.get_user_input("Patient Registration Number"))
                patient = Patient.objects.get(Patient_id=patient_id, is_active=True)
                self.display_patient_details(patient)
            except Patient.DoesNotExist:
                print("❌ Patient does not exist")
            except ValueError:
                print("❌ Please enter a valid patient ID")
        
        elif choice == 2:
            # Search by phone
            phone = self.get_user_input("Phone Number")
            if not self.validate_phone(phone):
                input("Press Enter to continue...")
                return
            
            try:
                patient = Patient.objects.get(Phone_number=phone, is_active=True)
                self.display_patient_details(patient)
            except Patient.DoesNotExist:
                print("❌ Patient does not exist")
        
        elif choice == 3:
            return
        
        input("\nPress Enter to continue...")
    
    def display_patient_details(self, patient):
        """Display patient details with edit/disable options"""
        self.clear_screen()
        self.print_header(f"PATIENT DETAILS - {patient.Patient_name}")
        
        print(f"Registration Number: {patient.Patient_id}")
        print(f"Name: {patient.Patient_name}")
        print(f"Date of Birth: {patient.date_of_birth.strftime('%d-%m-%Y')}")
        print(f"Age: {patient.Age}")
        print(f"Gender: {patient.Gender}")
        print(f"Blood Group: {patient.Blood_Group}")
        print(f"Phone: {patient.Phone_number}")
        print(f"Address: {patient.Address}")
        
        print("\nHow would you like to proceed?")
        options = [
            "Edit Patient",
            "Disable Patient",
            "Go Back"
        ]
        self.print_menu(options)
        
        choice = int(self.get_user_input("Enter your choice"))
        
        if choice == 1:
            self.edit_patient(patient)
        elif choice == 2:
            self.disable_patient(patient)
    
    def edit_patient(self, patient):
        """Edit patient (Name and Address only)"""
        self.clear_screen()
        self.print_header("EDIT PATIENT")
        
        print("Which field do you want to edit?")
        options = [
            "Name",
            "Address"
        ]
        self.print_menu(options)
        
        choice = int(self.get_user_input("Enter your choice"))
        
        try:
            if choice == 1:
                new_name = self.get_user_input("New Name")
                if self.validate_name(new_name):
                    patient.Patient_name = new_name
                    patient.save()
                    print("✅ Updated successfully")
            
            elif choice == 2:
                new_address = self.get_user_input("New Address")
                patient.Address = new_address
                patient.save()
                print("✅ Updated successfully")
            
            else:
                print("❌ Invalid choice")
        
        except Exception as e:
            print(f"❌ Error updating patient: {e}")
        
        input("\nPress Enter to continue...")
    
    def disable_patient(self, patient):
        """Disable patient"""
        confirm = self.get_user_input("Do you want to disable the Patient? (y/n)").lower()
        if confirm == 'y':
            patient.is_active = False
            patient.save()
            print("✅ Successfully disabled")
        else:
            print("❌ Operation cancelled")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main application loop"""
        # Screen 1: Login
        if not self.login_screen():
            return
        
        # Screen 2: Main Menu Loop
        while True:
            try:
                choice, option = self.main_menu_screen()
                
                if option == "Logout":
                    print("\n👋 Thank you for using HMS!")
                    break
                elif option == "Manage Patients":
                    self.patient_management_screen()
                elif option == "Manage Staff":
                    print("Staff management - Coming soon!")
                    input("Press Enter to continue...")
                elif option == "Manage Medicines":
                    print("Medicine management - Coming soon!")
                    input("Press Enter to continue...")
                elif option == "Manage Lab Tests":
                    print("Lab test management - Coming soon!")
                    input("Press Enter to continue...")
                else:
                    print("Feature coming soon!")
                    input("Press Enter to continue...")
            
            except KeyboardInterrupt:
                print("\n\n👋 Application closed by user.")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                input("Press Enter to continue...")


class Command(BaseCommand):
    help = 'Run the Console HMS Interface'
    
    def handle(self, *args, **options):
        """Entry point for the management command"""
        self.stdout.write(
            self.style.SUCCESS('Starting Console HMS Interface...')
        )
        
        # Create and run the console interface
        console_hms = ConsoleHMS()
        console_hms.run()
        
        self.stdout.write(
            self.style.SUCCESS('Console HMS Interface closed.')
        )

