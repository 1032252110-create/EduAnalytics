"""
EduAnalytics - Student Performance Analytics & AI Prediction System
Main Streamlit Application.
"""
import streamlit as st
import pandas as pd
import numpy as np

import crud
from ml_model import predictor
from utils.analytics import compute_dashboard_metrics, filter_analytics_data, compute_student_summary
from utils.visualizations import (
    chart_subject_wise_marks, chart_semester_performance, chart_pass_fail_distribution,
    chart_attendance_vs_marks, chart_performance_distribution, chart_student_subject_marks,
    chart_student_subject_attendance
)

CSV_TEMPLATE = """student_id,name,email,branch,semester,subject,internal_marks,external_marks,total_classes,attended_classes
STU1001,Aarav Sharma,aarav@example.edu,Computer Science,5,Data Structures,36,54,45,42
STU1002,Diya Patel,diya@example.edu,Information Tech,4,Database Systems,28,42,45,35
STU1003,Rohan Verma,rohan@example.edu,Electronics & Comm,6,Computer Networks,18,25,40,22
"""

st.set_page_config(page_title="EduAnalytics", page_icon="🎓", layout="wide")

# ==============================================================================
# SIDEBAR
# ==============================================================================
st.sidebar.markdown("## 🎓 EduAnalytics")
st.sidebar.caption("Student Analytics & AI Prediction")
menu = ["🏠 Dashboard", "👨‍🎓 Students", "📚 Marks", "📅 Attendance", "📊 Student Analysis", "🤖 AI Prediction", "📥 Upload Data"]
page = st.sidebar.radio("Navigation", menu, label_visibility="collapsed")

# ==============================================================================
# 1. DASHBOARD
# ==============================================================================
if page == "🏠 Dashboard":
    st.markdown("## 🏠 Academic Dashboard")
    s_df, m_df, a_df = pd.DataFrame(crud.get_all_students()), pd.DataFrame(crud.get_all_marks()), pd.DataFrame(crud.get_all_attendance())

    if s_df.empty:
        st.info("No student records found. Go to '📥 Upload Data' to import your student CSV.")
    else:
        # Global Filters
        f1, f2, f3 = st.columns(3)
        b_filter = f1.selectbox("Filter Branch", ["All"] + sorted(list(s_df["branch"].unique())))
        sem_filter = f2.selectbox("Filter Semester", ["All"] + sorted([str(s) for s in s_df["semester"].unique()]))
        sub_filter = f3.selectbox("Filter Subject", ["All"] + sorted(list(m_df["subject"].unique())) if not m_df.empty else ["All"])

        f_students, f_marks, f_att = filter_analytics_data(s_df, m_df, a_df, b_filter, sem_filter, sub_filter)
        metrics = compute_dashboard_metrics(f_students, f_marks, f_att)

        # 5 Top KPI Metric Cards
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Students", metrics["total_students"])
        c2.metric("Average Marks", f"{metrics['avg_marks']}/100")
        c3.metric("Average Attendance", f"{metrics['avg_attendance']}%")
        c4.metric("Pass Percentage", f"{metrics['pass_percentage']}%")
        c5.metric("Students At Risk", metrics["students_at_risk"])

        st.markdown("---")
        # 5 Charts
        ch1, ch2 = st.columns(2)
        ch1.plotly_chart(chart_subject_wise_marks(f_marks), use_container_width=True)
        ch2.plotly_chart(chart_semester_performance(f_marks), use_container_width=True)

        ch3, ch4 = st.columns(2)
        ch3.plotly_chart(chart_pass_fail_distribution(f_marks), use_container_width=True)
        ch4.plotly_chart(chart_attendance_vs_marks(f_marks, f_att), use_container_width=True)

        st.plotly_chart(chart_performance_distribution(f_marks), use_container_width=True)

