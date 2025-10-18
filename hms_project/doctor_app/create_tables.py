from django.db import connection

def create_doctor_tables():
    with connection.cursor() as cursor:
        # 1. Create Consultation table WITHOUT foreign keys first
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor_app_consultation (
            id INT AUTO_INCREMENT PRIMARY KEY,
            appointment_id INT NOT NULL,
            doctor_id INT NOT NULL,
            patient_id INT NOT NULL,
            consultation_date DATETIME(6) NOT NULL,
            diagnosis LONGTEXT,
            symptoms LONGTEXT,
            notes LONGTEXT,
            follow_up_date DATE,
            status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
            created_at DATETIME(6) NOT NULL,
            updated_at DATETIME(6) NOT NULL
        );
        """)
        
        # 2. Create Prescription table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor_app_prescription (
            id INT AUTO_INCREMENT PRIMARY KEY,
            consultation_id INT NOT NULL,
            prescription_date DATE NOT NULL,
            notes LONGTEXT,
            is_active TINYINT(1) NOT NULL DEFAULT 1,
            created_at DATETIME(6) NOT NULL,
            updated_at DATETIME(6) NOT NULL
        );
        """)
        
        # 3. Create MedicinePrescription table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor_app_medicineprescription (
            id INT AUTO_INCREMENT PRIMARY KEY,
            prescription_id INT NOT NULL,
            medicine_id INT NOT NULL,
            dosage VARCHAR(100) NOT NULL,
            frequency VARCHAR(100) NOT NULL,
            duration VARCHAR(50) NOT NULL,
            instructions LONGTEXT,
            quantity INT NOT NULL DEFAULT 1
        );
        """)
        
        # 4. Create TestPrescription table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor_app_testprescription (
            id INT AUTO_INCREMENT PRIMARY KEY,
            prescription_id INT NOT NULL,
            test_id INT NOT NULL,
            instructions LONGTEXT,
            urgency VARCHAR(20) NOT NULL DEFAULT 'routine'
        );
        """)
        
    print("✅ All doctor_app tables created successfully!")

if __name__ == "__main__":
    create_doctor_tables()
