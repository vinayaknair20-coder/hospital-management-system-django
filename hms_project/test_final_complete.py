"""
FINAL COMPLETE HMS API Testing Suite
Tests all CRUD operations with correct field names and unique data
"""

import requests
import json
import random
import string
from datetime import datetime, date, timedelta

BASE_URL = "http://localhost:8000"

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'

def generate_unique_string(prefix="", length=6):
    """Generate unique string to avoid duplicate errors"""
    timestamp = datetime.now().strftime("%H%M%S")
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{prefix}{timestamp}_{random_str}"

class CompleteCRUDTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.created_objects = {}
        self.test_summary = {
            'GET': {'pass': 0, 'fail': 0},
            'POST': {'pass': 0, 'fail': 0},
            'PUT': {'pass': 0, 'fail': 0},
            'PATCH': {'pass': 0, 'fail': 0},
            'DELETE': {'pass': 0, 'fail': 0}
        }
        
    def print_section(self, title):
        print(f"\n{CYAN}{'='*100}{RESET}")
        print(f"{CYAN}  {title}{RESET}")
        print(f"{CYAN}{'='*100}{RESET}\n")
    
    def log_test(self, method, endpoint, status, description, details=""):
        """Log test result"""
        status_text = f"{GREEN}✓ PASS{RESET}" if status else f"{RED}✗ FAIL{RESET}"
        print(f"{status_text} {method:6} {endpoint:60} {description}")
        
        if not status and details:
            print(f"         {YELLOW}└─ {details[:150]}{RESET}")
        
        self.test_summary[method]['pass' if status else 'fail'] += 1
        if status:
            self.passed += 1
        else:
            self.failed += 1
    
    def test_endpoint(self, method, url, data=None, description=""):
        """Generic endpoint tester"""
        try:
            full_url = f"{BASE_URL}{url}"
            
            if method == 'GET':
                response = requests.get(full_url, timeout=5)
            elif method == 'POST':
                response = requests.post(full_url, json=data, timeout=5)
            elif method == 'PUT':
                response = requests.put(full_url, json=data, timeout=5)
            elif method == 'PATCH':
                response = requests.patch(full_url, json=data, timeout=5)
            elif method == 'DELETE':
                response = requests.delete(full_url, timeout=5)
            
            success = response.status_code in [200, 201, 204]
            details = "" if success else f"HTTP {response.status_code}: {response.text[:200]}"
            
            self.log_test(method, url, success, description, details)
            
            return response if success else None
            
        except Exception as e:
            self.log_test(method, url, False, description, f"Exception: {str(e)[:100]}")
            return None
    
    def print_final_summary(self):
        """Print comprehensive test summary"""
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n{MAGENTA}{'='*100}{RESET}")
        print(f"{MAGENTA}  FINAL TEST SUMMARY{RESET}")
        print(f"{MAGENTA}{'='*100}{RESET}\n")
        
        print(f"  Total Tests:       {total}")
        print(f"  {GREEN}✓ Passed:          {self.passed} ({self.passed/total*100:.1f}%){RESET}")
        print(f"  {RED}✗ Failed:          {self.failed} ({self.failed/total*100:.1f}%){RESET}")
        print(f"  Overall Success:   {success_rate:.1f}%")
        
        print(f"\n{BLUE}  Breakdown by HTTP Method:{RESET}\n")
        
        for method, counts in self.test_summary.items():
            total_method = counts['pass'] + counts['fail']
            if total_method > 0:
                pass_rate = (counts['pass'] / total_method * 100)
                bar_length = 30
                filled = int(bar_length * counts['pass'] / total_method)
                bar = '█' * filled + '░' * (bar_length - filled)
                
                print(f"  {method:8} │ {bar} │ {counts['pass']:2}/{total_method:2} ({pass_rate:5.1f}%)")
        
        print(f"\n{MAGENTA}{'='*100}{RESET}\n")

