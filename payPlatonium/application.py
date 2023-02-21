from flask import Flask, g, render_template, request, redirect, url_for, session, flash
import sqlite3
from users import create_database, create_table, insert_sample_users, check_user
from werkzeug.utils import secure_filename
from flask_session import Session
from page import generate_cover_page
import os

app = Flask(__name__)

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Define user types
USERS = 0
SUPPLIERS = 1
MANAGERS = 2

# Home page
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Authenticate user
        if username == 'admin' and password == 'password':
            return redirect(url_for('dashboard', role='admin'))
        elif username == 'manager' and password == 'password':
            return redirect(url_for('dashboard', role='manager'))
        else:
            message = 'Invalid username or password'
            return render_template('login.html', message=message)
    else:
        return render_template('login.html')
    
    


# Dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    role = request.args.get('role')

    if role == 'admin':
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Add a new user to the database
            try:
                connection = sqlite3.connect('users.db')
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                connection.commit()
                message = "User added successfully"
            except Exception as e:
                message = "An error occurred while adding the user. Error: {}".format(str(e))
                connection.rollback()
            finally:
                connection.close()

        # Query the database for user information
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        connection.close()

        return render_template('capture.html', users=users)

    elif role == 'manager':
        if request.method == 'POST':
            payment_id = request.form['payment_id']
            status = request.form['status']

            # Update the payment status in the database
            try:
                connection = sqlite3.connect('payments1.db')
                cursor = connection.cursor()
                cursor.execute("UPDATE payments SET status=? WHERE id=?", (status, payment_id))
                connection.commit()
                message = "Payment status updated successfully"
            except Exception as e:
                message = "An error occurred while updating the payment status. Error: {}".format(str(e))
                connection.rollback()
            finally:
                connection.close()

        # Query the database for payment information
        connection = sqlite3.connect('payments1.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM payments1")
        payments = cursor.fetchall()
        connection.close()

        return render_template('manager_dashboard.html', payments=payments)


def get_suppliers():
    conn = sqlite3.connect('suppliers1.db')
    c = conn.cursor()
    c.execute("SELECT * FROM suppliers")
    suppliers = c.fetchall()
    conn.close()
    return suppliers



@app.route('/capture', methods=['GET', 'POST'])
def capture():
    suppliers = get_suppliers()
    if request.method == 'POST':
        # process form data
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        department = request.form['department']
        date_of_invoice = request.form['date_of_invoice']
        date_of_payment_requested = request.form['date_of_payment_requested']
        payment_made_to = request.form['payment_made_to']
        company_name = request.form['company_name']
        payment_description = request.form['payment_description'] 
        bank_name = request.form['bank_name']
        acc_number = request.form['acc_number']
        branch_code = request.form['branch_code']
        amount = request.form['amount']
        
        # upload files
        invoice = request.files['invoice']
        #signature = request.files['signature']
        
        # Save the payment information to a database
        conn = sqlite3.connect('payments1.db')
        c = conn.cursor()
        c.execute("INSERT INTO payments1 (name, surname, email, department, date_of_invoice, date_of_payment_requested, payment_made_to, company_name, payment_description, bank_name, acc_number, branch_code, amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, surname, email, department, date_of_invoice, date_of_payment_requested, payment_made_to, company_name, payment_description, bank_name, acc_number, branch_code, amount))
        payment_id = c.lastrowid
        conn.commit()
        conn.close()
        
        # Save uploaded files to disk
        invoice_filename = secure_filename(invoice.filename)
        invoice_path = os.path.join('uploads', str(payment_id), 'invoice', invoice_filename)
        os.makedirs(os.path.dirname(invoice_path), exist_ok=True)
        invoice.save(invoice_path)

        #signature_filename = secure_filename(signature.filename)
        #signature_path = os.path.join('uploads', str(payment_id), 'signature', signature_filename)
        #os.makedirs(os.path.dirname(signature_path), exist_ok=True)
        #signature.save(signature_path)

        # Generate PDF cover page
        cover_page_path = os.path.join('uploads', str(payment_id), 'cover_page.pdf')
        generate_cover_page(cover_page_path, name, surname, email, department, date_of_invoice, date_of_payment_requested, payment_made_to, company_name, payment_description, bank_name, acc_number, branch_code, amount)
        
        # Redirect to manager approval page
        return redirect(url_for('display_select_suppliers', payment_id=payment_id))
        
    return render_template("capture.html", suppliers=suppliers)

# Define a function to get a connection to the payments database
def get_payments_connection():
    conn = getattr(g, '_payments_conn', None)
    if conn is None:
        conn = sqlite3.connect('payments1.db')
        g._payments_conn = conn
    return conn

# Define a function to get a connection to the suppliers database
def get_suppliers_connection():
    conn = getattr(g, '_suppliers_conn', None)
    if conn is None:
        conn = sqlite3.connect('suppliers1.db')
        g._suppliers_conn = conn
    return conn

# Define route for displaying suppliers with pending payments
@app.route('/display_select_suppliers', methods=['GET', 'POST'])
def display_select_suppliers():
    if request.method == 'POST':
        # Get the supplier ID from the form
        supplier_id = request.form['supplier_id']

        # Connect to the payments database and update the status for the given supplier ID
        conn = get_payments_connection()
        c = conn.cursor()
        c.execute("UPDATE payments1 SET status = 'pending' WHERE supplier_id = ?", (supplier_id,))
        conn.commit()

        # Redirect the user to the track_payments page with a success message
        flash('Supplier selected and sent for manager approval!')
        return redirect(url_for('track_payments'))

    # Get all suppliers with pending payments
    conn = get_suppliers_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM suppliers WHERE id IN (SELECT supplier_id FROM payments1 WHERE status = 'pending')")
    suppliers = c.fetchall()

    # Close connections
    c.close()

    return render_template("display_select_suppliers.html", suppliers=suppliers)

#@app.route('/suppliers/pending-payments')
#def display_select_suppliers():
    # Get all suppliers with pending payments
#    suppliers_c.execute("SELECT * FROM suppliers WHERE id IN (SELECT supplier_id FROM payments1 WHERE status = 'pending')")
#    suppliers = suppliers_c.fetchall()
    
    # Close connections
#    suppliers_conn.close()
#    payments_conn.close()
    
    # Render template with suppliers data
#    return render_template('suppliers.html', suppliers=suppliers)



@app.route('/manage_payments', methods=['GET', 'POST'])
def manage_payments():
    if request.method == 'POST':
        # Get the IDs and approval statuses from the form
        ids = request.form.getlist('id')
        statuses = request.form.getlist('status')

        # Update the payment statuses in the database
        conn = sqlite3.connect('payments1.db')
        c = conn.cursor()
        for i in range(len(ids)):
            c.execute("UPDATE payments1 SET status = ? WHERE id = ?", (statuses[i], ids[i]))
        conn.commit()
        conn.close()

        # Redirect the user to the track_payments page with a success message
        flash('Payment statuses updated!')
        return redirect(url_for('track_payments'))

    # Connect to the suppliers and payments databases and get all the suppliers with pending payments
    conn = sqlite3.connect('suppliers1.db')
    c = conn.cursor()
    c.execute("SELECT * FROM suppliers WHERE id IN (SELECT supplier_id FROM payments1 WHERE status = 'pending')")
    suppliers = c.fetchall()
    conn.close()

    # Get the payment information for the pending payments
    conn = sqlite3.connect('payments1.db')
    c = conn.cursor()
    c.execute("SELECT * FROM payments1 WHERE status = 'pending'")
    payments = c.fetchall()
    conn.close()

    return render_template("manage_payments.html", suppliers=suppliers, payments=payments)




@app.route('/track_payments', methods=['GET', 'POST'])
def track_payments():
    suppliers = get_suppliers()
    if request.method == 'POST':
         
        name = request.form['name']
        amount = request.form['amount']
        date_of_payment_requested = request.form['date_of_payment_requested']
        manager_approval = request.form.get('manager_approval')

        # Validate the input data
        if name and amount and date_of_payment_requested:
            # Insert the payment data into the database
            try:
                connection = sqlite3.connect('suppliers1.db')
                cursor = connection.cursor()
                cursor.execute("INSERT INTO payments (supplier_name, payment_amount, payment_date, manager_approval) VALUES (?, ?, ?, ?)", (name, amount, date_of_payment_requested, manager_approval))
                connection.commit()
                message = "Payment tracked successfully"
            except Exception as e:
                message = "An error occurred while tracking the payment. Error: {}".format(str(e))
                connection.rollback()
            finally:
                connection.close()
            
            if manager_approval:
                return redirect(url_for('process_payment'))
        else:
            message = "Please enter all the required details"
    else:
        message = ""

    return render_template('track_payments.html', suppliers=suppliers, message=message)


@app.route('/process_payment', methods=['GET', 'POST'])
def process_payment():
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        description = request.form.get('description', '')
        manager_name = request.form.get('manager_name', '')
        manager_signature = request.form.get('manager_signature', '')
        
        invoice = request.files['invoice']
        invoice_filename = secure_filename(invoice.filename)
        invoice.save(os.path.join('invoices', invoice_filename))
    
        # Add processing logic here
   
        return render_template('index.html')

# Run the app
if __name__ == '__main__':
    create_database()
    create_table()
    insert_sample_users()
    app.run(debug=True)
    

