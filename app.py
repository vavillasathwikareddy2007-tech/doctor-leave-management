from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "doctorproject"

# CREATE DATABASE TABLES

def create_tables():

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    # DOCTORS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_name TEXT,
        department TEXT,
        shift TEXT, 
        status TEXT,
        availability TEXT,
        emergency_available TEXT
    )
    ''')

    # LEAVE REQUEST TABLE
    cursor.execute("""
CREATE TABLE IF NOT EXISTS leave_requests (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    doctor_name TEXT,
    department TEXT,
    shift TEXT,

    leave_date TEXT,
    reason TEXT,

    status TEXT
)
""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS emergency_alerts(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    emergency_type TEXT,

    department TEXT,

    shift TEXT,

    status TEXT
)
""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS roster(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    doctor_name TEXT,

    monday TEXT,
    tuesday TEXT,
    wednesday TEXT,
    thursday TEXT,
    friday TEXT,
    saturday TEXT,
    sunday TEXT
)
""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS emergency_assignments(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    doctor_name TEXT,

    emergency_type TEXT,

    status TEXT
)
""")

    conn.commit()
    conn.close()

# CALL FUNCTION
create_tables()


# CREATE DATABASE TABLE

# HOME PAGE
@app.route('/')
def home():
    return render_template("index.html")

# LOGIN PAGE
@app.route('/login')
def login():
    return render_template("login.html")

# DASHBOARD PAGE
@app.route('/dashboard')
def dashboard():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    search = request.args.get('search')
    cursor.execute("SELECT COUNT(*) FROM doctors")

    total_doctors = cursor.fetchone()[0]

    # GET LEAVE REQUESTS
    cursor.execute("SELECT * FROM leave_requests Where status='Approved' ")
    leave_data = cursor.fetchall()

    # GET DOCTORS
    if search:

        cursor.execute(
            "SELECT * FROM doctors WHERE doctor_name LIKE ?",
            ('%' + search + '%',)
    )

    else:

        cursor.execute("SELECT * FROM doctors WHERE status='Active'")
    doctor_data = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        leave_requests=leave_data,
        doctors=doctor_data,
        total_doctors=total_doctors
    )

# SUBMIT LEAVE REQUEST
@app.route('/submit_leave', methods=['POST'])
def submit_leave():

    doctor_name = request.form['doctor_name']
    department = request.form['department']
    shift = request.form['shift']

    leave_date = request.form['leave_date']
    reason = request.form['reason']

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute(

        """
        INSERT INTO leave_requests
        (
            doctor_name,
            department,
            shift,
            leave_date,
            reason,
            status
        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,

        (
            doctor_name,
            department,
            shift,
            leave_date,
            reason,
            "Pending"
        )
    )

    conn.commit()
    conn.close()

    flash("Leave Request Submitted Successfully ✅")

    return redirect('/dashboard')

#ADD DOCTOR
@app.route('/add_doctor',methods=['POST'])
def add_doctor():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM doctors")

    doctors = cursor.fetchall()

    conn.close()

    return render_template(
        "add_doctor.html",
        doctors=doctors
    )

#SAVE DOCTOR
@app.route('/save_doctor', methods=['POST'])
def save_doctor():
    doctor_name = request.form['doctor_name']
    department = request.form['department']
    shift = request.form['shift']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
    "INSERT INTO doctors (doctor_name, department, shift, status, availability, emergency_available) VALUES (?, ?, ?, ?, ?, ?)",
    (doctor_name, department, shift, "Active", "Free", "Yes")
)

    conn.commit()
    conn.close()

    flash("Doctor Added Successfully ✅")
    return redirect('/dashboard')

# ROSTER PAGE
@app.route('/roster')
def roster():

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM doctors")

    doctors = cursor.fetchall()

    conn.close()

    return render_template(
        "roster.html",
        doctors=doctors
    )


# APPROVE LEAVE PAGE
@app.route('/approve_leave')
def approve_leave():

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM leave_requests")

    leaves = cursor.fetchall()

    conn.close()

    return render_template(
        "approve_leave.html",
        leaves=leaves
    )

# APPROVE LEAVE
@app.route('/approve/<int:id>')
def approve(id):

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute(
        "UPDATE leave_requests SET status='Approved' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/approve_leave')


# REJECT LEAVE
@app.route('/reject/<int:id>')
def reject(id):

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute(
        "UPDATE leave_requests SET status='Rejected' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/approve_leave')


# ADMIN PAGE
@app.route('/admin')
def admin():
    return render_template("admin.html")

# DELETE DOCTOR
@app.route('/delete_doctor/<int:id>')
def delete_doctor(id):

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute(

        """
        UPDATE doctors
        SET status='Inactive'
        WHERE id=?
        """,

        (id,)
    )

    conn.commit()
    conn.close()

    flash("Doctor moved to inactive state")

    return redirect('/dashboard')
@app.route('/inactive_doctors')
def inactive_doctors():

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM doctors WHERE status='Inactive'"
    )

    doctors = cursor.fetchall()

    conn.close()

    return render_template(
        "inactive_doctors.html",
        doctors=doctors
    )


@app.route('/restore_doctor/<int:id>')
def restore_doctor(id):

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute(

        """
        UPDATE doctors
        SET status='Active'
        WHERE id=?
        """,

        (id,)
    )

    conn.commit()
    conn.close()

    flash("Doctor Restored Successfully")

    return redirect('/inactive_doctors')

#EMERGENCY ROUTE
@app.route('/emergency')
def emergency():
    return render_template('emergency.html')

@app.route('/send_emergency', methods=['POST'])
def send_emergency():

    department = request.form['department']
    shift = request.form['shift']
    emergency_type = request.form['emergency']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Save emergency alert

    cursor.execute(
        """
        INSERT INTO emergency_alerts
        (
            emergency_type,
            department,
            shift,
            status
        )

        VALUES (?, ?, ?, ?)
        """,
        (
            emergency_type,
            department,
            shift,
            "Open"
        )
    )

    conn.commit()

    # Get all doctors

    cursor.execute(
        "SELECT * FROM doctors"
    )

    doctors = cursor.fetchall()

    # Get approved leave doctors

    cursor.execute(
        """
        SELECT * FROM leave_requests
        WHERE status='Approved'
        """
    )

    leave_doctors = cursor.fetchall()

    conn.close()

    return render_template(
        "emergency_result.html",
        doctors=doctors,
        leave_doctors=leave_doctors,
        emergency_type=emergency_type,
        department=department,
        shift=shift
    )

@app.route('/accept_emergency/<int:id>')
def accept_emergency(id):

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO emergency_assignments
        (
            doctor_name,
            emergency_type,
            status
        )

        VALUES (?, ?, ?)
        """,
        (
            "Doctor Name",
            "Emergency",
            "Accepted"
        )
    )

    conn.commit()

    conn.close()

    return redirect('/emergency')

@app.route('/create_roster')
def create_roster():

    return render_template(
        "create_roster.html"
    )


@app.route('/save_roster', methods=['POST'])
def save_roster():

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO roster
        (
            doctor_name,
            monday,
            tuesday,
            wednesday,
            thursday,
            friday,
            saturday,
            sunday
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (
            request.form['doctor_name'],
            request.form['monday'],
            request.form['tuesday'],
            request.form['wednesday'],
            request.form['thursday'],
            request.form['friday'],
            request.form['saturday'],
            request.form['sunday']
        )
    )

    conn.commit()

    conn.close()

    flash("Roster Saved Successfully")

    return redirect('/roster')


conn = sqlite3.connect('database.db')

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS emergency_assignments(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    doctor_name TEXT,

    emergency_type TEXT,

    status TEXT
)
""")

conn.commit()

conn.close()


if __name__ == '__main__':
    app.run(debug=True)