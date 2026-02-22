# ======================================================
# SCHOOL PERFORMANCE DASHBOARD - DARK PREMIUM VERSION
# Multi-Select Filters + CSV Download Feature
# ======================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="School Performance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- DARK PREMIUM CSS ----------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0e1117;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

h1, h2, h3 {
    color: #ffffff !important;
}

.metric-card {
    background: #1f2937;
    padding: 22px;
    border-radius: 16px;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.6);
    text-align: center;
    transition: 0.3s;
}

.metric-card:hover {
    transform: scale(1.05);
}

.metric-title {
    font-size: 14px;
    color: #9ca3af;
}

.metric-value {
    font-size: 32px;
    font-weight: bold;
    color: #3b82f6;
}

.block-container {
    background-color: #0e1117;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN SYSTEM ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.markdown("<h1 style='text-align:center;'>🔐 School Dashboard Login</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# ======================================================
# DATA MODELING
# ======================================================

np.random.seed(42)

teachers = ["Mr. Sharma", "Ms. Patel", "Mrs. Iyer", "Mr. Khan"]
sections = ["A", "B", "C"]

data = []
for i in range(300):
    data.append([
        i + 1,
        random.choice(teachers),
        random.choice(sections),
        random.randint(50, 100),
        random.randint(0, 5),
        random.choice(["Yes", "No"]),
        random.choice(pd.date_range("2024-01-01", "2024-06-01"))
    ])

df = pd.DataFrame(data, columns=[
    "Student_ID", "Teacher", "Section",
    "Score", "Late_Count", "Attrition", "Date"
])

df["Score"] = df["Score"].fillna(df["Score"].mean())
df["Performance_%"] = round((df["Score"] / 100) * 100, 2)

# ======================================================
# SIDEBAR NAVIGATION + FILTERS
# ======================================================

st.sidebar.title("📌 Navigation")
page = st.sidebar.radio(
    "",
    ["Dashboard", "Teacher", "Late Count & Attrition"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Filters")

selected_teachers = st.sidebar.multiselect(
    "Select Teacher(s)",
    teachers,
    default=teachers
)

selected_sections = st.sidebar.multiselect(
    "Select Section(s)",
    sections,
    default=sections
)

# Apply Filters
filtered_df = df[
    (df["Teacher"].isin(selected_teachers)) &
    (df["Section"].isin(selected_sections))
]

# ---------------- CSV DOWNLOAD FEATURE ----------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Download Data")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.sidebar.download_button(
    label="Download Filtered Data (CSV)",
    data=csv_data,
    file_name="filtered_school_data.csv",
    mime="text/csv"
)

# ======================================================
# DASHBOARD PAGE
# ======================================================

if page == "Dashboard":

    st.title("📊 Overall Performance Dashboard")

    total_students = filtered_df["Student_ID"].nunique()
    avg_score = round(filtered_df["Score"].mean(), 2)
    avg_performance = round(filtered_df["Performance_%"].mean(), 2)

    col1, col2, col3 = st.columns(3)

    metrics = [
        ("Total Students", total_students),
        ("Average Score", avg_score),
        ("Performance %", f"{avg_performance}%")
    ]

    for col, (title, value) in zip([col1, col2, col3], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    col_gauge, col_bar = st.columns(2)

    with col_gauge:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_performance,
            title={'text': "Performance Index"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#3b82f6"}}
        ))
        fig_gauge.update_layout(template="plotly_dark")
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_bar:
        section_avg = filtered_df.groupby("Section")["Score"].mean().reset_index()
        fig_bar = px.bar(
            section_avg,
            x="Section",
            y="Score",
            color="Section",
            text_auto=True
        )
        fig_bar.update_layout(template="plotly_dark", showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

# ======================================================
# TEACHER PAGE
# ======================================================

elif page == "Teacher":

    st.title("👩‍🏫 Teacher Performance")

    teacher_summary = filtered_df.groupby("Teacher").agg({
        "Score": "mean",
        "Late_Count": "sum"
    }).reset_index()

    col1, col2 = st.columns(2)

    with col1:
        fig_line = px.line(
            filtered_df.sort_values("Date"),
            x="Date",
            y="Score",
            color="Teacher"
        )
        fig_line.update_layout(template="plotly_dark")
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        fig_bar = px.bar(
            teacher_summary,
            x="Teacher",
            y="Score",
            color="Teacher",
            text_auto=True
        )
        fig_bar.update_layout(template="plotly_dark", showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.dataframe(
        teacher_summary.style.background_gradient(cmap="Blues"),
       
    )

# ======================================================
# LATE COUNT & ATTRITION PAGE
# ======================================================

elif page == "Late Count & Attrition":

    st.title("⏰ Late Count & Attrition Analysis")

    col1, col2 = st.columns(2)

    with col1:
        late_summary = filtered_df.groupby("Teacher")["Late_Count"].sum().reset_index()
        fig_late = px.bar(
            late_summary,
            x="Teacher",
            y="Late_Count",
            color="Late_Count",
            text_auto=True
        )
        fig_late.update_layout(template="plotly_dark", showlegend=False)
        st.plotly_chart(fig_late, use_container_width=True)

    with col2:
        fig_attrition = px.pie(
            filtered_df,
            names="Attrition",
            hole=0.6
        )
        fig_attrition.update_layout(template="plotly_dark")

        st.plotly_chart(fig_attrition, use_container_width=True)
