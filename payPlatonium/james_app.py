from flask import Flask, g, render_template, request, redirect, url_for, session, flash, Response
import sqlite3
from users import create_database, create_table, insert_sample_users, check_user
from werkzeug.utils import secure_filename
from flask_session import Session
from page import generate_cover_page
import os
import random
import pdfkit
import os.path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import make_response

from flask import send_file
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


from utils.pdf_utils import generate_pdf, generate_payment_pdf




app = Flask(__name__, static_url_path='/static')
# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "payments.db")

# Define user types
USERS = 0
SUPPLIERS = 1
MANAGERS = 2


# Home page
@app.route('/')
def home():
    return render_template('home.html')


# AI Analytics. thius is where we are going to upograde the system 
@app.route('/payment_analytics')
def payment_analytics():
    return render_template('payment_analytics.html')


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
                with sqlite3.connect('users.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    message = "User added successfully"
            except Exception as e:
                message = "An error occurred while adding the user. Error: {}".format(str(e))

        # Query the database for user information
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()

        return render_template('capture.html', users=users)

    elif role == 'manager':
        if request.method == 'POST':
            payment_id = request.form['payment_id']
            status = request.form['status']

            # Update the payment status in the database
            try:
                with sqlite3.connect('payments.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE payments SET status=? WHERE id=?", (status, payment_id))
                    message = "Payment status updated successfully"
            except Exception as e:
                message = "An error occurred while updating the payment status. Error: {}".format(str(e))

        # Query the database for payment information
        with sqlite3.connect('payments.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM payments")
            payments = cursor.fetchall()

        return render_template('manager_dashboard.html', payments=payments)




def get_suppliers():
    with get_suppliers_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM suppliers")
        suppliers = c.fetchall()
    return suppliers

def get_payments_connection():
    conn = getattr(g, '_payments_conn', None)
    if conn is None:
        conn = sqlite3.connect('payments.db')
        g._payments_conn = conn
    return conn

def get_suppliers_connection():
    conn = getattr(g, '_suppliers_conn', None)
    if conn is None:
        conn = sqlite3.connect('suppliers.db')
        g._suppliers_conn = conn
    return conn

def generate_payment_id():
    # Connect to the payments database and get the latest payment ID
    conn_payments = sqlite3.connect('payments.db')
    c_payments = conn_payments.cursor()
    c_payments.execute("SELECT MAX(id) FROM payments")
    result = c_payments.fetchone()[0]
    conn_payments.close()

    # Increment the latest payment ID by 1 to generate a new unique payment ID
    if result is not None:
        return result + 1
    else:
        return 1
    
@app.route('/capture', methods=['GET', 'POST'])
def capture():
    suppliers = get_suppliers()
    if request.method == 'POST':
        # process form data
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        department = request.form['department']
        company_name = request.form['company_name']
        bank_name = request.form['bank_name']
        acc_number = request.form['acc_number']
        branch_code = request.form['branch_code']
        
        # Connect to the suppliers database
        conn = sqlite3.connect('suppliers.db')
        cursor = conn.cursor()

        # Insert the captured data into the suppliers table
        cursor.execute('INSERT INTO suppliers (name, surname, email, department, company_name, bank_name, acc_number, branch_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                       (name, surname, email, department, company_name, bank_name, acc_number, branch_code))
        conn.commit()
        conn.close()

        # redirect to capture_payments function
        return redirect(url_for('capture_payments'))

    return render_template("capture.html", suppliers=suppliers)



@app.route('/capture_payments', methods=['GET', 'POST'])
def capture_payments():
    if request.method == 'POST':
        # Get the form data
        supplier_id = request.form['supplier_id']
        supplier_name = request.form['supplier_name']
        date_of_invoice = request.form['date_of_invoice']
        date_of_payment_requested = request.form['date_of_payment_requested']
        payment_description = request.form['payment_description']
        amount = request.form['amount']
        status = 'pending'
        invoice = request.files['invoice']

        # Save uploaded files to disk
        invoice_filename = secure_filename(invoice.filename)
        payment_id = generate_payment_id()
        invoice_path = os.path.join('uploads', str(payment_id), 'invoice', invoice_filename)
        os.makedirs(os.path.dirname(invoice_path), exist_ok=True)
        invoice.save(invoice_path)

        # Connect to the payments database and insert the new payment
        conn_payments = get_payments_connection()
        c_payments = conn_payments.cursor()
        c_payments.execute("INSERT INTO payments (supplier_id, supplier_name, date_of_invoice, date_of_payment_requested, payment_description, amount, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (supplier_id, supplier_name, date_of_invoice, date_of_payment_requested, payment_description, amount, status))
        conn_payments.commit()

        # Close the connections
        c_payments.close()
        conn_payments.close()

        # Generate the PDF document
        pdf_bytes = generate_pdf(payment_id, supplier_name, date_of_invoice, date_of_payment_requested, payment_description, amount, status)
        pdf_path = os.path.join('uploads', str(payment_id), 'payment.pdf')
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)

        flash('Payment captured and sent for manager approval!')
        return redirect(url_for('track_payments'))

    # Connect to the suppliers database and get all suppliers
    conn_suppliers = get_suppliers_connection()
    c_suppliers = conn_suppliers.cursor()
    c_suppliers.execute("SELECT * FROM suppliers")
    suppliers = c_suppliers.fetchall()

    # Close the connections
    c_suppliers.close()
    conn_suppliers.close()

    return render_template("capture_payments.html", suppliers=suppliers)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('payments.db')
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()




@app.route('/manager_dashboard', methods=['GET', 'POST'])
def manager_dashboard():
    db = get_db()
    print('is the pdf generated?')

    if request.method == 'POST':
        # Get form data
        payment_id = request.form['payment_id']
        supplier_name = request.form['supplier_name']
        amount = request.form['amount']
        status = request.form['status']
        signature = request.files['signature']

        # Save uploaded files to disk
        try:
            signature_filename = secure_filename(signature.filename)
            signature_path = os.path.join('static', signature_filename)
            signature.save(signature_path)
        except Exception as e:
            # Handle file save error
            return "Error: " + str(e)

        # Update payment status
        try:
            db.execute('UPDATE payments SET status=? WHERE id=?', [status, payment_id])
            db.commit()
        except Exception as e:
            # Handle database update error
            return "Error: " + str(e)

        # Get payment details
        try:
            cur = db.execute('SELECT payments.payment_description, suppliers.company_name FROM payments INNER JOIN suppliers ON payments.supplier_id = suppliers.id WHERE payments.id=?', [payment_id])
            payment = cur.fetchone()
        except Exception as e:
            # Handle database query error
            return "Error: " + str(e)

        payment = cur.fetchone()
        if payment is None:
            return "Error: payment not found"
        pdf = generate_payment_pdf(db, payment_id, payment['company_name'], amount, status, signature)

        # Save payment information and PDF to disk without signature
        pdf_path = os.path.join('uploads/payments', str(payment_id), 'payment_unsigned.pdf')
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        with open(pdf_path, 'wb') as f:
            f.write(pdf)

        # Open saved PDF and insert signature
        from PyPDF2 import PdfFileWriter, PdfFileReader
        output_pdf_path = os.path.join('uploads/payments', str(payment_id), 'payment_signed.pdf')
        output_pdf = PdfFileWriter()
        input_pdf_path = pdf_path
        with open(input_pdf_path, 'rb') as input_pdf_file:
            input_pdf = PdfFileReader(input_pdf_file)
            signature_page = input_pdf.getPage(0)
            signature_image = PdfFileReader(open(signature_path, 'rb')).getPage(0)
            signature_page.mergePage(signature_image)
            output_pdf.addPage(signature_page)
            with open(output_pdf_path, 'wb') as f:
                output_pdf.write(f)

        print('is the pdf generated?')
        return redirect(url_for('payment_confirmation', payment_id=payment_id))

    # Get pending payments
    cur = db.execute('SELECT payments.id, suppliers.name AS supplier_name, suppliers.company_name, payments.amount, payments.status FROM payments INNER JOIN suppliers ON payments.supplier_id = suppliers.id WHERE payments.status="pending" ORDER BY suppliers.name')
    payments = cur.fetchall()

    # Get payment IDs, supplier names, and amounts for dropdowns
    cur = db.execute('SELECT id FROM payments WHERE status="pending" ORDER BY id')
    payment_ids = [row['id'] for row in cur.fetchall()]

    cur = db.execute('SELECT name FROM suppliers ORDER BY name')
    supplier_names = [row['name'] for row in cur.fetchall()]

    cur = db.execute('SELECT amount FROM payments WHERE status="pending" ORDER BY amount')
    amounts = [row['amount'] for row in cur.fetchall()]

    return render_template('manager_dashboard.html', payments=payments, payment_ids=payment_ids, supplier_names=supplier_names, amounts=amounts)


@app.route('/payment_confirmation', methods=['GET', 'POST'])
def payment_confirmation(payment_id=None):
    # Check if payment_id is None or empty
    if payment_id is None or payment_id == '':
        return "Invalid payment ID"
    
    # Connect to the payments database and retrieve the payment information
    conn_payments = sqlite3.connect('payments.db')
    c_payments = conn_payments.cursor()
    c_payments.execute("SELECT * FROM payments WHERE payment_id=?", (payment_id,))
    payment = c_payments.fetchone()
    
    # Check if the payment status is already approved
    if payment is None:
        return "Payment not found"
    elif payment[4] == 'approved':
        return "Payment has already been approved"
    
    # Connect to the suppliers database and retrieve the supplier information
    conn_suppliers = sqlite3.connect('suppliers.db')
    c_suppliers = conn_suppliers.cursor()
    c_suppliers.execute("SELECT * FROM suppliers WHERE supplier_id=?", (payment[1],))
    supplier = c_suppliers.fetchone()
    
    # Update the payment status to approved in the payments database
    c_payments.execute("UPDATE payments SET status='approved' WHERE payment_id=?", (payment_id,))
    conn_payments.commit()
    
    # Render the payment confirmation template with the payment and supplier information
    return render_template('payment_confirmation.html', payment=payment, supplier=supplier)



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
                connection = sqlite3.connect('suppliers.db')
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
    




