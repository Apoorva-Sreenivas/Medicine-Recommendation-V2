from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_PATH = 'healthcare.db'

# Ensure database exists
if not os.path.exists(DB_PATH):
    import init_db  # This runs init_db.py to create the database and tables

import re



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        password = request.form['password']
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT * FROM login WHERE patient_id = ? AND password = ?", (patient_id, password))
        user = cur.fetchone()
        conn.close()
        
        if user:
            flash("Login successful", "success")
            return redirect(url_for('patient_dashboard', patient_id=patient_id))  # Use a new route for patient view
        else:
            flash("Invalid patient credentials", "danger")
    
    return render_template('login.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT * FROM admin WHERE username = ? AND password = ?", (username, password))
        admin = cur.fetchone()
        conn.close()

        if admin:
            flash("Admin login successful", "success")
            return redirect(url_for('view'))  # Only admin should go to this
        else:
            flash("Invalid admin credentials", "danger")
            
    return render_template('admin_login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        password = request.form['password']
        name = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        height = request.form['height']
        weight = request.form['weight']
        medical_history = request.form.get('medical_history', '')  # Use .get() to avoid KeyError

        # Validate password
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return render_template('register.html')

        # Store login info
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO login (password) VALUES (?)", (password,))
        patient_id = cur.lastrowid
        # Store patient details
        cur.execute('''
            INSERT INTO patient_details (patient_id, name, age, sex, height, weight, medical_history)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, name, age, sex, height, weight, medical_history))

        conn.commit()
        conn.close()
        flash("Registration successful!", "success")

        # return redirect(url_for('login'))  # Redirect after successful registration
        return render_template("register_success.html", patient_id=patient_id)

    return render_template('register.html')


@app.route('/patient/<int:patient_id>')
def patient_dashboard(patient_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM patient_details WHERE patient_id = ?", (patient_id,))
    patient = cur.fetchone()
    conn.close()

    if not patient:
        flash("Patient not found", "danger")
        return redirect(url_for('login'))

    return render_template('patient_dashboard.html', patient=patient)


@app.route('/view', methods=['GET', 'POST'])
def view():
    # Session check skipped – add later if login sessions are implemented

    # if 'admin_logged_in' not in session:
    #     flash("Unauthorized access. Please login as admin.", "danger")
    #     return redirect(url_for('admin_login'))

    filters = []
    values = []

    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        name = request.form.get('name')
        age = request.form.get('age')
        sex = request.form.get('sex')

        if patient_id:
            filters.append("pd.patient_id = ?")
            values.append(patient_id)
        if name:
            filters.append("pd.name LIKE ?")
            values.append(f"%{name}%")
        if age:
            filters.append("pd.age = ?")
            values.append(age)
        if sex and sex != 'Any':
            filters.append("pd.sex = ?")
            values.append(sex)

    query = """
    SELECT pd.patient_id, pd.name, pd.age, pd.sex, pd.height, pd.weight
    FROM patient_details pd
    """
    if filters:
        query += " WHERE " + " AND ".join(filters)

    conn = sqlite3.connect("healthcare.db")
    cursor = conn.cursor()
    cursor.execute(query, values)
    patients = cursor.fetchall()
    conn.close()

    return render_template("view.html", patients=patients)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/help')
def help():
    return render_template('help.html')

if __name__ == '__main__':
    app.run(debug=True)