# 🎓 EduAnalytics – Student Performance Analytics & AI Prediction System

**EduAnalytics** is a clean, modern, and compact student analytics and machine learning web application built with **Python**, **Streamlit**, **SQLite**, and **Scikit-learn**.

The entire project has been optimized to be **concise (~680 total lines across all files)** and **extremely easy to explain in a college viva or project presentation**.

---

## 🌟 Key Features

1. **🏠 Academic Dashboard**
   - 5 KPI metric cards: Total Students, Average Marks, Average Attendance, Pass Percentage, Students At Risk.
   - 5 interactive Plotly charts: Subject averages, semester trend, pass vs fail donut, attendance vs marks scatter, and grade distribution.
   - Dynamic filters by **Branch**, **Semester**, and **Subject**.

2. **👨‍🎓 Student Management (CRUD)**
   - Searchable student directory by ID, Name, or Email.
   - Add new student, edit existing student, delete student with confirmation.

3. **📚 Marks Management**
   - Record internal marks (0–40) and external marks (0–60).
   - Automatic calculation of Total Marks out of 100.
   - Add, Edit, Delete marks records.

4. **📅 Attendance Tracking**
   - Log total classes and attended classes.
   - Automatic attendance percentage and status badges (🟢 Good, 🟡 Warning, 🔴 Critical).

5. **📊 Student Analysis**
   - Individual student profile cards, strongest and weakest subject detection.
   - Stacked internal + external marks chart and subject attendance benchmark chart.

6. **🤖 AI Prediction Engine**
   - **Linear Regression**: Predicts expected final score (0–100%).
   - **Random Forest Classifier**: Categorizes risk level (Low Risk, Medium Risk, High Risk).
   - Displays prediction badge, natural-language advice, and probability breakdown.

7. **📥 CSV Data Importer**
   - Drag-and-drop `.csv` file uploader with download template button.
   - Row/column summary, data preview table, automated validation, and database import.
   - Duplicate protection: updates existing records in place without creating duplicates.

---

## 📁 Project Structure & Line Count

| File | Purpose | Lines of Code |
|---|---|---|
| **`app.py`** | Main Streamlit interface (all 7 pages, charts & forms) | ~260 lines |
| **`database.py`** | SQLite database setup & 4 table schemas | ~55 lines |
| **`crud.py`** | Database functions (Students, Marks, Attendance, CSV Import) | ~180 lines |
| **`ml_model.py`** | Linear Regression & Random Forest models | ~55 lines |
| **`utils/analytics.py`** | Averages, pass rate, risk student calculations | ~55 lines |
| **`utils/visualizations.py`** | Plotly charts using concise Plotly Express | ~80 lines |
| **Total** | **Entire Project Codebase** | **~685 lines** |

---

## 🎓 Viva Cheat Sheet: How to Explain Each File in 30 Seconds

### 1. `database.py` (Database Layer)
> *"This file connects to SQLite (`eduanalytics.db`) and creates our 4 relational tables: `students`, `marks`, `attendance`, and `predictions`. We use foreign keys with `ON DELETE CASCADE` so deleting a student cleans up all their records automatically."*

### 2. `ml_model.py` (Machine Learning Layer)
> *"We use Scikit-Learn to train two models on 4 student features (internals, attendance, assignments, previous semester):*
> *1. **Linear Regression** predicts the continuous expected final mark (0–100%).*
> *2. **Random Forest Classifier** categorizes risk into Low Risk, Medium Risk, or High Risk.*
> *Our `predict()` function takes 4 numbers and returns the predicted score, risk badge, and actionable advice."*

### 3. `crud.py` (Data Operations Layer)
> *"This file contains functions to Create, Read, Update, and Delete records in SQLite. It also has `validate_student_csv()` to verify uploaded files and `import_csv_data()` which updates existing students safely without creating duplicate rows."*

### 4. `utils/analytics.py` & `utils/visualizations.py` (Analytics & Charts)
> *"`analytics.py` computes summary statistics like average marks, pass percentages, and at-risk student counts. `visualizations.py` uses Plotly Express to generate clean bar charts, line trends, and donut charts in just 2 to 4 lines per chart."*

### 5. `app.py` (Frontend User Interface)
> *"This is our Streamlit app. It uses `st.sidebar.radio()` to route between 7 pages: Dashboard, Students, Marks, Attendance, Student Analysis, AI Prediction, and CSV Upload."*

---

## 🚀 How to Run the Application

```bash
streamlit run app.py
```
