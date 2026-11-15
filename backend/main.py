
import os
import json
import time
import hmac
import base64
import sqlite3
import hashlib
import secrets

from datetime import date
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

HOST = "127.0.0.1"
PORT = 8000
DB_PATH = os.path.join(os.path.dirname(__file__), "attendance.db")
SECRET = os.environ.get(
    "ATTENDANCE_SECRET",
    "CHANGE_THIS_SECRET_BEFORE_DEPLOYMENT"
)

# FASTAPI APPLICATION
app = FastAPI(
    title="Class Attendance System API",
    description="REST API for the Ionic Class Attendance System",
    version="1.0.0"
)

# CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8100",
        "http://127.0.0.1:8100",
        "http://localhost:8101",
        "http://127.0.0.1:8101"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# REQUEST SCHEMAS

class LoginRequest(BaseModel):
    username: str
    password: str


class StudentCreate(BaseModel):
    student_number: str = Field(min_length=1)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    grade_section: str = ""


class StudentUpdate(BaseModel):
    student_number: str = Field(min_length=1)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    grade_section: str = ""


class ScheduleCreate(BaseModel):
    subject: str = Field(min_length=1)
    start_time: str
    end_time: str
    room: str = ""
    instructor: str = ""
    day_of_week: str = "Monday"


class ScheduleUpdate(BaseModel):
    subject: str = Field(min_length=1)
    start_time: str
    end_time: str
    room: str = ""
    instructor: str = ""
    day_of_week: str = "Monday"


class AttendanceCreate(BaseModel):
    student_id: int
    attendance_date: date
    status: str


class AttendanceUpdate(BaseModel):
    student_id: int
    attendance_date: date
    status: str


# DATABASE CONNECTION

def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


# PASSWORD HASHING

def password_hash(password, salt=None):
    salt = salt or secrets.token_bytes(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        180000
    )

    return salt.hex() + "$" + digest.hex()


def verify_password(password, stored):
    try:
        salt_hex, digest_hex = stored.split("$", 1)

        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt_hex),
            180000
        ).hex()

        return hmac.compare_digest(actual, digest_hex)

    except (ValueError, TypeError):
        return False


# TOKEN FUNCTIONS

def create_token(user):
    payload = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "exp": int(time.time()) + 28800
    }

    raw = json.dumps(
        payload,
        separators=(",", ":")
    ).encode()

    body = base64.urlsafe_b64encode(
        raw
    ).decode().rstrip("=")

    signature = hmac.new(
        SECRET.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    return body + "." + signature


def read_token(token):
    try:
        body, signature = token.split(".", 1)

        expected = hmac.new(
            SECRET.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            return None

        raw = base64.urlsafe_b64decode(
            body + "=" * (-len(body) % 4)
        )

        payload = json.loads(raw)

        if payload.get("exp", 0) < int(time.time()):
            return None

        return payload

    except Exception:
        return None


# DATABASE INITIALIZATION

def init_db():
    with connect() as db:

        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_number TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            grade_section TEXT DEFAULT '',
            active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            room TEXT DEFAULT '',
            instructor TEXT DEFAULT '',
            day_of_week TEXT DEFAULT 'Monday'
        );

        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL,
            marked_by INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, attendance_date),
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(marked_by) REFERENCES users(id)
        );
        """)

        # DEFAULT ACCOUNTS

        accounts = [
            ("registrar", "Registrar User", "registrar123", "registrar"),
            ("teacher", "Mr. Teacher", "teacher123", "teacher")
        ]

        for username, name, password, role in accounts:

            exists = db.execute(
                "SELECT id FROM users WHERE username=?",
                (username,)
            ).fetchone()

            if not exists:
                db.execute(
                    """
                    INSERT INTO users
                    (username, full_name, password_hash, role)
                    VALUES (?, ?, ?, ?)
                    """,
                    (username, name, password_hash(password), role)
                )

        # SAMPLE STUDENTS

        student_count = db.execute(
            "SELECT COUNT(*) AS n FROM students WHERE active=1"
        ).fetchone()["n"]

        if student_count == 0:
            db.executemany(
                """
                INSERT INTO students
                (student_number, first_name, last_name, grade_section)
                VALUES (?, ?, ?, ?)
                """,
                [
                    ("1", "Juan", "Dela Cruz", "Grade 7-A"),
                    ("2", "Maria", "Santos", "Grade 7-A"),
                    ("3", "Pedro", "Reyes", "Grade 7-A"),
                    ("4", "Ana", "Garcia", "Grade 7-A"),
                    ("5", "Mark", "Lopez", "Grade 7-A")
                ]
            )

        # SAMPLE SCHEDULES

        schedule_count = db.execute(
            "SELECT COUNT(*) AS n FROM schedules"
        ).fetchone()["n"]

        if schedule_count == 0:
            db.executemany(
                """
                INSERT INTO schedules
                (subject, start_time, end_time, room, instructor, day_of_week)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        "Introduction to Computing",
                        "7:30 AM", "9:00 AM",
                        "Room 101", "Mr. Teacher", "Monday"
                    ),
                    (
                        "Computer Programming 1",
                        "9:00 AM", "10:30 AM",
                        "Computer Laboratory", "Ms. Teacher", "Monday"
                    ),
                    (
                        "Networking Fundamentals",
                        "1:00 PM", "2:30 PM",
                        "Room 202", "Mr. Instructor", "Monday"
                    )
                ]
            )


