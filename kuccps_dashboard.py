import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

# Page setup
st.set_page_config(page_title="KUCCPS Dashboard", layout="wide")
st.title("📊 KUCCPS INTERACTIVE DASHBOARD")

# File upload
uploaded_file = st.file_uploader("📂 Upload KUCCPS dataset (CSV or Excel)", type=["csv", "xlsx"])

# Function to categorize programmes into departments
def categorize_programme(programme_name):
    programme_name = programme_name.lower()  # Convert to lowercase for case-insensitive matching
    if any(keyword in programme_name for keyword in ["nursing", "medicine", "surgery", "clinical", "physiotherapy"]):
        return "Health Sciences"
    elif any(keyword in programme_name for keyword in ["engineering"]):
        return "Engineering"
    elif any(keyword in programme_name for keyword in ["computer", "cloud", "software"]):
        return "ICT / Tech"
    elif any(keyword in programme_name for keyword in ["commerce", "business"]):
        return "Business"
    elif any(keyword in programme_name for keyword in ["law"]):
        return "Arts & Humanities"
    elif any(keyword in programme_name for keyword in ["education", "teaching"]):
        return "Education"
    elif any(keyword in programme_name for keyword in ["agric"]):
        return "Agriculture"
    elif any(keyword in programme_name for keyword in ["tourism", "hospitality"]):
        return "Hospitality & Tourism"
    elif any(keyword in programme_name for keyword in ["architecture"]):
        return "Architecture & Planning"
    elif any(keyword in programme_name for keyword in ["statistics", "mathematics"]):
        return "Math & Science"
    else:
        return "Other"

