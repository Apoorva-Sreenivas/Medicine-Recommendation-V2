import sqlite3

def create_database():
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect("healthcare.db")
    cursor = conn.cursor()

    # Table 1: Login Information
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS login (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        password TEXT NOT NULL
    )
    ''')

    # Table 2: Patient Details
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patient_details (
        patient_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        sex TEXT NOT NULL CHECK (sex IN ('M', 'F', 'Other')),
        height REAL,
        weight REAL,
        medical_history TEXT,
        FOREIGN KEY (patient_id) REFERENCES login(patient_id) ON DELETE CASCADE
    )
    ''')

    # Table 3: Session Records and Predictions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recommendation_sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        session_date TEXT NOT NULL,  -- Format: YYYY-MM-DD
        predicted_disease TEXT NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES login(patient_id) ON DELETE CASCADE
    )
    ''')

    # Commit and close
    conn.commit()
    conn.close()
    print("Database and tables created successfully.")

import sqlite3

def create_admin_table():
    conn = sqlite3.connect("healthcare.db")
    cursor = conn.cursor()

    # Create admin table (if not exists)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    # Insert a single admin (if not exists)
    cursor.execute("SELECT * FROM admin WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("admin", "adminpass"))

    conn.commit()
    conn.close()
    print("Admin table created and default admin added.")


def clear_db():
    conn = sqlite3.connect('healthcare.db')
    cur = conn.cursor()

    # Clear all data from tables
    # cur.execute("DELETE FROM login")
    cur.execute("DELETE FROM patient_details")
    # cur.execute("DELETE FROM admin")  # If you have an admin table

    conn.commit()
    conn.close()

    print("Database cleared.")



if __name__ == "__main__":
    # create_admin_table()
    # clear_db()


# if __name__ == "__main__":
#     create_database()


