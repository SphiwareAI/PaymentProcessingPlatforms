from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from users import create_database, create_table, insert_sample_users, check_user
from werkzeug.utils import secure_filename
from flask_session import Session
import os

app = Flask(__name__)

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

#app = Flask(__name__)
#app.secret_key = 'secret_key'

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username, password):
            session['username'] = username
            return redirect(url_for('capture'))
        else:
            return 'Invalid login. Please try again.'
    return render_template('login.html')

@app.route('/capture', methods=['GET', 'POST'])
def capture():
    if request.method == 'POST':
        # code to process form data
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
        
        # Save the payment information to a database or a file
        # Add the code here

        # Redirect to the "track_payment" page
        return redirect(url_for('track_payments'))

    # Query the database for supplier information
    conn = sqlite3.connect('suppliers1.db')
    c = conn.cursor()
    c.execute("SELECT * FROM suppliers")
    suppliers = c.fetchall()

    return render_template("capture.html", suppliers=suppliers)

def get_suppliers():
    try:
        connection = sqlite3.connect('suppliers1.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM suppliers")
        suppliers = cursor.fetchall()
    except Exception as e:
        print("An error occurred while fetching the suppliers data. Error: {}".format(str(e)))
        suppliers = []
    finally:
        connection.close()
    return suppliers

#@app.route('/track_payments', methods=['GET', 'POST'])

@app.route('/track_payments', methods=['GET', 'POST'])
def track_payments():
    if request.method == 'POST':
        suppliers = get_suppliers() 
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


if __name__ == '__main__':
    create_database()
    create_table()
    insert_sample_users()
    app.run(debug=True)