# ==============================================================================
# 2. STUDENTS
# ==============================================================================
elif page == "👨‍🎓 Students":
    st.markdown("## 👨‍🎓 Student Management")
    tab_view, tab_add, tab_edit, tab_del = st.tabs(["Directory", "Add Student", "Edit Student", "Delete Student"])
    students = crud.get_all_students()

    with tab_view:
        search = st.text_input("Search by ID, Name or Email")
        filtered = crud.get_all_students(search_query=search)
        if filtered:
            st.dataframe(pd.DataFrame(filtered), use_container_width=True, hide_index=True)
        else:
            st.info("No students found.")

    with tab_add:
        with st.form("add_student"):
            col1, col2 = st.columns(2)
            sid = col1.text_input("Student ID (e.g. STU1001)")
            name = col1.text_input("Full Name")
            email = col1.text_input("Email Address")
            branch = col2.selectbox("Branch", ["Computer Science", "Information Tech", "Data Science", "Electronics & Comm", "Mechanical Eng", "Civil Eng"])
            sem = col2.slider("Semester", 1, 8, 1)
            if st.form_submit_button("Save Student", type="primary"):
                ok, msg = crud.add_student(sid, name, email, branch, sem)
                (st.success(msg) if ok else st.error(msg)) and st.rerun() if ok else None

    with tab_edit:
        if students:
            s_map = {f"{s['student_id']} - {s['name']}": s for s in students}
            chosen = s_map[st.selectbox("Select Student to Edit", list(s_map.keys()))]
            with st.form("edit_student"):
                name = st.text_input("Name", value=chosen["name"])
                email = st.text_input("Email", value=chosen["email"])
                branches = ["Computer Science", "Information Tech", "Data Science", "Electronics & Comm", "Mechanical Eng", "Civil Eng"]
                branch = st.selectbox("Branch", branches, index=branches.index(chosen["branch"]) if chosen["branch"] in branches else 0)
                sem = st.slider("Semester", 1, 8, int(chosen["semester"]))
                if st.form_submit_button("Update"):
                    ok, msg = crud.update_student(chosen["student_id"], name, email, branch, sem)
                    (st.success(msg) if ok else st.error(msg)) and st.rerun() if ok else None

    with tab_del:
        if students:
            del_id = st.selectbox("Select Student to Delete", [s["student_id"] for s in students])
            if st.button(f"Confirm Delete {del_id}", type="primary"):
                crud.delete_student(del_id)
                st.success(f"Student {del_id} deleted.")
                st.rerun()

# ==============================================================================
# 3. MARKS
# ==============================================================================
elif page == "📚 Marks":
    st.markdown("## 📚 Marks Management")
    students = crud.get_all_students()
    if not students: st.warning("Please add students first.")
    else:
        tab_v, tab_a, tab_e, tab_d = st.tabs(["View Marks", "Add Marks", "Edit Marks", "Delete Marks"])
        with tab_v:
            marks = crud.get_all_marks()
            st.dataframe(pd.DataFrame(marks), use_container_width=True, hide_index=True) if marks else st.info("No marks records.")

        with tab_a:
            with st.form("add_marks"):
                sid = st.selectbox("Student", [s["student_id"] for s in students])
                subj = st.text_input("Subject Name")
                sem = st.number_input("Semester", 1, 8, 1)
                intl = st.number_input("Internal Marks (0-40)", 0.0, 40.0, 25.0)
                ext = st.number_input("External Marks (0-60)", 0.0, 60.0, 40.0)
                st.info(f"Total: {round(intl + ext, 2)} / 100")
                if st.form_submit_button("Save Marks", type="primary"):
                    ok, msg = crud.add_mark(sid, subj, intl, ext, sem)
                    (st.success(msg) if ok else st.error(msg)) and st.rerun() if ok else None

        with tab_e:
            marks = crud.get_all_marks()
            if marks:
                m_map = {f"#{m['id']} - {m['student_id']} - {m['subject']}": m for m in marks}
                rec = m_map[st.selectbox("Select Record", list(m_map.keys()))]
                with st.form("edit_marks"):
                    s = st.text_input("Subject", rec["subject"])
                    sm = st.number_input("Semester", 1, 8, int(rec["semester"]))
                    i = st.number_input("Internal (0-40)", 0.0, 40.0, float(rec["internal_marks"]))
                    e = st.number_input("External (0-60)", 0.0, 60.0, float(rec["external_marks"]))
                    if st.form_submit_button("Update"):
                        crud.update_mark(rec["id"], s, i, e, sm)
                        st.success("Marks updated.")
                        st.rerun()

        with tab_d:
            marks = crud.get_all_marks()
            if marks:
                del_mid = st.selectbox("Delete Mark ID", [m["id"] for m in marks])
                if st.button("Delete Marks Entry", type="primary"):
                    crud.delete_mark(del_mid)
                    st.success("Deleted.")
                    st.rerun()

