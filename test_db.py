import sqlite3

def view_patient_data():
    conn = sqlite3.connect("healthcare.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patient_details")
    rows = cursor.fetchall()

    if rows:
        for row in rows:
            print(row)
    else:
        print("No patient records found.")

    conn.close()

if __name__ == "__main__":
    view_patient_data()