def run_complete_tests():
    """Run complete CRUD tests for ALL endpoints"""
    tester = CompleteCRUDTester()
    
    print(f"\n{MAGENTA}{'='*100}{RESET}")
    print(f"{MAGENTA}  🏥 HMS - COMPLETE API CRUD TESTING SUITE 🏥{RESET}")
    print(f"{MAGENTA}  Testing all endpoints with proper field names and unique data{RESET}")
    print(f"{MAGENTA}  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}{RESET}")
    print(f"{MAGENTA}{'='*100}{RESET}")
    
    # ====================================================================
    # 1. LAB TECHNICIAN APP - Lab Tests
    # ====================================================================
    tester.print_section("1. LAB TECHNICIAN - Lab Tests")
    
    # GET - List all tests
    tester.test_endpoint('GET', '/api/lab-tech/tests/', description="List all lab tests")
    
    # POST - Create new test
    unique_test_name = generate_unique_string("Lab Test ")
    test_data = {
        "test_name": unique_test_name,
        "test_code": generate_unique_string("LAB-"),
        "category": "Hematology",
        "price": 950.00,
        "normal_range": "WBC: 4,000-11,000/μL",
        "description": "Complete blood count analysis"
    }
    test_response = tester.test_endpoint('POST', '/api/lab-tech/tests/', test_data, "Create lab test")
    
    test_id = None
    if test_response:
        test_result = test_response.json()
        test_id = test_result.get('Test_id')
        
        if test_id:
            # GET - Retrieve single test
            tester.test_endpoint('GET', f'/api/lab-tech/tests/{test_id}/', description="Get test details")
            
            # PUT - Full update
            test_data['price'] = 1000.00
            tester.test_endpoint('PUT', f'/api/lab-tech/tests/{test_id}/', test_data, "Update test (PUT)")
            
            # PATCH - Partial update
            tester.test_endpoint('PATCH', f'/api/lab-tech/tests/{test_id}/', {'price': 1050.00}, "Partial update (PATCH)")
            
            # DELETE
            tester.test_endpoint('DELETE', f'/api/lab-tech/tests/{test_id}/', description="Delete test")
    
    # ====================================================================
    # 2. LAB TECHNICIAN APP - Test Results
    # ====================================================================
    tester.print_section("2. LAB TECHNICIAN - Test Results")
    
    tester.test_endpoint('GET', '/api/lab-tech/results/', description="List all test results")
    
    # ====================================================================
    # 3. PHARMACIST APP - Medicine Categories
    # ====================================================================
    tester.print_section("3. PHARMACIST - Medicine Categories")
    
    # GET - List all categories
    tester.test_endpoint('GET', '/api/pharmacist/categories/', description="List all categories")
    
    # POST - Create category
    unique_category = generate_unique_string("Category_")
    category_data = {
        "category_name": unique_category,
        "description": "Pharmaceutical category for testing"
    }
    cat_response = tester.test_endpoint('POST', '/api/pharmacist/categories/', category_data, "Create category")
    
    category_id = None
    if cat_response:
        cat_result = cat_response.json()
        category_id = cat_result.get('Category_id')
        
        if category_id:
            # GET - Retrieve single
            tester.test_endpoint('GET', f'/api/pharmacist/categories/{category_id}/', description="Get category details")
            
            # PUT - Update
            category_data['description'] = "Updated description"
            tester.test_endpoint('PUT', f'/api/pharmacist/categories/{category_id}/', category_data, "Update category (PUT)")
            
            # PATCH - Partial update
            tester.test_endpoint('PATCH', f'/api/pharmacist/categories/{category_id}/', {'description': 'Patched'}, "Partial update (PATCH)")
            
            # DELETE
            tester.test_endpoint('DELETE', f'/api/pharmacist/categories/{category_id}/', description="Delete category")
    
    # ====================================================================
    # 4. PHARMACIST APP - Medicines
    # ====================================================================
    tester.print_section("4. PHARMACIST - Medicines")
    
    # GET - List all medicines
    tester.test_endpoint('GET', '/api/pharmacist/medicines/', description="List all medicines")
    
    # POST - Create medicine (with ALL required fields)
    unique_medicine = generate_unique_string("Medicine_")
    medicine_data = {
        "medicine_name": unique_medicine,
        "generic_name": "Generic Name",
        "category": 1,  # Assuming category 1 exists
        "company_name": "PharmaCorp Ltd",  # ✅ Required field
        "strength": "500mg",  # ✅ Required field
        "unit_price": 25.50,
        "expiry_date": str(date.today() + timedelta(days=365)),  # ✅ Required field
        "minimum_stock_level": 100,
        "description": "Test medicine"
    }
    med_response = tester.test_endpoint('POST', '/api/pharmacist/medicines/', medicine_data, "Create medicine")
    
    medicine_id = None
    if med_response:
        med_result = med_response.json()
        medicine_id = med_result.get('Medicine_id')
        
        if medicine_id:
            # GET - Retrieve single
            tester.test_endpoint('GET', f'/api/pharmacist/medicines/{medicine_id}/', description="Get medicine details")
            
            # PUT - Update
            medicine_data['unit_price'] = 30.00
            tester.test_endpoint('PUT', f'/api/pharmacist/medicines/{medicine_id}/', medicine_data, "Update medicine (PUT)")
            
            # PATCH - Partial update
            tester.test_endpoint('PATCH', f'/api/pharmacist/medicines/{medicine_id}/', {'unit_price': 32.50}, "Partial update (PATCH)")
            
            # DELETE
            tester.test_endpoint('DELETE', f'/api/pharmacist/medicines/{medicine_id}/', description="Delete medicine")
    
    # ====================================================================
    # 5. PHARMACIST APP - Medicine Batches
    # ====================================================================
    tester.print_section("5. PHARMACIST - Medicine Batches")
    
    tester.test_endpoint('GET', '/api/pharmacist/batches/', description="List all batches")
    
    # ====================================================================
    # 6. PHARMACIST APP - Stock Movements
    # ====================================================================
    tester.print_section("6. PHARMACIST - Stock Movements")
    
    tester.test_endpoint('GET', '/api/pharmacist/stock-movements/', description="List all stock movements")
    
    # ====================================================================
    # 7. RECEPTIONIST APP - Patients
    # ====================================================================
    tester.print_section("7. RECEPTIONIST - Patients")
    
    tester.test_endpoint('GET', '/api/receptionist/patients/', description="List all patients")
    
    # ====================================================================
    # 8. RECEPTIONIST APP - Appointments
    # ====================================================================
    tester.print_section("8. RECEPTIONIST - Appointments")
    
    tester.test_endpoint('GET', '/api/receptionist/appointments/', description="List all appointments")
    
    # ====================================================================
    # 9. DOCTOR APP - Consultations
    # ====================================================================
    tester.print_section("9. DOCTOR - Consultations")
    
    tester.test_endpoint('GET', '/api/doctor/consultations/', description="List all consultations")
    
    # ====================================================================
    # 10. DOCTOR APP - Prescriptions
    # ====================================================================
    tester.print_section("10. DOCTOR - Prescriptions")
    
    tester.test_endpoint('GET', '/api/doctor/prescriptions/', description="List all prescriptions")
    
    # ====================================================================
    # 11. ADMIN APP - Staff
    # ====================================================================
    tester.print_section("11. ADMIN - Staff Management")
    
    tester.test_endpoint('GET', '/api/admin/staff/', description="List all staff")
    
    # Print final summary
    tester.print_final_summary()
    
    return tester.passed, tester.failed

if __name__ == "__main__":
    try:
        passed, failed = run_complete_tests()
        exit(0 if failed == 0 else 1)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test interrupted by user{RESET}\n")
        exit(1)
