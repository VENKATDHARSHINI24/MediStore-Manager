import sqlite3
import os
from datetime import datetime, timedelta
import random
DB_PATH = os.path.join('database', 'medicine_stock.db')

medicines = [
    {
        'name': 'Paracetamol 500mg',
        'description': 'Pain reliever and fever reducer',
        'category': 'Tablet',
        'quantity': 150,
        'unit': 'Tablets',
        'manufacturer': 'PharmaCorp',
        'batch_number': 'PCM2023-001',
        'purchase_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'expiry_date': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
        'price': 5.99
    },
    {
        'name': 'Amoxicillin 250mg',
        'description': 'Antibiotic for bacterial infections',
        'category': 'Capsule',
        'quantity': 60,
        'unit': 'Capsules',
        'manufacturer': 'MediPharm',
        'batch_number': 'AMX2023-002',
        'purchase_date': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
        'expiry_date': (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d'),
        'price': 12.50
    },
    {
        'name': 'Ibuprofen 400mg',
        'description': 'NSAID for pain and inflammation',
        'category': 'Tablet',
        'quantity': 100,
        'unit': 'Tablets',
        'manufacturer': 'HealthMeds',
        'batch_number': 'IBU2023-003',
        'purchase_date': (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d'),
        'expiry_date': (datetime.now() + timedelta(days=730)).strftime('%Y-%m-%d'),
        'price': 7.25
    },
    {
        'name': 'Cetirizine 10mg',
        'description': 'Antihistamine for allergies',
        'category': 'Tablet',
        'quantity': 30,
        'unit': 'Tablets',
        'manufacturer': 'AllergyRelief',
        'batch_number': 'CET2023-004',
        'purchase_date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
        'expiry_date': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
        'price': 8.99
    },
    {
        'name': 'Omeprazole 20mg',
        'description': 'Proton pump inhibitor for acid reflux',
        'category': 'Capsule',
        'quantity': 28,
        'unit': 'Capsules',
        'manufacturer': 'GastroHealth',
        'batch_number': 'OME2023-005',
        'purchase_date': (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d'),
        'expiry_date': (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
        'price': 14.75
    },
    {
        'name': 'Metformin 500mg',
        'description': 'Oral diabetes medication',
        'category': 'Tablet',
        'quantity': 90,
        'unit': 'Tablets',
        'manufacturer': 'DiabeCare',
        'batch_number': 'MET2023-006',
        'purchase_date': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
        'expiry_date': (datetime.now() + timedelta(days=450)).strftime('%Y-%m-%d'),
        'price': 9.50
    },
    {
        'name': 'Salbutamol Inhaler',
        'description': 'Bronchodilator for asthma',
        'category': 'Inhaler',
        'quantity': 5,
        'unit': 'Inhalers',
        'manufacturer': 'RespiCare',
        'batch_number': 'SAL2023-007',
        'purchase_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
        'expiry_date': (datetime.now() + timedelta(days=300)).strftime('%Y-%m-%d'),
        'price': 22.99
    },
    {
        'name': 'Aspirin 75mg',
        'description': 'Blood thinner',
        'category': 'Tablet',
        'quantity': 28,
        'unit': 'Tablets',
        'manufacturer': 'CardioHealth',
        'batch_number': 'ASP2023-008',
        'purchase_date': (datetime.now() - timedelta(days=25)).strftime('%Y-%m-%d'),
        'expiry_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
        'price': 4.25
    },
    {
        'name': 'Diazepam 5mg',
        'description': 'Benzodiazepine for anxiety',
        'category': 'Tablet',
        'quantity': 10,
        'unit': 'Tablets',
        'manufacturer': 'NeuroCare',
        'batch_number': 'DIA2023-009',
        'purchase_date': (datetime.now() - timedelta(days=40)).strftime('%Y-%m-%d'),
        'expiry_date': (datetime.now() + timedelta(days=270)).strftime('%Y-%m-%d'),
        'price': 18.50
    },
    {
        'name': 'Hydrocortisone Cream 1%',
        'description': 'Topical steroid for skin inflammation',
        'category': 'Cream',
        'quantity': 3,
        'unit': 'Tubes',
        'manufacturer': 'DermaCare',
        'batch_number': 'HYD2023-010',
        'purchase_date': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
        'expiry_date': (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d'),
        'price': 11.25
    }
]

suppliers = [
    {
        'name': 'MediSupply Inc.',
        'contact_person': 'John Smith',
        'phone': '555-123-4567',
        'email': 'john@medisupply.com',
        'address': '123 Pharma Street, Medical District, City'
    },
    {
        'name': 'Global Pharmaceuticals',
        'contact_person': 'Sarah Johnson',
        'phone': '555-987-6543',
        'email': 'sarah@globalpharma.com',
        'address': '456 Health Avenue, Wellness Park, City'
    },
    {
        'name': 'Healthcare Distributors',
        'contact_person': 'Michael Brown',
        'phone': '555-456-7890',
        'email': 'michael@healthcaredist.com',
        'address': '789 Medicine Road, Care Center, City'
    }
]

def populate_sample_data():
    if not os.path.exists(DB_PATH):
        print("Database not found. Please run the main application first to create the database.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    
    medicine_count = cursor.execute('SELECT COUNT(*) FROM medicines').fetchone()[0]
    if medicine_count > 0:
        print("Database already contains data. Skipping sample data insertion.")
        conn.close()
        return
    
    
    for medicine in medicines:
        cursor.execute('''
        INSERT INTO medicines (name, description, category, quantity, unit, manufacturer, 
                              batch_number, purchase_date, expiry_date, price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (medicine['name'], medicine['description'], medicine['category'], 
              medicine['quantity'], medicine['unit'], medicine['manufacturer'], 
              medicine['batch_number'], medicine['purchase_date'], medicine['expiry_date'], 
              medicine['price']))
        
        
        medicine_id = cursor.lastrowid
        cursor.execute('''
        INSERT INTO transactions (medicine_id, transaction_type, quantity, notes, transaction_date)
        VALUES (?, ?, ?, ?, ?)
        ''', (medicine_id, 'add', medicine['quantity'], f'Initial stock of {medicine["name"]}', 
              (datetime.now() - timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d %H:%M:%S')))
    
    
    for supplier in suppliers:
        cursor.execute('''
        INSERT INTO suppliers (name, contact_person, phone, email, address)
        VALUES (?, ?, ?, ?, ?)
        ''', (supplier['name'], supplier['contact_person'], supplier['phone'], 
              supplier['email'], supplier['address']))
    
   
    for i in range(20):
        medicine_id = random.randint(1, len(medicines))
        transaction_type = random.choice(['add', 'remove'])
        quantity = random.randint(1, 20)
        days_ago = random.randint(1, 30)
        transaction_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        if transaction_type == 'add':
            notes = f'Restocked {quantity} units'
        else:
            notes = f'Dispensed {quantity} units'
        
        cursor.execute('''
        INSERT INTO transactions (medicine_id, transaction_type, quantity, notes, transaction_date)
        VALUES (?, ?, ?, ?, ?)
        ''', (medicine_id, transaction_type, quantity, notes, transaction_date))
    
    conn.commit()
    conn.close()
    
    print("Sample data has been successfully added to the database!")

if __name__ == "__main__":
    populate_sample_data()