def as_dict(row):
    return dict(row) if row is not None else None


# AUTHENTICATION AND ROLE CHECKING

def get_current_user(
    authorization: Optional[str] = Header(default=None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Please log in again."
        )

    payload = read_token(authorization[7:])

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    with connect() as db:
        row = db.execute(
            """
            SELECT id, username, full_name, role
            FROM users
            WHERE id=?
            """,
            (payload["id"],)
        ).fetchone()

    user = as_dict(row)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User account not found."
        )

    return user


def require_role(*roles):
    def role_checker(user=Depends(get_current_user)):

        if user["role"] not in roles:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to perform this action."
            )

        return user

    return role_checker


# INITIALIZE DATABASE WHEN FASTAPI STARTS

@app.on_event("startup")
def startup_event():
    init_db()


# HOME AND TEST ROUTES

@app.get("/")
def root():
    return {
        "message": "Welcome to Class Attendance System!",
        "status": "API is running",
        "documentation": "/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "application": "Class Attendance System"
    }


@app.get("/test")
def test_api():
    return {
        "message": "FastAPI successfully connected!",
        "application": "Class Attendance System"
    }


# LOGIN AND USER PROFILE

@app.post("/auth/login")
def login(data: LoginRequest):

    with connect() as db:
        user = db.execute(
            "SELECT * FROM users WHERE username=?",
            (data.username.strip(),)
        ).fetchone()

    if not user or not verify_password(
        data.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password."
        )

    user_data = {
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"]
    }

    return {
        "access_token": create_token(user_data),
        "token_type": "bearer",
        "user": user_data
    }


@app.get("/auth/me")
def get_profile(user=Depends(get_current_user)):
    return user


# =========================================================
# STUDENT MANAGEMENT - CRUD
# REGISTRAR ONLY FOR ADD, UPDATE AND DELETE
# =========================================================

@app.get("/students")
def get_students(user=Depends(get_current_user)):

    with connect() as db:
        rows = db.execute(
            """
            SELECT id, student_number, first_name,
                   last_name, grade_section
            FROM students
            WHERE active=1
            ORDER BY last_name, first_name
            """
        ).fetchall()

    return [as_dict(row) for row in rows]


@app.post("/students", status_code=201)
def add_student(
    data: StudentCreate,
    user=Depends(require_role("registrar"))
):

    try:
        with connect() as db:
            cursor = db.execute(
                """
                INSERT INTO students
                (student_number, first_name, last_name, grade_section)
                VALUES (?, ?, ?, ?)
                """,
                (
                    data.student_number.strip(),
                    data.first_name.strip(),
                    data.last_name.strip(),
                    data.grade_section.strip()
                )
            )

            db.commit()
            new_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Student number already exists."
        )

    return {
        "message": "Student added successfully.",
        "id": new_id
    }


@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    data: StudentUpdate,
    user=Depends(require_role("registrar"))
):

    try:
        with connect() as db:
            cursor = db.execute(
                """
                UPDATE students
                SET student_number=?,
                    first_name=?,
                    last_name=?,
                    grade_section=?
                WHERE id=? AND active=1
                """,
                (
                    data.student_number.strip(),
                    data.first_name.strip(),
                    data.last_name.strip(),
                    data.grade_section.strip(),
                    student_id
                )
            )

            db.commit()

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Student number already exists."
        )

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )

    return {
        "message": "Student updated successfully."
    }


@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    user=Depends(require_role("registrar"))
):

    with connect() as db:
        cursor = db.execute(
            """
            UPDATE students
            SET active=0
            WHERE id=? AND active=1
            """,
            (student_id,)
        )

        db.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )

    return {
        "message": "Student archived successfully."
    }


# =========================================================
# CLASS SCHEDULE - CRUD
# REGISTRAR ONLY FOR ADD, UPDATE AND DELETE
# =========================================================

