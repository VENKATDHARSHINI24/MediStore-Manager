from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'medicine_stock_management_secret_key'

# Database setup
DB_PATH = os.path.join('database', 'medicine_stock.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create medicines table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        quantity INTEGER NOT NULL,
        unit TEXT,
        manufacturer TEXT,
        batch_number TEXT,
        purchase_date TEXT,
        expiry_date TEXT NOT NULL,
        price REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create suppliers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact_person TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER,
        transaction_type TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        transaction_date TEXT DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (medicine_id) REFERENCES medicines (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
if not os.path.exists('database'):
    os.makedirs('database')
init_db()

# Helper functions
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_expiring_medicines(days=30):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    today_date = datetime.now().date()
    
    # Get medicines expiring within the specified days
    cursor.execute('''
    SELECT * FROM medicines 
    WHERE date(expiry_date) <= date(?, '+' || ? || ' days') 
    AND quantity > 0
    ORDER BY expiry_date
    ''', (today, days))
    
    medicines = cursor.fetchall()
    
    # Convert to list of dictionaries and add days_left
    result = []
    for medicine in medicines:
        med_dict = dict(medicine)
        try:
            expiry_date = datetime.strptime(medicine['expiry_date'], '%Y-%m-%d').date()
            days_left = (expiry_date - today_date).days
            med_dict['days_left'] = days_left
        except (ValueError, TypeError):
            med_dict['days_left'] = None
        result.append(med_dict)
    
    conn.close()
    return result

def get_low_stock_medicines(threshold=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM medicines WHERE quantity <= ? ORDER BY quantity', (threshold,))
    
    medicines = cursor.fetchall()
    conn.close()
    return medicines

# Routes
@app.route('/')
def index():
    conn = get_db_connection()
    
    # Get total medicine count
    total_medicines = conn.execute('SELECT COUNT(*) FROM medicines').fetchone()[0]
    
    # Get expiring medicines count (within 90 days)
    expiring_medicines = len(get_expiring_medicines(90))
    
    # Get low stock medicines count
    low_stock_medicines = len(get_low_stock_medicines())
    
    # Get recent transactions
    recent_transactions = conn.execute('''
    SELECT t.*, m.name as medicine_name 
    FROM transactions t 
    JOIN medicines m ON t.medicine_id = m.id 
    ORDER BY t.transaction_date DESC LIMIT 5
    ''').fetchall()
    
    # Get expiring soon medicines
    expiring_soon = get_expiring_medicines(30)
    
    conn.close()
    
    return render_template('index.html', 
                          total_medicines=total_medicines,
                          expiring_medicines=expiring_medicines,
                          low_stock_medicines=low_stock_medicines,
                          recent_transactions=recent_transactions,
                          expiring_soon=expiring_soon)

@app.route('/medicines')
def medicines():
    conn = get_db_connection()
    medicines_data = conn.execute('SELECT * FROM medicines ORDER BY name').fetchall()
    conn.close()
    
    # Calculate days left for each medicine
    today_date = datetime.now().date()
    medicines = []
    for medicine in medicines_data:
        med_dict = dict(medicine)
        try:
            expiry_date = datetime.strptime(medicine['expiry_date'], '%Y-%m-%d').date()
            days_left = (expiry_date - today_date).days
            med_dict['days_left'] = days_left
        except (ValueError, TypeError):
            med_dict['days_left'] = None
        medicines.append(med_dict)
    
    return render_template('medicines.html', medicines=medicines)

@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        quantity = request.form['quantity']
        unit = request.form['unit']
        manufacturer = request.form['manufacturer']
        batch_number = request.form['batch_number']
        purchase_date = request.form['purchase_date']
        expiry_date = request.form['expiry_date']
        price = request.form['price']
        
        if not name or not quantity or not expiry_date:
            flash('Name, quantity, and expiry date are required fields!', 'danger')
            return redirect(url_for('add_medicine'))
        
        conn = get_db_connection()
        conn.execute('''
        INSERT INTO medicines (name, description, category, quantity, unit, manufacturer, 
                              batch_number, purchase_date, expiry_date, price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, category, quantity, unit, manufacturer, 
              batch_number, purchase_date, expiry_date, price))
        
        # Add transaction record
        medicine_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.execute('''
        INSERT INTO transactions (medicine_id, transaction_type, quantity, notes)
        VALUES (?, ?, ?, ?)
        ''', (medicine_id, 'add', quantity, f'Initial stock of {name}'))
        
        conn.commit()
        conn.close()
        
        flash('Medicine added successfully!', 'success')
        return redirect(url_for('medicines'))
    
    return render_template('add_medicine.html')

@app.route('/edit_medicine/<int:id>', methods=['GET', 'POST'])
def edit_medicine(id):
    conn = get_db_connection()
    medicine = conn.execute('SELECT * FROM medicines WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        quantity = request.form['quantity']
        unit = request.form['unit']
        manufacturer = request.form['manufacturer']
        batch_number = request.form['batch_number']
        purchase_date = request.form['purchase_date']
        expiry_date = request.form['expiry_date']
        price = request.form['price']
        
        if not name or not quantity or not expiry_date:
            flash('Name, quantity, and expiry date are required fields!', 'danger')
            return redirect(url_for('edit_medicine', id=id))
        
        # Get old quantity to calculate difference
        old_quantity = medicine['quantity']
        new_quantity = int(quantity)
        quantity_diff = new_quantity - old_quantity
        
        conn.execute('''
        UPDATE medicines
        SET name = ?, description = ?, category = ?, quantity = ?, unit = ?, 
            manufacturer = ?, batch_number = ?, purchase_date = ?, expiry_date = ?, price = ?
        WHERE id = ?
        ''', (name, description, category, quantity, unit, manufacturer, 
              batch_number, purchase_date, expiry_date, price, id))
        
        # Add transaction record if quantity changed
        if quantity_diff != 0:
            transaction_type = 'add' if quantity_diff > 0 else 'remove'
            conn.execute('''
            INSERT INTO transactions (medicine_id, transaction_type, quantity, notes)
            VALUES (?, ?, ?, ?)
            ''', (id, transaction_type, abs(quantity_diff), f'Updated stock of {name}'))
        
        conn.commit()
        conn.close()
        
        flash('Medicine updated successfully!', 'success')
        return redirect(url_for('medicines'))
    
    conn.close()
    return render_template('edit_medicine.html', medicine=medicine)

@app.route('/delete_medicine/<int:id>', methods=['POST'])
def delete_medicine(id):
    conn = get_db_connection()
    medicine = conn.execute('SELECT * FROM medicines WHERE id = ?', (id,)).fetchone()
    
    if medicine:
        conn.execute('DELETE FROM medicines WHERE id = ?', (id,))
        conn.execute('DELETE FROM transactions WHERE medicine_id = ?', (id,))
        conn.commit()
        flash('Medicine deleted successfully!', 'success')
    else:
        flash('Medicine not found!', 'danger')
    
    conn.close()
    return redirect(url_for('medicines'))

@app.route('/update_stock/<int:id>', methods=['GET', 'POST'])
def update_stock(id):
    conn = get_db_connection()
    medicine = conn.execute('SELECT * FROM medicines WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        quantity_change = int(request.form['quantity_change'])
        transaction_type = request.form['transaction_type']
        notes = request.form['notes']
        
        if transaction_type == 'remove' and quantity_change > medicine['quantity']:
            flash('Cannot remove more than available stock!', 'danger')
            conn.close()
            return redirect(url_for('update_stock', id=id))
        
        # Update medicine quantity
        new_quantity = medicine['quantity'] + quantity_change if transaction_type == 'add' else medicine['quantity'] - quantity_change
        
        conn.execute('UPDATE medicines SET quantity = ? WHERE id = ?', (new_quantity, id))
        
        # Add transaction record
        conn.execute('''
        INSERT INTO transactions (medicine_id, transaction_type, quantity, notes)
        VALUES (?, ?, ?, ?)
        ''', (id, transaction_type, quantity_change, notes))
        
        conn.commit()
        conn.close()
        
        flash('Stock updated successfully!', 'success')
        return redirect(url_for('medicines'))
    
    conn.close()
    return render_template('update_stock.html', medicine=medicine)

@app.route('/transactions')
def transactions():
    conn = get_db_connection()
    transactions = conn.execute('''
    SELECT t.*, m.name as medicine_name 
    FROM transactions t 
    JOIN medicines m ON t.medicine_id = m.id 
    ORDER BY t.transaction_date DESC
    ''').fetchall()
    conn.close()
    return render_template('transactions.html', transactions=transactions)

@app.route('/expiring')
def expiring():
    days = request.args.get('days', 90, type=int)
    expiring_medicines = get_expiring_medicines(days)
    
    return render_template('expiring.html', medicines=expiring_medicines, days=days)

@app.route('/low_stock')
def low_stock():
    threshold = request.args.get('threshold', 10, type=int)
    low_stock_medicines = get_low_stock_medicines(threshold)
    
    # Calculate days left for each medicine
    today_date = datetime.now().date()
    medicines = []
    for medicine in low_stock_medicines:
        med_dict = dict(medicine)
        try:
            expiry_date = datetime.strptime(medicine['expiry_date'], '%Y-%m-%d').date()
            days_left = (expiry_date - today_date).days
            med_dict['days_left'] = days_left
        except (ValueError, TypeError):
            med_dict['days_left'] = None
        medicines.append(med_dict)
    
    return render_template('low_stock.html', medicines=medicines, threshold=threshold)

@app.route('/suppliers')
def suppliers():
    conn = get_db_connection()
    suppliers = conn.execute('SELECT * FROM suppliers ORDER BY name').fetchall()
    conn.close()
    return render_template('suppliers.html', suppliers=suppliers)

@app.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        name = request.form['name']
        contact_person = request.form['contact_person']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        
        if not name:
            flash('Supplier name is required!', 'danger')
            return redirect(url_for('add_supplier'))
        
        conn = get_db_connection()
        conn.execute('''
        INSERT INTO suppliers (name, contact_person, phone, email, address)
        VALUES (?, ?, ?, ?, ?)
        ''', (name, contact_person, phone, email, address))
        
        conn.commit()
        conn.close()
        
        flash('Supplier added successfully!', 'success')
        return redirect(url_for('suppliers'))
    
    return render_template('add_supplier.html')

@app.route('/edit_supplier/<int:id>', methods=['GET', 'POST'])
def edit_supplier(id):
    conn = get_db_connection()
    supplier = conn.execute('SELECT * FROM suppliers WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        name = request.form['name']
        contact_person = request.form['contact_person']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        
        if not name:
            flash('Supplier name is required!', 'danger')
            return redirect(url_for('edit_supplier', id=id))
        
        conn.execute('''
        UPDATE suppliers
        SET name = ?, contact_person = ?, phone = ?, email = ?, address = ?
        WHERE id = ?
        ''', (name, contact_person, phone, email, address, id))
        
        conn.commit()
        conn.close()
        
        flash('Supplier updated successfully!', 'success')
        return redirect(url_for('suppliers'))
    
    conn.close()
    return render_template('edit_supplier.html', supplier=supplier)

@app.route('/delete_supplier/<int:id>', methods=['POST'])
def delete_supplier(id):
    conn = get_db_connection()
    supplier = conn.execute('SELECT * FROM suppliers WHERE id = ?', (id,)).fetchone()
    
    if supplier:
        conn.execute('DELETE FROM suppliers WHERE id = ?', (id,))
        conn.commit()
        flash('Supplier deleted successfully!', 'success')
    else:
        flash('Supplier not found!', 'danger')
    
    conn.close()
    return redirect(url_for('suppliers'))

@app.route('/search')
def search():
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('medicines'))
    
    conn = get_db_connection()
    medicines_data = conn.execute('''
    SELECT * FROM medicines 
    WHERE name LIKE ? OR description LIKE ? OR category LIKE ? OR manufacturer LIKE ?
    ORDER BY name
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
    
    conn.close()
    
    # Calculate days left for each medicine
    today_date = datetime.now().date()
    medicines = []
    for medicine in medicines_data:
        med_dict = dict(medicine)
        try:
            expiry_date = datetime.strptime(medicine['expiry_date'], '%Y-%m-%d').date()
            days_left = (expiry_date - today_date).days
            med_dict['days_left'] = days_left
        except (ValueError, TypeError):
            med_dict['days_left'] = None
        medicines.append(med_dict)
    
    return render_template('search_results.html', medicines=medicines, query=query)

@app.route('/api/expiring_medicines')
def api_expiring_medicines():
    days = request.args.get('days', 90, type=int)
    expiring_medicines = get_expiring_medicines(days)
    
    result = []
    for medicine in expiring_medicines:
        result.append({
            'id': medicine['id'],
            'name': medicine['name'],
            'quantity': medicine['quantity'],
            'expiry_date': medicine['expiry_date'],
            'days_left': medicine.get('days_left')
        })
    
    return jsonify(result)

@app.route('/discount_offers')
def discount_offers():
    # Get medicines expiring within 15 days
    expiring_medicines = get_expiring_medicines(15)
    
    # Calculate recommended discount based on days left
    for medicine in expiring_medicines:
        days_left = medicine.get('days_left', 0)
        if days_left <= 5:
            # 50% discount for medicines expiring in 5 days or less
            medicine['recommended_discount'] = 50
        elif days_left <= 10:
            # 30% discount for medicines expiring in 6-10 days
            medicine['recommended_discount'] = 30
        else:
            # 15% discount for medicines expiring in 11-15 days
            medicine['recommended_discount'] = 15
            
        # Calculate discounted price
        try:
            if medicine['price']:
                original_price = float(medicine['price'])
                discount_percent = medicine['recommended_discount']
                medicine['discounted_price'] = round(original_price * (1 - discount_percent/100), 2)
            else:
                medicine['discounted_price'] = None
        except (ValueError, TypeError):
            # Handle any conversion errors
            medicine['discounted_price'] = None
    
    return render_template('discount_offers.html', medicines=expiring_medicines)

if __name__ == '__main__':
    app.run(debug=True)