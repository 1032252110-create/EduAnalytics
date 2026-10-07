"""
Database setup for SQLite.
Creates 4 simple tables: students, marks, attendance, predictions.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eduanalytics.db")

def get_connection():
    """Returns a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates the 4 tables if they do not exist."""
    conn = get_connection()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                branch TEXT NOT NULL,
                semester INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS marks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                internal_marks REAL NOT NULL,
                external_marks REAL NOT NULL,
                total_marks REAL NOT NULL,
                semester INTEGER NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                total_classes INTEGER NOT NULL,
                attended_classes INTEGER NOT NULL,
                attendance_percentage REAL NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                predicted_score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                prediction_date TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
            );
        """)
    conn.close()

init_db()
