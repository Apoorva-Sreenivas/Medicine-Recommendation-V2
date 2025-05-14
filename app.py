from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
import sqlite3
from llm_response import get_response
from chatbot_handler import chat_with_llm


app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_PATH = 'healthcare.db'


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


@app.route('/patient/<int:patient_id>/dashboard')
def patient_dashboard(patient_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT * FROM patient_details WHERE patient_id = ?", (patient_id,))
    patient = cur.fetchone()

    # Fetch previous AI interactions
    cur.execute('''
        SELECT timestamp, llm_output FROM interactions
        WHERE patient_id = ?
        ORDER BY timestamp DESC
        LIMIT 5
    ''', (patient_id,))
    sessions = cur.fetchall()

    conn.close()
    return render_template("patient_dashboard.html", patient=patient, sessions=sessions)



@app.route('/patient/<int:patient_id>/llm-predict', methods=['GET', 'POST'])
def llm_predict(patient_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get patient details and medical history
    cur.execute("SELECT * FROM patient_details WHERE patient_id = ?", (patient_id,))
    patient = cur.fetchone()

    cur.execute("SELECT symptoms FROM interactions WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 2", (patient_id,))
    recent_symptoms = [row[0] for row in cur.fetchall()]

    if not patient:
        flash("Patient not found", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Handle JSON fetch POST request from JavaScript
        data = request.get_json()
        symptoms = data.get('symptoms', [])
        history = patient[6]  # Adjust if needed

        # Generate structured response from LLM
        response_data = get_response(symptoms, history, recent_symptoms)

        # Store interaction
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        symptoms_str = ",".join(symptoms)

        cur.execute('''
        INSERT INTO interactions (patient_id, symptoms, timestamp, llm_output)
        VALUES (?, ?, ?, ?) 
    ''', (patient_id, symptoms_str, timestamp, response_data['disease']))

        conn.commit()
        conn.close()

        # ✅ Return JSON instead of re-rendering the template
        return jsonify(response_data)

    # For GET, render the prediction UI
    conn.close()
    return render_template("llm_predict.html", patient=patient)


@app.route("/chatbot", methods=["POST"])
def chatbot():
    # Get the actual patient_id from the request body
    patient_id = request.json.get("patient_id")
    if not patient_id:
        return jsonify({"error": "Patient ID not provided"}), 400

    user_message = request.json.get("message", "")
    
    # Function to chat with the LLM (assuming this function is defined elsewhere)
    response = chat_with_llm(patient_id, user_message)
    
    return jsonify({"reply": response})


@app.route('/view', methods=['GET', 'POST'])
def view():
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
    # NEW: Fetch recent AI predictions for all patients
    cursor.execute('''
        SELECT p.patient_id, p.name, i.timestamp, i.llm_output
        FROM interactions i
        JOIN patient_details p ON i.patient_id = p.patient_id
        ORDER BY i.timestamp DESC
        LIMIT 20
    ''')
    predictions = cursor.fetchall()
    
    conn.close()

    return render_template("view.html", patients=patients,predictions=predictions)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/help')
def help():
    return render_template('help.html')

if __name__ == '__main__':
    app.run(debug=True)