@app.get("/schedules")
def get_schedules(user=Depends(get_current_user)):

    with connect() as db:
        rows = db.execute(
            "SELECT * FROM schedules ORDER BY id DESC"
        ).fetchall()

    return [as_dict(row) for row in rows]


@app.post("/schedules", status_code=201)
def add_schedule(
    data: ScheduleCreate,
    user=Depends(require_role("registrar"))
):

    with connect() as db:
        cursor = db.execute(
            """
            INSERT INTO schedules
            (subject, start_time, end_time,
             room, instructor, day_of_week)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data.subject.strip(),
                data.start_time,
                data.end_time,
                data.room,
                data.instructor,
                data.day_of_week
            )
        )

        db.commit()
        new_id = cursor.lastrowid

    return {
        "message": "Schedule added successfully.",
        "id": new_id
    }


@app.put("/schedules/{schedule_id}")
def update_schedule(
    schedule_id: int,
    data: ScheduleUpdate,
    user=Depends(require_role("registrar"))
):

    with connect() as db:
        cursor = db.execute(
            """
            UPDATE schedules
            SET subject=?,
                start_time=?,
                end_time=?,
                room=?,
                instructor=?,
                day_of_week=?
            WHERE id=?
            """,
            (
                data.subject.strip(),
                data.start_time,
                data.end_time,
                data.room,
                data.instructor,
                data.day_of_week,
                schedule_id
            )
        )

        db.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Schedule not found."
        )

    return {
        "message": "Schedule updated successfully."
    }


@app.delete("/schedules/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    user=Depends(require_role("registrar"))
):

    with connect() as db:
        cursor = db.execute(
            "DELETE FROM schedules WHERE id=?",
            (schedule_id,)
        )

        db.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Schedule not found."
        )

    return {
        "message": "Schedule deleted successfully."
    }

# =========================================================
# ATTENDANCE MANAGEMENT - CRUD
# TEACHER ONLY FOR ADD, UPDATE AND DELETE
# =========================================================

@app.get("/attendance")
def get_attendance(
    attendance_date: Optional[date] = Query(default=None),
    user=Depends(get_current_user)
):

    sql = """
        SELECT
            a.id,
            a.student_id,
            s.student_number,
            s.first_name || ' ' || s.last_name AS student_name,
            a.attendance_date,
            a.status,
            u.full_name AS marked_by

        FROM attendance a

        JOIN students s
        ON s.id=a.student_id

        JOIN users u
        ON u.id=a.marked_by
    """

    params = ()

    if attendance_date:
        sql += " WHERE a.attendance_date=?"
        params = (attendance_date.isoformat(),)

    sql += " ORDER BY a.attendance_date DESC"

    with connect() as db:
        rows = db.execute(sql, params).fetchall()

    return [as_dict(row) for row in rows]


@app.post("/attendance")
def save_attendance(
    data: AttendanceCreate,
    user=Depends(require_role("teacher"))
):

    if data.status not in ("Present", "Absent", "Late"):
        raise HTTPException(
            status_code=400,
            detail="Invalid attendance status."
        )

    with connect() as db:

        student = db.execute(
            """
            SELECT id FROM students
            WHERE id=? AND active=1
            """,
            (data.student_id,)
        ).fetchone()

        if not student:
            raise HTTPException(
                status_code=404,
                detail="Student not found."
            )

        db.execute(
            """
            INSERT INTO attendance
            (student_id, attendance_date, status, marked_by)
            VALUES (?, ?, ?, ?)

            ON CONFLICT(student_id, attendance_date)
            DO UPDATE SET
                status=excluded.status,
                marked_by=excluded.marked_by
            """,
            (
                data.student_id,
                data.attendance_date.isoformat(),
                data.status,
                user["id"]
            )
        )

        db.commit()

    return {
        "message": "Attendance saved successfully."
    }


@app.put("/attendance/{attendance_id}")
def update_attendance(
    attendance_id: int,
    data: AttendanceUpdate,
    user=Depends(require_role("teacher"))
):

    if data.status not in ("Present", "Absent", "Late"):
        raise HTTPException(
            status_code=400,
            detail="Invalid attendance status."
        )

    with connect() as db:

        student = db.execute(
            """
            SELECT id FROM students
            WHERE id=? AND active=1
            """,
            (data.student_id,)
        ).fetchone()

        if not student:
            raise HTTPException(
                status_code=404,
                detail="Student not found."
            )

        duplicate = db.execute(
            """
            SELECT id FROM attendance
            WHERE student_id=?
            AND attendance_date=?
            AND id<>?
            """,
            (
                data.student_id,
                data.attendance_date.isoformat(),
                attendance_id
            )
        ).fetchone()

        if duplicate:
            raise HTTPException(
                status_code=409,
                detail="An attendance record already exists for this student and date."
            )

        cursor = db.execute(
            """
            UPDATE attendance
            SET student_id=?,
                attendance_date=?,
                status=?,
                marked_by=?
            WHERE id=?
            """,
            (
                data.student_id,
                data.attendance_date.isoformat(),
                data.status,
                user["id"],
                attendance_id
            )
        )

        db.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Attendance record not found."
        )

    return {
        "message": "Attendance updated successfully."
    }


@app.delete("/attendance/{attendance_id}")
def delete_attendance(
    attendance_id: int,
    user=Depends(require_role("teacher"))
):

    with connect() as db:
        cursor = db.execute(
            "DELETE FROM attendance WHERE id=?",
            (attendance_id,)
        )

        db.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Attendance record not found."
        )

    return {
        "message": "Attendance deleted successfully."
    }




@app.get("/dashboard")
def dashboard(
    attendance_date: Optional[date] = Query(default=None),
    user=Depends(get_current_user)
):

    selected_date = (
        attendance_date.isoformat()
        if attendance_date
        else date.today().isoformat()
    )

    with connect() as db:

        total = db.execute(
            """
            SELECT COUNT(*) AS n
            FROM students
            WHERE active=1
            """
        ).fetchone()["n"]

        rows = db.execute(
            """
            SELECT a.status, COUNT(*) AS n

            FROM attendance a

            JOIN students s
            ON s.id=a.student_id

            WHERE a.attendance_date=?
            AND s.active=1

            GROUP BY a.status
            """,
            (selected_date,)
        ).fetchall()

    counts = {
        row["status"]: row["n"]
        for row in rows
    }

    present = counts.get("Present", 0)
    absent = counts.get("Absent", 0)
    late = counts.get("Late", 0)

    percentage = (
        round(present / total * 100)
        if total else 0
    )

    return {
        "attendance_date": selected_date,
        "total_students": total,
        "present": present,
        "absent": absent,
        "late": late,
        "attendance_percentage": percentage
    }




if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True
    )




# Create academic periods table
def create_academic_periods_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS academic_periods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_year TEXT NOT NULL,
            semester TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(school_year, semester)
        )
    """)

    conn.commit()
    conn.close()


