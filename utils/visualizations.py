"""
Visualization utilities: creates clean Plotly charts in 2-4 lines using Plotly Express.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def empty_chart(title):
    """Returns a placeholder when no data exists."""
    fig = go.Figure()
    fig.add_annotation(text="No data available for selection", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
    fig.update_layout(title=title, height=320, xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig

def chart_subject_wise_marks(df):
    """Chart 1: Horizontal bar chart of subject averages."""
    if df.empty: return empty_chart("Subject-wise Average Marks")
    data = df.groupby("subject")["total_marks"].mean().round(1).reset_index()
    fig = px.bar(data, x="total_marks", y="subject", orientation="h", text="total_marks", title="Subject Average Marks", color="total_marks", color_continuous_scale="Blues")
    fig.update_layout(height=340, xaxis_title="Average Marks", yaxis_title="", coloraxis_showscale=False)
    return fig

def chart_semester_performance(df):
    """Chart 2: Line chart of semester performance trend."""
    if df.empty or "semester" not in df.columns: return empty_chart("Semester Trend")
    data = df.groupby("semester")["total_marks"].mean().round(1).reset_index()
    data["semester"] = data["semester"].apply(lambda s: f"Sem {s}")
    fig = px.line(data, x="semester", y="total_marks", markers=True, title="Semester Performance Trend")
    fig.update_layout(height=340, yaxis=dict(range=[0, 105]), yaxis_title="Average Marks", xaxis_title="")
    return fig

def chart_pass_fail_distribution(df):
    """Chart 3: Donut chart of pass vs fail distribution."""
    if df.empty: return empty_chart("Pass vs Fail")
    counts = pd.DataFrame({
        "Status": ["Pass (≥40)", "Fail (<40)"],
        "Count": [(df["total_marks"] >= 40).sum(), (df["total_marks"] < 40).sum()]
    })
    fig = px.pie(counts, names="Status", values="Count", hole=0.5, title="Pass vs Fail Distribution", color="Status", color_discrete_map={"Pass (≥40)": "#10B981", "Fail (<40)": "#EF4444"})
    fig.update_layout(height=340)
    return fig

def chart_attendance_vs_marks(m_df, a_df):
    """Chart 4: Scatter plot correlating attendance and marks."""
    if m_df.empty or a_df.empty: return empty_chart("Attendance vs Marks")
    merged = pd.merge(m_df.groupby("student_id")["total_marks"].mean().round(1), a_df.groupby("student_id")["attendance_percentage"].mean().round(1), on="student_id").reset_index()
    fig = px.scatter(merged, x="attendance_percentage", y="total_marks", hover_data=["student_id"], title="Attendance vs Marks Correlation")
    fig.add_hline(y=40, line_dash="dash", line_color="#EF4444", annotation_text="Pass Line (40)")
    fig.add_vline(x=75, line_dash="dash", line_color="#2563EB", annotation_text="75% Req")
    fig.update_layout(height=340, xaxis_title="Attendance %", yaxis_title="Marks / 100")
    return fig

def chart_performance_distribution(df):
    """Chart 5: Bar chart showing grade brackets."""
    if df.empty: return empty_chart("Performance Distribution")
    labels = ["Fail (<40)", "Pass (40-59)", "First Class (60-74)", "Distinction (75-100)"]
    bracket = pd.cut(df["total_marks"], bins=[0, 40, 60, 75, 100], labels=labels, right=False)
    counts = bracket.value_counts()[labels].reset_index()
    counts.columns = ["Bracket", "Count"]
    fig = px.bar(counts, x="Bracket", y="Count", text="Count", title="Performance Distribution", color="Bracket")
    fig.update_layout(height=340, showlegend=False)
    return fig

def chart_student_subject_marks(df):
    """Stacked bar chart of Internal (40) + External (60) for a student."""
    if df.empty: return empty_chart("Subject Marks")
    fig = go.Figure(data=[
        go.Bar(name="Internal (40)", x=df["subject"], y=df["internal_marks"], marker_color="#6366F1"),
        go.Bar(name="External (60)", x=df["subject"], y=df["external_marks"], marker_color="#2563EB")
    ])
    fig.update_layout(barmode="stack", title="Subject Marks (Internal + External)", height=340, yaxis=dict(range=[0, 110]))
    return fig

def chart_student_subject_attendance(df):
    """Bar chart of attendance % per subject for a student."""
    if df.empty: return empty_chart("Subject Attendance")
    fig = px.bar(df, x="subject", y="attendance_percentage", text="attendance_percentage", title="Subject Attendance %")
    fig.add_hline(y=75, line_dash="dash", line_color="#2563EB", annotation_text="75% Goal")
    fig.update_layout(height=340, yaxis=dict(range=[0, 110]))
    return fig

def chart_student_semester_trend(df):
    """Line chart showing student semester performance trend."""
    return chart_semester_performance(df)
