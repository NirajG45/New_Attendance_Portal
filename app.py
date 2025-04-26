from flask import Flask, request, jsonify, render_template
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
import os
from datetime import timedelta, datetime
import random
import logging
from dotenv import load_dotenv
import sqlite3
from flask import send_file



# Load environment variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# SQLite Configuration
db_file = os.getenv("DB_FILE", "student_portal.db")  # Database file path from .env

# Security Config
bcrypt = Bcrypt(app)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecretkey")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# Logger Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Database Manager to manage DB operations
class DatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript('''
                CREATE TABLE IF NOT EXISTS teachers (
                    teacher_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    password TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    password TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS attendance_codes (
                    teacher_id TEXT,
                    t_code TEXT,
                    timestamp TEXT,
                    PRIMARY KEY (teacher_id)
                );
                CREATE TABLE IF NOT EXISTS attendance (
                    student_id TEXT,
                    date TEXT,
                    status TEXT,
                    teacher_id TEXT,
                    timestamp TEXT,
                    PRIMARY KEY (student_id, date)
                );
            ''')
            conn.commit()

    def execute_query(self, query, params=()):
        """Execute a query and return the result"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchall()

    def execute_insert(self, query, params=()):
        """Execute an insert query"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

# Initialize the DatabaseManager
db_manager = DatabaseManager(db_file)
db_manager.init_db()

def save_attendance_code(code):
    conn = sqlite3.connect('student_portal.db')
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO attendance_codes (t_code) VALUES (?)", (code,))
    
    conn.commit()
    conn.close()

# Helper Function for User Registration
def register_user(table, user_data, id_field):
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT 1 FROM {table} WHERE {id_field} = ?", (user_data[id_field],))
        if cursor.fetchone():
            return {"success": False, "message": f"{id_field} already exists!"}, 400

        hashed_password = bcrypt.generate_password_hash(user_data["password"]).decode("utf-8")
        cursor.execute(f"INSERT INTO {table} ({id_field}, name, password) VALUES (?, ?, ?)",
                       (user_data[id_field], user_data["name"], hashed_password))
        conn.commit()
    return {"success": True, "message": "Registration successful!"}, 201

# Helper Function for User Login
def login_user(table, user_data, id_field):
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT password FROM {table} WHERE {id_field} = ?", (user_data[id_field],))
        user = cursor.fetchone()

        if not user or not bcrypt.check_password_hash(user["password"], user_data["password"]):
            return {"success": False, "message": "Invalid credentials!"}, 401

        token = create_access_token(identity=user_data[id_field])
        return {"success": True, "message": "Login successful!", "token": token}, 200


# Helper Function to Check if Attendance Code is Expired
def is_attendance_code_expired(timestamp):
    code_time = datetime.fromisoformat(timestamp)
    return (datetime.utcnow() - code_time).seconds > 1800

@app.route("/")
def home():
    return render_template("home.html")


@app.route('/download_file')
def download_file():
    return send_file('path_to_your_file.txt', as_attachment=True)

# Route for teacher registration
@app.route("/teacher_register", methods=["GET", "POST"])
def teacher_register():
    if request.method == "POST":
        data = request.get_json()
        print(data) # debugging
        if not data or not all(key in data for key in ["name", "teacher_id", "password"]):
            return jsonify({"success": False, "message": "All fields are required!"}), 400
        register_user("teachers", data, "teacher_id")
        return jsonify({"success": True, "message": "Registration successful!"}), 201
    else:
        return render_template("teacher_register.html")

# Route for teacher login
@app.route("/teacher_login", methods=["GET","POST"])
def teacher_login():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        if not data or not all(key in data for key in ["teacher_id", "password"]):
            return jsonify({"success": False, "message": "All fields are required!"}), 400
        response, status_code = login_user("teachers", data, "teacher_id")

        if status_code == 200:
            attendance_code = str(random.randint(1000, 9999))
            db_manager.execute_insert("REPLACE INTO attendance_codes (teacher_id, t_code, timestamp) VALUES (?, ?, ?)",
                                    (data["teacher_id"], attendance_code, datetime.utcnow().isoformat()))
            response["attendance_code"] = attendance_code
        return jsonify(response), status_code
    else:
        return render_template("teacher_login.html")
    