# Initialize additional table without deleting existing data
create_academic_periods_table()



class AcademicPeriodCreate(BaseModel):
    school_year: str
    semester: str
    start_date: str
    end_date: str


class AcademicPeriodUpdate(BaseModel):
    school_year: str
    semester: str
    start_date: str
    end_date: str




def get_academic_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def validate_academic_dates(start_date, end_date):
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Dates must use YYYY-MM-DD format."
        )

    if start > end:
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be later than end date."
        )




@app.post("/academic-periods")
def create_academic_period(data: AcademicPeriodCreate):

    if data.semester not in ["First Semester", "Second Semester"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid semester."
        )

    validate_academic_dates(data.start_date, data.end_date)

    conn = get_academic_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO academic_periods
            (school_year, semester, start_date, end_date)
            VALUES (?, ?, ?, ?)
        """, (
            data.school_year,
            data.semester,
            data.start_date,
            data.end_date
        ))

        conn.commit()

        return {
            "message": "Academic period created successfully!"
        }

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="This semester already exists."
        )

    finally:
        conn.close()




@app.get("/academic-periods")
def get_academic_periods():

    conn = get_academic_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM academic_periods
        ORDER BY school_year DESC, id DESC
    """)

    periods = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return periods




@app.put("/academic-periods/{period_id}")
def update_academic_period(
    period_id: int,
    data: AcademicPeriodUpdate
):

    if data.semester not in ["First Semester", "Second Semester"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid semester."
        )

    validate_academic_dates(data.start_date, data.end_date)

    conn = get_academic_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE academic_periods
        SET school_year = ?,
            semester = ?,
            start_date = ?,
            end_date = ?
        WHERE id = ?
    """, (
        data.school_year,
        data.semester,
        data.start_date,
        data.end_date,
        period_id
    ))

    conn.commit()

    updated = cursor.rowcount

    conn.close()

    if updated == 0:
        raise HTTPException(
            status_code=404,
            detail="Academic period not found."
        )

    return {"message": "Academic period updated successfully!"}




@app.delete("/academic-periods/{period_id}")
def delete_academic_period(period_id: int):

    conn = get_academic_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM academic_periods WHERE id = ?",
        (period_id,)
    )

    conn.commit()

    deleted = cursor.rowcount

    conn.close()

    if deleted == 0:
        raise HTTPException(
            status_code=404,
            detail="Academic period not found."
        )

    return {"message": "Academic period deleted successfully!"}




def calculate_student_attendance_grade(
    student_id,
    period_id
):

    conn = get_academic_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM academic_periods
        WHERE id = ?
    """, (period_id,))

    period = cursor.fetchone()

    if not period:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Academic period not found."
        )

    
    cursor.execute("PRAGMA table_info(attendance)")
    columns = [row["name"] for row in cursor.fetchall()]

    if "attendance_date" in columns:
        date_column = "attendance_date"
    elif "date" in columns:
        date_column = "date"
    else:
        conn.close()
        raise HTTPException(
            status_code=500,
            detail="Attendance date column was not found."
        )

    if not {"student_id", "status"}.issubset(columns):
        conn.close()
        raise HTTPException(
            status_code=500,
            detail="Required attendance columns are missing."
        )

    cursor.execute(f"""
        SELECT
            COUNT(*) AS total_days,
            SUM(CASE WHEN LOWER(status) = 'present'
                THEN 1 ELSE 0 END) AS present_days,
            SUM(CASE WHEN LOWER(status) = 'absent'
                THEN 1 ELSE 0 END) AS absent_days,
            SUM(CASE WHEN LOWER(status) = 'late'
                THEN 1 ELSE 0 END) AS late_days
        FROM attendance
        WHERE student_id = ?
        AND {date_column} BETWEEN ? AND ?
    """, (
        student_id,
        period["start_date"],
        period["end_date"]
    ))

    result = cursor.fetchone()

    total = result["total_days"] or 0
    present = result["present_days"] or 0
    absent = result["absent_days"] or 0
    late = result["late_days"] or 0

    percentage = (
        (present / total) * 100
        if total > 0 else 0
    )

    conn.close()

    return {
        "student_id": student_id,
        "school_year": period["school_year"],
        "semester": period["semester"],
        "total_days": total,
        "present": present,
        "absent": absent,
        "late": late,
        "attendance_percentage": round(percentage, 2),
        "attendance_grade": round(percentage, 2)
    }



