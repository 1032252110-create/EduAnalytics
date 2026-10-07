"""
CRUD (Create, Read, Update, Delete) and CSV Import operations for SQLite.
"""
from datetime import datetime
import pandas as pd
from database import get_connection

# ==============================================================================
# 1. STUDENTS
# ==============================================================================
def get_all_students(search_query=None, branch=None, semester=None):
    """Fetches students with optional search and filters."""
    sql, params = "SELECT * FROM students WHERE 1=1", []
    if search_query:
        sql += " AND (student_id LIKE ? OR name LIKE ? OR email LIKE ?)"
        q = f"%{search_query.strip()}%"
        params.extend([q, q, q])
    if branch and branch != "All":
        sql += " AND branch = ?"
        params.append(branch)
    if semester and semester != "All":
        sql += " AND semester = ?"
        params.append(semester)
    sql += " ORDER BY student_id ASC"

    conn = get_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_student_by_id(student_id):
    """Fetches a single student by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM students WHERE student_id = ?", (student_id.strip().upper(),)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_student(student_id, name, email, branch, semester):
    """Adds a new student to database."""
    sid, name, email = student_id.strip().upper(), name.strip(), email.strip().lower()
    if not sid or not name or not email:
        return False, "All fields are required."
    if get_student_by_id(sid):
        return False, f"Student ID '{sid}' already exists."

    conn = get_connection()
    with conn:
        conn.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?)", (sid, name, email, branch, semester))
    conn.close()
    return True, f"Student {sid} added successfully."

def update_student(student_id, name, email, branch, semester):
    """Updates an existing student."""
    conn = get_connection()
    with conn:
        conn.execute("UPDATE students SET name=?, email=?, branch=?, semester=? WHERE student_id=?",
                     (name.strip(), email.strip().lower(), branch, semester, student_id.strip().upper()))
    conn.close()
    return True, f"Student {student_id} updated."

def delete_student(student_id):
    """Deletes a student and cascades to their marks and attendance."""
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM students WHERE student_id=?", (student_id.strip().upper(),))
    conn.close()
    return True, f"Student {student_id} deleted."

# ==============================================================================
# 2. MARKS
# ==============================================================================
def get_all_marks():
    """Fetches all marks records joined with student name."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT m.id, m.student_id, s.name, s.branch, m.semester, m.subject,
               m.internal_marks, m.external_marks, m.total_marks
        FROM marks m LEFT JOIN students s ON m.student_id = s.student_id
        ORDER BY m.id DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_marks_by_student(student_id):
    """Fetches marks for a single student."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM marks WHERE student_id=? ORDER BY semester, subject", (student_id.strip().upper(),)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_mark(student_id, subject, internal, external, semester):
    """Adds marks entry and auto-calculates total (internal + external)."""
    sid, subj = student_id.strip().upper(), subject.strip()
    if not get_student_by_id(sid):
        return False, f"Student '{sid}' does not exist."
    if not (0 <= internal <= 40 and 0 <= external <= 60):
        return False, "Internal marks must be 0-40, external 0-60."

    total = round(float(internal) + float(external), 2)
    conn = get_connection()
    with conn:
        conn.execute("INSERT INTO marks (student_id, subject, internal_marks, external_marks, total_marks, semester) VALUES (?, ?, ?, ?, ?, ?)",
                     (sid, subj, internal, external, total, semester))
    conn.close()
    return True, f"Marks for {subj} added."

def update_mark(mark_id, subject, internal, external, semester):
    """Updates existing marks entry."""
    total = round(float(internal) + float(external), 2)
    conn = get_connection()
    with conn:
        conn.execute("UPDATE marks SET subject=?, internal_marks=?, external_marks=?, total_marks=?, semester=? WHERE id=?",
                     (subject.strip(), internal, external, total, semester, mark_id))
    conn.close()
    return True, "Marks updated."

def delete_mark(mark_id):
    """Deletes a marks entry."""
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM marks WHERE id=?", (mark_id,))
    conn.close()
    return True, "Marks entry deleted."

# ==============================================================================
# 3. ATTENDANCE
# ==============================================================================
def get_all_attendance():
    """Fetches all attendance records."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.id, a.student_id, s.name, s.branch, s.semester, a.subject,
               a.total_classes, a.attended_classes, a.attendance_percentage
        FROM attendance a LEFT JOIN students s ON a.student_id = s.student_id
        ORDER BY a.id DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_attendance_by_student(student_id):
    """Fetches attendance for a single student."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM attendance WHERE student_id=? ORDER BY subject", (student_id.strip().upper(),)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_attendance(student_id, subject, total_cls, attended_cls):
    """Adds attendance and calculates percentage."""
    sid, subj = student_id.strip().upper(), subject.strip()
    if not get_student_by_id(sid): return False, f"Student '{sid}' does not exist."
    if total_cls <= 0 or attended_cls < 0 or attended_cls > total_cls:
        return False, "Attended classes cannot exceed total classes held (>0)."

    pct = round((attended_cls / total_cls) * 100, 2)
    conn = get_connection()
    with conn:
        conn.execute("INSERT INTO attendance (student_id, subject, total_classes, attended_classes, attendance_percentage) VALUES (?, ?, ?, ?, ?)",
                     (sid, subj, total_cls, attended_cls, pct))
    conn.close()
    return True, f"Attendance for {subj} added."

def update_attendance(att_id, subject, total_cls, attended_cls):
    """Updates existing attendance record."""
    if total_cls <= 0 or attended_cls < 0 or attended_cls > total_cls:
        return False, "Attended classes cannot exceed total classes."
    pct = round((attended_cls / total_cls) * 100, 2)
    conn = get_connection()
    with conn:
        conn.execute("UPDATE attendance SET subject=?, total_classes=?, attended_classes=?, attendance_percentage=? WHERE id=?",
                     (subject.strip(), total_cls, attended_cls, pct, att_id))
    conn.close()
    return True, "Attendance updated."

def delete_attendance(att_id):
    """Deletes attendance entry."""
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM attendance WHERE id=?", (att_id,))
    conn.close()
    return True, "Attendance record deleted."

# ==============================================================================
# 4. PREDICTIONS
# ==============================================================================
def save_prediction(student_id, score, risk):
    """Saves ML prediction into database."""
    conn = get_connection()
    with conn:
        conn.execute("INSERT INTO predictions (student_id, predicted_score, risk_level, prediction_date) VALUES (?, ?, ?, ?)",
                     (student_id.strip().upper(), score, risk, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.close()

# ==============================================================================
# 5. CSV VALIDATION & IMPORT
# ==============================================================================
def validate_student_csv(df):
    """Validates CSV columns and value ranges."""
    if df is None or df.empty:
        return False, ["CSV file is empty."], [], df

    cleaned = df.copy()
    cleaned.columns = [str(c).strip().lower().replace(" ", "_") for c in cleaned.columns]
    errors, warnings = [], []

    required = ["student_id", "name", "email", "branch", "semester"]
    missing = [c for c in required if c not in cleaned.columns]
    if missing:
        return False, [f"Missing required columns: {', '.join(missing)}"], [], cleaned

    for idx, row in cleaned.iterrows():
        sid = str(row.get("student_id", "")).strip().upper()
        if not sid or sid == "NAN":
            errors.append(f"Row {idx+1}: Missing student_id.")
        try:
            sem = int(row.get("semester", 1))
            if not (1 <= sem <= 8): errors.append(f"Row {idx+1} ({sid}): Semester must be 1-8.")
        except Exception:
            errors.append(f"Row {idx+1} ({sid}): Semester must be an integer.")

        # Check marks bounds
        if "internal_marks" in cleaned.columns and pd.notna(row["internal_marks"]):
            if not (0 <= float(row["internal_marks"]) <= 40): errors.append(f"Row {idx+1} ({sid}): Internal marks must be 0-40.")
        if "external_marks" in cleaned.columns and pd.notna(row["external_marks"]):
            if not (0 <= float(row["external_marks"]) <= 60): errors.append(f"Row {idx+1} ({sid}): External marks must be 0-60.")

        # Check attendance bounds
        if "total_classes" in cleaned.columns and "attended_classes" in cleaned.columns:
            if pd.notna(row["total_classes"]) and pd.notna(row["attended_classes"]):
                tot, att = int(row["total_classes"]), int(row["attended_classes"])
                if tot <= 0 or att < 0 or att > tot:
                    errors.append(f"Row {idx+1} ({sid}): Attended classes cannot exceed total classes.")
        if len(errors) >= 10: break

    return (len(errors) == 0), errors, warnings, cleaned

def import_csv_data(df):
    """Imports CSV records. If student/mark already exists, updates instead of duplicating."""
    conn = get_connection()
    added, updated = 0, 0
    with conn:
        # 1. Students
        for sid, group in df.groupby("student_id"):
            sid = str(sid).strip().upper()
            first = group.iloc[0]
            name, email, branch, sem = str(first["name"]).strip(), str(first["email"]).strip(), str(first["branch"]).strip(), int(first["semester"])

            exists = conn.execute("SELECT 1 FROM students WHERE student_id=?", (sid,)).fetchone()
            if exists:
                conn.execute("UPDATE students SET name=?, email=?, branch=?, semester=? WHERE student_id=?", (name, email, branch, sem, sid))
                updated += 1
            else:
                conn.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?)", (sid, name, email, branch, sem))
                added += 1

        # 2. Marks & Attendance if columns exist
        has_sub = "subject" in df.columns
        for _, row in df.iterrows():
            sid = str(row["student_id"]).strip().upper()
            sem = int(row["semester"])
            subj = str(row["subject"]).strip() if (has_sub and pd.notna(row["subject"])) else None

            if subj and "internal_marks" in df.columns and "external_marks" in df.columns and pd.notna(row["internal_marks"]):
                intl, ext = float(row["internal_marks"]), float(row["external_marks"])
                total = round(intl + ext, 2)
                m_exists = conn.execute("SELECT id FROM marks WHERE student_id=? AND subject=? AND semester=?", (sid, subj, sem)).fetchone()
                if m_exists:
                    conn.execute("UPDATE marks SET internal_marks=?, external_marks=?, total_marks=? WHERE id=?", (intl, ext, total, m_exists[0]))
                else:
                    conn.execute("INSERT INTO marks (student_id, subject, internal_marks, external_marks, total_marks, semester) VALUES (?, ?, ?, ?, ?, ?)", (sid, subj, intl, ext, total, sem))

            if subj and "total_classes" in df.columns and "attended_classes" in df.columns and pd.notna(row["total_classes"]):
                tot, att = int(row["total_classes"]), int(row["attended_classes"])
                pct = round((att / tot) * 100, 2) if tot > 0 else 0
                a_exists = conn.execute("SELECT id FROM attendance WHERE student_id=? AND subject=?", (sid, subj)).fetchone()
                if a_exists:
                    conn.execute("UPDATE attendance SET total_classes=?, attended_classes=?, attendance_percentage=? WHERE id=?", (tot, att, pct, a_exists[0]))
                else:
                    conn.execute("INSERT INTO attendance (student_id, subject, total_classes, attended_classes, attendance_percentage) VALUES (?, ?, ?, ?, ?)", (sid, subj, tot, att, pct))

    conn.close()
    return True, {"message": f"{added + updated} student records imported successfully ({added} added, {updated} updated)."}