# Route for student registration 
@app.route("/student_register", methods=["GET", "POST"])
def student_register():
    if request.method == 'POST':
        # Parse the JSON data
        data = request.get_json()

        # Check if data is None or missing required fields
        if not data:
            return jsonify({"success": False, "message": "Invalid JSON data!"}), 400

        required_fields = ["name", "student_id", "password"]
        if not all(field in data for field in required_fields):
            return jsonify({"success": False, "message": "All fields are required!"}), 400

        # Call the function that handles user registration
        registration_result = register_user("students", data, "student_id")

        # ✅ Safe Checking
        if isinstance(registration_result, dict):
            registration_result.setdefault('success', True)
            registration_result.setdefault('message', 'Student registered successfully!')
            return jsonify(registration_result)
        else:
            # Agar kuch galat value return hui hai, to default success response bhej do
            return jsonify({
                "success": True,
                "message": "Student registered successfully!"
            }), 201

    # Handle GET request - render the registration form
    return render_template("student_register.html")

# Route for student login
@app.route("/student_login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        data = request.get_json()
        print("Received Data:", data)

        # Validate input fields
        required_fields = ["student_id", "student_password", "teacher_code"]
        if not data or not all(key in data for key in required_fields):
            return jsonify({"success": False, "message": "All fields are required!"}), 400

        # Rename password field for consistency
        data["password"] = data.pop("student_password")

        # Authenticate student
        response, status_code = login_user("students", data, "student_id")
        if status_code != 200:
            return jsonify(response), status_code

        with db_manager.get_connection() as conn:
            cursor = conn.cursor()

            # Retrieve the attendance code details
            cursor.execute("SELECT teacher_id, timestamp FROM attendance_codes WHERE t_code = ?", (data["teacher_code"],))
            code_entry = cursor.fetchone()

            if not code_entry:
                return jsonify({"success": False, "message": "Invalid attendance code!"}), 400

            teacher_id, timestamp = code_entry

            # # Ensure timestamp is properly formatted
            # if is_attendance_code_expired(timestamp):
            #     return jsonify({"success": False, "message": "Expired attendance code!"}), 400

            # Mark attendance
            cursor.execute("""
                INSERT OR REPLACE INTO attendance 
                (student_id, date, status, teacher_id, timestamp) 
                VALUES (?, ?, ?, ?, ?)
            """, (data["student_id"], datetime.utcnow().strftime("%Y-%m-%d"), "Present", teacher_id, datetime.utcnow().isoformat()))

            conn.commit()

        return jsonify({"success": True, "message": "Attendance marked successfully!", "countdown": 1800}), 200

    return render_template("student_login.html")

@app.route("/timer")
def timer_page():
    return render_template("timer.html")

# Route for teacher dashboard
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if request.method == "GET":
        return render_template("dashboard.html")
    
    if request.method == "POST":
        t_code = random.randint(1000, 9999)  # Generate random code
        
        save_attendance_code(t_code)  # Store code in database
        
        return jsonify({"t_code": t_code})
    
    # Route for fetching attendance summary data for a specific teacher 
    @app.route("/attendance_summary", methods=["GET"])
    def attendance_summary():
        teacher_id = request.args.get('teacher_id')  # From frontend
        if not teacher_id:
            return jsonify({"success": False, "message": "Teacher ID is required!"}), 400

        with db_manager.get_connection() as conn:
            cursor = conn.cursor()

            # Get Teacher Name
            cursor.execute("SELECT name FROM teachers WHERE teacher_id = ?", (teacher_id,))
            teacher = cursor.fetchone()
            if not teacher:
                return jsonify({"success": False, "message": "Teacher not found!"}), 404

            teacher_name = teacher["name"]

            # Get Students who marked attendance with this teacher
            today = datetime.utcnow().strftime("%Y-%m-%d")
            cursor.execute("""
                SELECT s.student_id, s.name 
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.teacher_id = ? AND a.date = ?
            """, (teacher_id, today))

            students = [{"student_id": row["student_id"], "student_name": row["name"]} for row in cursor.fetchall()]

            return jsonify({
                "success": True,
                "teacher_name": teacher_name,
                "total_present": len(students),
                "students": students
            }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)
