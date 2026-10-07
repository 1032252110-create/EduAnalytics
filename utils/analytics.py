"""
Analytics calculations: calculates averages, filters data, and summarizes student performance.
"""
import pandas as pd

def compute_dashboard_metrics(students_df, marks_df, attendance_df):
    """Calculates the 5 metrics on top of the dashboard."""
    total_students = len(students_df) if not students_df.empty else 0
    avg_marks = round(marks_df["total_marks"].mean(), 1) if not marks_df.empty else 0.0
    avg_att = round(attendance_df["attendance_percentage"].mean(), 1) if not attendance_df.empty else 0.0
    pass_pct = round(((marks_df["total_marks"] >= 40).sum() / len(marks_df)) * 100, 1) if not marks_df.empty else 0.0

    # A student is at risk if average score < 40 or average attendance < 60%
    low_marks = set(marks_df.groupby("student_id")["total_marks"].mean().loc[lambda x: x < 40].index) if not marks_df.empty else set()
    low_att = set(attendance_df.groupby("student_id")["attendance_percentage"].mean().loc[lambda x: x < 60].index) if not attendance_df.empty else set()
    visible_ids = set(students_df["student_id"].unique()) if not students_df.empty else set()
    at_risk_count = len((low_marks | low_att) & visible_ids)

    return {
        "total_students": total_students, "avg_marks": avg_marks,
        "avg_attendance": avg_att, "pass_percentage": pass_pct, "students_at_risk": at_risk_count
    }

def filter_analytics_data(students_df, marks_df, attendance_df, branch="All", semester="All", subject="All"):
    """Filters students, marks, and attendance by branch, semester, or subject."""
    s_df, m_df, a_df = students_df.copy(), marks_df.copy(), attendance_df.copy()

    if branch != "All" and not s_df.empty:
        s_df = s_df[s_df["branch"] == branch]
        ids = s_df["student_id"].unique()
        m_df = m_df[m_df["student_id"].isin(ids)] if not m_df.empty else m_df
        a_df = a_df[a_df["student_id"].isin(ids)] if not a_df.empty else a_df

    if semester != "All":
        sem = int(semester)
        s_df = s_df[s_df["semester"] == sem] if not s_df.empty else s_df
        m_df = m_df[m_df["semester"] == sem] if not m_df.empty else m_df
        ids = s_df["student_id"].unique() if not s_df.empty else []
        a_df = a_df[a_df["student_id"].isin(ids)] if not a_df.empty else a_df

    if subject != "All":
        m_df = m_df[m_df["subject"] == subject] if not m_df.empty else m_df
        a_df = a_df[a_df["subject"] == subject] if not a_df.empty else a_df

    return s_df, m_df, a_df

def compute_student_summary(student_info, marks_list, attendance_list):
    """Calculates overall metrics, strongest/weakest subjects for a single student."""
    m_df = pd.DataFrame(marks_list) if marks_list else pd.DataFrame()
    a_df = pd.DataFrame(attendance_list) if attendance_list else pd.DataFrame()

    avg_marks = round(m_df["total_marks"].mean(), 1) if not m_df.empty else 0.0
    avg_att = round(a_df["attendance_percentage"].mean(), 1) if not a_df.empty else 0.0

    strongest = f"{m_df.loc[m_df['total_marks'].idxmax()]['subject']} ({int(m_df['total_marks'].max())}/100)" if not m_df.empty else "N/A"
    weakest = f"{m_df.loc[m_df['total_marks'].idxmin()]['subject']} ({int(m_df['total_marks'].min())}/100)" if not m_df.empty else "N/A"

    grade = "Distinction" if avg_marks >= 75 else ("First Class" if avg_marks >= 60 else ("Pass Class" if avg_marks >= 40 else "Needs Improvement"))
    status_color = "🟢" if avg_marks >= 60 else ("🟡" if avg_marks >= 40 else "🔴")

    return {
        "student_id": student_info.get("student_id", ""), "name": student_info.get("name", ""),
        "branch": student_info.get("branch", ""), "semester": student_info.get("semester", ""),
        "email": student_info.get("email", ""), "avg_marks": avg_marks, "avg_attendance": avg_att,
        "strongest_subject": strongest, "weakest_subject": weakest, "academic_status": grade,
        "status_color": status_color, "marks_df": m_df, "attendance_df": a_df
    }