if uploaded_file is not None:
    # Load file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file, engine="openpyxl")

    # Convert 'application_day' like 'Day 1' → 1 (int)
    if "application_day" in df.columns:
        df["application_day"] = df["application_day"].astype(str).str.extract(r'(\d+)').astype(float)
    
    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("#", "number")
    
    # Categorize programmes into departments
    df['department'] = df['programme_name'].apply(categorize_programme)

    st.success("✅ File loaded successfully!")
    st.subheader("🔍 Data Preview")
    st.dataframe(df.head())

    # ========== Filters ==========
    st.sidebar.header("🔎 Filter Data")
    selected_sponsors = st.sidebar.multiselect("Select Institution Sponsor", options=df["institution_sponsor_id"].unique(), default=df["institution_sponsor_id"].unique())
    selected_stages = st.sidebar.multiselect("Select Application Stage", options=df["application_stage_id"].unique(), default=df["application_stage_id"].unique())
    selected_types = st.sidebar.multiselect("Select Programme Type", options=df["programme_type_id"].unique(), default=df["programme_type_id"].unique())
    selected_programmes = st.sidebar.multiselect("Select Programme Name", options=df["programme_name"].unique(), default=df["programme_name"].unique())
    selected_institutions = st.sidebar.multiselect("Select Institution Name", options=df["institution_name"].unique(), default=df["institution_name"].unique())
    selected_grades = st.sidebar.multiselect("Select Mean Grade", options=df["mean_grade_id"].unique(), default=df["mean_grade_id"].unique())
    selected_cycles = st.sidebar.multiselect("Select Placement Cycle", options=df["placement_cycle_id"].unique(), default=df["placement_cycle_id"].unique())
    selected_departments = st.sidebar.multiselect("Select Department", options=df["department"].unique(), default=df["department"].unique())

    # ========== Apply Filters ==========
    filtered_df = df[
        (df["institution_sponsor_id"].isin(selected_sponsors)) &
        (df["application_stage_id"].isin(selected_stages)) &
        (df["programme_type_id"].isin(selected_types)) &
        (df["programme_name"].isin(selected_programmes)) &
        (df["institution_name"].isin(selected_institutions)) &
        (df["mean_grade_id"].isin(selected_grades)) &
        (df["placement_cycle_id"].isin(selected_cycles)) &
        (df["department"].isin(selected_departments))
    ]

    # ===== VISUALIZATIONS =====
    # ========== Chart 1: Programme Name Breakdown ==========
    st.subheader("🧭 Programme Name Breakdown")
    if "programme_name" in filtered_df.columns:
        cat_counts = filtered_df["programme_name"].value_counts().reset_index()
        cat_counts.columns = ["programme_name", "count"]

        fig1 = px.pie(
            cat_counts,
            names="programme_name",
            values="count",
            hole=0.5,
            color_discrete_sequence=px.colors.sequential.RdBu,
        )
        fig1.update_traces(textinfo="percent+label")
        st.plotly_chart(fig1, use_container_width=True)

        # Download button for Chart 1
        img_bytes1 = pio.to_image(fig1, format="png", engine="kaleido")
        st.download_button("📥 Download Programme Breakdown", img_bytes1, "programme_pie.png", "image/png")
    else:
        st.warning("⚠️ 'programme_name' column not found.")

    # ========== Chart 2: Public vs Private ==========
    st.subheader("🏫 Institution Sponsorship Summary")
    if "institution_sponsor_id" in filtered_df.columns:
        sponsor_counts = filtered_df["institution_sponsor_id"].value_counts().reset_index()
        sponsor_counts.columns = ["sponsorship", "count"]

        fig2 = px.bar(
            sponsor_counts,
            x="sponsorship",
            y="count",
            color="sponsorship",
            text="count",
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        fig2.update_layout(xaxis_title="Institution Type", yaxis_title="Number of Institutions")
        st.plotly_chart(fig2, use_container_width=True)

        # Download button for Chart 2
        img_bytes2 = pio.to_image(fig2, format="png", engine="kaleido")
        st.download_button("📥 Download Institution Sponsorship Chart", img_bytes2, "institution_sponsorship.png", "image/png")
    else:
        st.warning("⚠️ 'institution_sponsor_id' column not found.")

    # ========== Chart 3: Student Count per Programme ==========
    st.subheader("📚 Student Count per Programme")
    if "programme_name" in filtered_df.columns and "number_student_id" in filtered_df.columns:
        student_counts = filtered_df.groupby("programme_name")["number_student_id"].count().reset_index()
        student_counts = student_counts.sort_values(by="number_student_id", ascending=False)

        fig3 = px.bar(
            student_counts,
            x="programme_name",
            y="number_student_id",
            color="programme_name",
            text="number_student_id",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig3.update_layout(
            xaxis_title="Programme Name",
            yaxis_title="Total Students",
            showlegend=False
        )
        st.plotly_chart(fig3, use_container_width=True)

        # Download button for Chart 3
        img_bytes3 = pio.to_image(fig3, format="png", engine="kaleido")
        st.download_button("📥 Download Student Count Chart", img_bytes3, "student_count_per_programme.png", "image/png")
    else:
        st.warning("⚠️ Required columns missing.")

    # ========== Chart 4: Application Trend ==========
    st.subheader("📈 Application Trend by Day")
    if "application_day" in filtered_df.columns:
        day_counts = filtered_df["application_day"].value_counts().sort_index().reset_index()
        day_counts.columns = ["application_day", "count"]

        fig4 = px.line(
            day_counts,
            x="application_day",
            y="count",
            markers=True,
            title="Application Submissions Over Days",
            labels={"application_day": "Application Day", "count": "Number of Applications"},
        )
        st.plotly_chart(fig4, use_container_width=True)

        # Download button for Chart 4
        img_bytes4 = pio.to_image(fig4, format="png", engine="kaleido")
        st.download_button("📥 Download Application Trend Chart", img_bytes4, "application_trend.png", "image/png")
    else:
        st.warning("⚠️ 'application_day' column not found.")

    # ========== Application Day Filter ==========
    st.sidebar.markdown("### ⏱️ Filter by Application Day")
    min_day, max_day = int(df["application_day"].min()), int(df["application_day"].max())
    selected_days = st.sidebar.slider("Select Application Day Range", min_value=min_day, max_value=max_day, value=(min_day, max_day))

    # Include day filter in the main filtered_df
    filtered_df = filtered_df[
        (filtered_df["application_day"] >= selected_days[0]) & 
        (filtered_df["application_day"] <= selected_days[1])
    ]

    # ========== Animated Chart by Day ==========
    st.subheader("📊 Programme Demand by Application Day")

    if "programme_name" in filtered_df.columns and "number_student_id" in filtered_df.columns and "application_day" in filtered_df.columns:
        animated_df = filtered_df.groupby(["application_day", "programme_name"])["number_student_id"].count().reset_index()
        animated_df.columns = ["application_day", "programme_name", "student_count"]

        fig_animated = px.bar(
            animated_df,
            x="programme_name",
            y="student_count",
            animation_frame="application_day",
            color="programme_name",
            range_y=[0, animated_df["student_count"].max() + 5],
            title="📊 Student Count by Programme Over Application Days",
            labels={"programme_name": "Programme", "student_count": "Students"},
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig_animated.update_layout(xaxis_title="Programme", yaxis_title="Student Count", showlegend=False)
        st.plotly_chart(fig_animated, use_container_width=True)
    else:
        st.warning("⚠️ Required columns for animation are missing.")

    # ========== 📌 Dynamic Summary KPIs ==========
    st.subheader("📌 Summary Insights (Filtered View)")

    total_students = filtered_df["number_student_id"].nunique() if "number_student_id" in filtered_df.columns else 0
    total_institutions = filtered_df["institution_name"].nunique() if "institution_name" in filtered_df.columns else 0
    total_programmes = filtered_df["programme_name"].nunique() if "programme_name" in filtered_df.columns else 0
    top_day = (
        filtered_df["application_day"].mode()[0]
        if "application_day" in filtered_df.columns and not filtered_df["application_day"].isna().all()
        else "N/A"
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎓 Students", f"{total_students:,}")
    col2.metric("🏫 Institutions", f"{total_institutions:,}")
    col3.metric("📚 Programmes", f"{total_programmes:,}")
    col4.metric("📅 Most Active Day", f"Day {top_day}" if top_day != "N/A" else "N/A")

    # ===== SUMMARY TABLE =====
    st.subheader("📋 Summary Table of Filtered Data")
    st.dataframe(filtered_df.head(50))

    # ===== DOWNLOAD OPTION =====
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Filtered Data as CSV", data=csv, file_name="filtered_kuccps_data.csv", mime="text/csv")

    # Additional Visualizations
    # Chart 5: Mean Grade Distribution
    st.subheader("🎯 Mean Grade Distribution")
    if "mean_grade_id" in filtered_df.columns:
        grade_counts = filtered_df["mean_grade_id"].value_counts().sort_index().reset_index()
        grade_counts.columns = ["mean_grade_id", "count"]

        fig5 = px.bar(
            grade_counts,
            x="mean_grade_id",
            y="count",
            color="mean_grade_id",
            text="count",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig5.update_layout(
            xaxis_title="Mean Grade",
            yaxis_title="Number of Students",
            showlegend=False
        )
        st.plotly_chart(fig5, use_container_width=True)

        # Download button for Chart 5
        img_bytes5 = pio.to_image(fig5, format="png", engine="kaleido")
        st.download_button("📥 Download Mean Grade Chart", img_bytes5, "mean_grade_distribution.png", "image/png")
    else:
        st.warning("⚠️ 'mean_grade_id' column not found.")

    # Chart 6: Applications by Placement Cycle
    st.subheader("🔄 Applications by Placement Cycle")
    if "placement_cycle_id" in filtered_df.columns:
        cycle_counts = filtered_df["placement_cycle_id"].value_counts().sort_index().reset_index()
        cycle_counts.columns = ["placement_cycle_id", "count"]

        fig6 = px.bar(
            cycle_counts,
            x="placement_cycle_id",
            y="count",
            color="placement_cycle_id",
            text="count",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig6.update_layout(
            xaxis_title="Placement Cycle",
            yaxis_title="Number of Applications",
            showlegend=False
        )
        st.plotly_chart(fig6, use_container_width=True)

        # Download button for Chart 6
        img_bytes6 = pio.to_image(fig6, format="png", engine="kaleido")
        st.download_button("📥 Download Placement Cycle Chart", img_bytes6, "applications_by_placement_cycle.png", "image/png")
    else:
        st.warning("⚠️ 'placement_cycle_id' column not found.")

    # Chart 7: Top 10 Institutions by Student Count
    st.subheader("🏆 Top 10 Institutions by Student Count")
    if "institution_name" in filtered_df.columns and "number_student_id" in filtered_df.columns:
        top_institutions = (
            filtered_df.groupby("institution_name")["number_student_id"]
            .count()
            .reset_index()
            .sort_values(by="number_student_id", ascending=False)
            .head(10)
        )

        fig7 = px.bar(
            top_institutions,
            x="institution_name",
            y="number_student_id",
            color="institution_name",
            text="number_student_id",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig7.update_layout(
            xaxis_title="Institution Name",
            yaxis_title="Student Count",
            showlegend=False
        )
        st.plotly_chart(fig7, use_container_width=True)

        # Download button for Chart 7
        img_bytes7 = pio.to_image(fig7, format="png", engine="kaleido")
        st.download_button("📥 Download Top Institutions Chart", img_bytes7, "top_10_institutions.png", "image/png")
    else:
        st.warning("⚠️ Required columns for institution chart are missing.")

    # Chart 8: Application Stage Distribution
    st.subheader("📝 Application Stage Distribution")
    if "application_stage_id" in filtered_df.columns:
        stage_counts = filtered_df["application_stage_id"].value_counts().sort_index().reset_index()
        stage_counts.columns = ["application_stage_id", "count"]

        fig8 = px.pie(
            stage_counts,
            names="application_stage_id",
            values="count",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        fig8.update_traces(textinfo="percent+label")
        st.plotly_chart(fig8, use_container_width=True)

        # Download button for Chart 8
        img_bytes8 = pio.to_image(fig8, format="png", engine="kaleido")
        st.download_button("📥 Download Application Stage Chart", img_bytes8, "application_stage_distribution.png", "image/png")
    else:
        st.warning("⚠️ 'application_stage_id' column not found.")

# ====== ABOUT SECTION ======
with st.expander("ℹ️ About this Dashboard", expanded=False):
    st.markdown("""
    **KUCCPS Interactive Dashboard**  
    This dashboard provides a comprehensive overview and analysis of KUCCPS application data. It enables users to explore trends, distributions, and key metrics interactively, supporting data-driven decision making for supervisors and stakeholders.

    **Key Features & Insights:**
    - **Programme Popularity:** Visualizes which programmes are most in demand, both as a breakdown (pie chart) and by student count (bar chart).
    - **Institution Sponsorship:** Shows the distribution of applications by institution type (public/private).
    - **Application Trends:** Displays application trends over time and by day, including an animated view.
    - **Mean Grade Distribution:** Illustrates the academic profile of applicants.
    - **Placement Cycle Analysis:** Reveals application distribution across placement cycles.
    - **Top Institutions:** Highlights institutions attracting the most students.
    - **Application Stages:** Shows applicant progress through various stages.
    - **Dynamic Filtering:** All insights can be filtered by sponsor, stage, programme, institution, grade, and cycle.
    - **Summary KPIs:** Quick metrics on students, institutions, programmes, and most active application day.
    - **Data Export:** Download filtered data and all visualizations for further analysis or reporting.

    _Tip: Use the dashboard live to demonstrate how changing filters updates insights in real time. Highlight any surprising trends or areas for further investigation._
    """)
# ====== HELP SECTION ======
with st.expander("❓ Help & Usage Guide", expanded=False):
    st.markdown("""
    ### 📚 Help & Usage Guide

    **How to Use the Dashboard:**
    - **Upload Data:** Start by uploading your KUCCPS dataset in CSV or Excel format using the uploader at the top.
    - **Apply Filters:** Use the sidebar to filter data by Institution Sponsor, Application Stage, Programme Type, Programme Name, Institution Name, Mean Grade, Placement Cycle, and Application Day.
    - **Explore Visualizations:** The main area displays interactive charts and summary metrics that update based on your selected filters.
    - **Download Results:** Download filtered data and individual charts using the provided download buttons.

    **Filter Descriptions:**
    - **Institution Sponsor:** Filter applications by the sponsoring body of the institution (e.g., public, private).
    - **Application Stage:** Select which stages of the application process to analyze.
    - **Programme Type:** Choose the type of programme (e.g., diploma, degree).
    - **Programme Name:** Focus on specific programmes of interest.
    - **Institution Name:** Analyze data for selected institutions.
    - **Mean Grade:** Filter applicants by their mean grade.
    - **Placement Cycle:** Select placement cycles to include in the analysis.
    - **Application Day:** Use the slider to analyze trends over specific application days.

    _Tip: Hover over charts for more details. Use the download buttons to save charts and filtered data for reporting or further analysis._
    """)
st.info("Please upload a KUCCPS dataset to get started.")