@app.get("/attendance-grades/{student_id}")
def get_student_attendance_grade(
    student_id: int,
    period_id: int
):

    return calculate_student_attendance_grade(
        student_id,
        period_id
    )



@app.get("/attendance-grades")
def get_all_attendance_grades(period_id: int):

    conn = get_academic_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM students ORDER BY id")

    students = cursor.fetchall()

    conn.close()

    return [
        calculate_student_attendance_grade(
            student["id"],
            period_id
        )
        for student in students
    ]


# =====================================================
# QUARTERLY ATTENDANCE MONITORING
# =====================================================

@app.get("/attendance/quarterly-summary")
def get_quarterly_attendance_summary(
    start_date: date,
    end_date: date,
    user=Depends(get_current_user)
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be later than end date."
        )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                s.id AS student_id,
                s.student_number,
                s.first_name || ' ' || s.last_name AS student_name,

                COALESCE(SUM(
                    CASE WHEN LOWER(a.status) = 'present'
                    THEN 1 ELSE 0 END
                ), 0) AS total_present,

                COALESCE(SUM(
                    CASE WHEN LOWER(a.status) = 'absent'
                    THEN 1 ELSE 0 END
                ), 0) AS total_absent,

                COALESCE(SUM(
                    CASE WHEN LOWER(a.status) = 'late'
                    THEN 1 ELSE 0 END
                ), 0) AS total_late,

                COUNT(a.id) AS total_recorded_days

            FROM students s

            LEFT JOIN attendance a
                ON a.student_id = s.id
                AND a.attendance_date BETWEEN ? AND ?

            WHERE s.active = 1

            GROUP BY
                s.id,
                s.student_number,
                s.first_name,
                s.last_name

            ORDER BY s.last_name ASC, s.first_name ASC
        """, (
            start_date.isoformat(),
            end_date.isoformat()
        ))

        rows = cursor.fetchall()

        results = []

        for row in rows:
            total_days = row["total_recorded_days"]
            present = row["total_present"]
            late = row["total_late"]

            attendance_percentage = (
                ((present + late) / total_days) * 100
                if total_days > 0 else 0
            )

            results.append({
                "student_id": row["student_id"],
                "student_number": row["student_number"],
                "student_name": row["student_name"],
                "total_present": present,
                "total_absent": row["total_absent"],
                "total_late": late,
                "total_recorded_days": total_days,
                "attendance_percentage": round(
                    attendance_percentage, 2
                )
            })

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_students": len(results),
            "records": results
        }

    finally:
        conn.close()