# ==============================================================================
# 4. ATTENDANCE
# ==============================================================================
elif page == "📅 Attendance":
    st.markdown("## 📅 Attendance Management")
    students = crud.get_all_students()
    if not students: st.warning("Please add students first.")
    else:
        tab_v, tab_a, tab_e, tab_d = st.tabs(["Attendance Log", "Add Attendance", "Edit Attendance", "Delete Attendance"])
        with tab_v:
            att = crud.get_all_attendance()
            if att:
                df_att = pd.DataFrame(att)
                df_att["Status"] = df_att["attendance_percentage"].apply(lambda p: "🟢 Good" if p >= 75 else ("🟡 Warning" if p >= 60 else "🔴 Critical"))
                st.dataframe(df_att, use_container_width=True, hide_index=True)
            else: st.info("No attendance records.")

        with tab_a:
            with st.form("add_att"):
                sid = st.selectbox("Student", [s["student_id"] for s in students])
                subj = st.text_input("Subject Name")
                total = st.number_input("Total Classes Held", 1, 200, 45)
                attended = st.number_input("Classes Attended", 0, 200, 38)
                if total > 0: st.info(f"Attendance: {round((attended / total) * 100, 1)}%")
                if st.form_submit_button("Save Attendance", type="primary"):
                    ok, msg = crud.add_attendance(sid, subj, total, attended)
                    (st.success(msg) if ok else st.error(msg)) and st.rerun() if ok else None

        with tab_e:
            att = crud.get_all_attendance()
            if att:
                a_map = {f"#{a['id']} - {a['student_id']} - {a['subject']}": a for a in att}
                rec = a_map[st.selectbox("Select Record", list(a_map.keys()))]
                with st.form("edit_att"):
                    s = st.text_input("Subject", rec["subject"])
                    tot = st.number_input("Total", 1, 200, int(rec["total_classes"]))
                    at = st.number_input("Attended", 0, 200, int(rec["attended_classes"]))
                    if st.form_submit_button("Update"):
                        crud.update_attendance(rec["id"], s, tot, at)
                        st.success("Attendance updated.")
                        st.rerun()

        with tab_d:
            att = crud.get_all_attendance()
            if att:
                del_aid = st.selectbox("Delete Attendance ID", [a["id"] for a in att])
                if st.button("Delete Attendance Entry", type="primary"):
                    crud.delete_attendance(del_aid)
                    st.success("Deleted.")
                    st.rerun()

# ==============================================================================
# 5. STUDENT ANALYSIS
# ==============================================================================
elif page == "📊 Student Analysis":
    st.markdown("## 📊 Individual Student Analytics")
    students = crud.get_all_students()
    if not students: st.warning("Please add students first.")
    else:
        sid = st.selectbox("Select Student", [s["student_id"] for s in students])
        s_info = crud.get_student_by_id(sid)
        summary = compute_student_summary(s_info, crud.get_marks_by_student(sid), crud.get_attendance_by_student(sid))

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Student Name", summary["name"], f"Sem {summary['semester']}")
        c2.metric("Average Marks", f"{summary['avg_marks']}/100")
        c3.metric("Average Attendance", f"{summary['avg_attendance']}%")
        c4.metric("Status", summary["academic_status"])

        st.info(f"🏆 Strongest: **{summary['strongest_subject']}**  |  ⚠️ Weakest: **{summary['weakest_subject']}**")

        ch1, ch2 = st.columns(2)
        ch1.plotly_chart(chart_student_subject_marks(summary["marks_df"]), use_container_width=True)
        ch2.plotly_chart(chart_student_subject_attendance(summary["attendance_df"]), use_container_width=True)

# ==============================================================================
# 6. AI PREDICTION
# ==============================================================================
elif page == "🤖 AI Prediction":
    st.markdown("## 🤖 AI Performance & Risk Predictor")
    students = crud.get_all_students()

    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown("#### Input Features")
        internal = st.slider("Internal Marks (0-40)", 0.0, 40.0, 30.0)
        attendance = st.slider("Attendance % (0-100)", 0.0, 100.0, 80.0)
        assignment = st.slider("Assignment Score % (0-100)", 0.0, 100.0, 75.0)
        prev_sem = st.slider("Previous Semester % (0-100)", 0.0, 100.0, 75.0)
        predict_click = st.button("Predict Performance", type="primary", use_container_width=True)

    with col2:
        st.markdown("#### Prediction Outcome")
        res = predictor.predict(internal, attendance, assignment, prev_sem)

        badge = "🟢 LOW RISK" if res["risk_level"] == "Low Risk" else ("🟡 MEDIUM RISK" if res["risk_level"] == "Medium Risk" else "🔴 HIGH RISK")
        st.metric("Expected Final Score", f"{res['predicted_score']}%", badge)
        st.info(res["insights"])

        p_cols = st.columns(3)
        for i, (k, v) in enumerate(res["probabilities"].items()):
            p_cols[i].metric(k, f"{v}%")

        if predict_click and students:
            crud.save_prediction(students[0]["student_id"], res["predicted_score"], res["risk_level"])

# ==============================================================================
# 7. UPLOAD DATA
# ==============================================================================
elif page == "📥 Upload Data":
    st.markdown("## 📥 Import Student Data (CSV)")
    st.download_button("📄 Download CSV Template", data=CSV_TEMPLATE, file_name="student_template.csv", mime="text/csv")

    uploaded = st.file_uploader("Upload Student CSV", type=["csv"])
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        st.write(f"**Rows:** {len(df)} | **Columns:** {len(df.columns)}")
        st.dataframe(df.head(5), use_container_width=True)

        is_valid, errors, _, cleaned = crud.validate_student_csv(df)
        if not is_valid:
            for e in errors: st.error(e)
        else:
            st.success("CSV format valid.")
            if st.button("Import Data into Database", type="primary"):
                _, res = crud.import_csv_data(cleaned)
                st.success(res["message"])
                st.balloons()
