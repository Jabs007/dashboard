import streamlit as st
import pandas as pd
from functools import reduce
import operator
import plotly.express as px
import plotly.io as pio

# ===== PAGE SETUP & CUSTOMIZATION =====
st.set_page_config(
    page_title="KUCCPS DASHBOARD",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visuals (targeting stable selectors)
st.markdown("""
    <style>
        /* Padding for main container */
        section.main > div { padding-top: 1.5rem !important; }
        /* Button styles */
        .stButton > button {
            color: white;
            background: linear-gradient(90deg, #4e4376 0%, #2b5876 100%);
            border-radius: 8px;
            border: none;
            padding: 0.5em 1.5em;
            font-weight: 600;
        }
        .stDownloadButton > button {
            color: white;
            background: linear-gradient(90deg, #38ef7d 0%, #11998e 100%);
            border-radius: 8px;
            border: none;
            padding: 0.5em 1.5em;
            font-weight: 600;
        }
        /* Radio buttons horizontal */
        .stRadio > div { flex-direction: row; }
        /* Checkbox label bold */
        .stCheckbox > label { font-weight: 500; }
        /* Slider color */
        .stSlider > div { color: #2b5876; }
        /* DataFrame background */
        .stDataFrame { background: #f8fafc; }
        /* Metric background */
        .stMetric { background: #f0f4f8; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# Main Title and Subtitle
st.title("📊 KUCCPS INTERACTIVE DASHBOARD")
st.caption("Empowering supervisors, analysts, and stakeholders to explore and analyze KUCCPS application data interactively.")

# ===== File Upload Section (Enhanced & Improved) =====
st.markdown("### 📂 Upload Your KUCCPS Dataset")
with st.container():
    uploaded_file = st.file_uploader(
        "Upload a KUCCPS dataset (CSV or Excel)",
        type=["csv", "xlsx"],
        accept_multiple_files=False,
        help="Accepted formats: .csv, .xlsx. For best results, ensure your file includes columns like 'programme_name', 'institution_name', 'mean_grade_id', etc."
    )
    st.caption(
        "Tip: Download a sample template from [here](https://github.com/kuccps-dashboard/sample-data/raw/main/sample_kuccps_data.xlsx) if unsure about the required format."
    )
    st.markdown(
        """
        <small>
        <ul>
            <li>Large files may take a few seconds to load.</li>
            <li>All processing is done securely on the server; your data is not shared.</li>
            <li>Supported Excel files: .xlsx only (not .xls).</li>
            <li>For best results, ensure your file has clear headers and no merged cells.</li>
        </ul>
        </small>
        """, unsafe_allow_html=True
    )
    if uploaded_file is None:
        st.info("Please upload a CSV or Excel file to unlock dashboard features.")
    # ===== Data Loading, Cleaning, and Filtering Section (Enhanced) =====

    # Enhanced department categorization with improved keyword matching and robustness
    def categorize_programme(programme_name):
        if pd.isna(programme_name):
            return "Other"
        name = str(programme_name).lower()
        mapping = [
            (["nursing", "medicine", "surgery", "clinical", "physiotherapy", "pharmacy", "dental", "public health", "medical", "nutrition", "biomedical", "anatomy", "physiology", "radiology", "midwifery"], "Health Sciences"),
            (["engineering", "civil", "mechanical", "electrical", "mechatronic", "telecom", "automotive", "chemical", "mining", "manufacturing", "industrial", "aerospace", "petroleum", "energy", "environmental engineering"], "Engineering"),
            (["computer", "ict", "information technology", "cloud", "software", "data science", "ai", "cyber", "informatics", "it", "computing", "machine learning", "robotics", "network"], "ICT / Tech"),
            (["commerce", "business", "accounting", "procurement", "finance", "marketing", "management", "entrepreneurship", "economics", "human resource", "insurance", "banking", "audit", "supply chain"], "Business"),
            (["law", "criminology", "justice", "legal", "forensic"], "Law & Humanities"),
            (["education", "teaching", "pedagogy", "curriculum", "teacher", "instructional", "educational"], "Education"),
            (["agric", "horticulture", "animal", "crop", "food science", "agribusiness", "soil", "dairy", "veterinary", "forestry", "fisheries", "plant", "agronomy"], "Agriculture"),
            (["tourism", "hospitality", "hotel", "leisure", "travel", "event management", "culinary"], "Hospitality & Tourism"),
            (["architecture", "planning", "urban", "landscape", "built environment", "construction", "quantity survey", "interior design"], "Architecture & Planning"),
            (["statistics", "mathematics", "math", "actuarial", "quantitative", "applied math", "statistical"], "Math & Statistics"),
            (["science", "biology", "chemistry", "physics", "biochemistry", "microbiology", "zoology", "botany", "geology", "environmental", "ecology", "genetics", "astronomy", "marine science"], "Pure & Applied Sciences"),
            (["arts", "music", "fine art", "design", "drama", "theatre", "literature", "philosophy", "history", "language", "linguistics", "communication", "media", "film", "animation", "creative"], "Arts & Humanities"),
            (["social work", "sociology", "psychology", "community", "development", "anthropology", "counseling", "public administration", "international relations", "political science"], "Social Sciences"),
            (["sports", "physical education", "recreation", "exercise", "fitness", "sport"], "Sports & Recreation"),
            (["aviation", "aeronautical", "pilot", "aircraft", "flight"], "Aviation"),
            (["marine", "maritime", "ocean", "fisheries", "aquatic", "naval"], "Marine & Fisheries"),
            (["library", "records", "information science", "archival", "documentation"], "Library & Information Science"),
            (["logistics", "supply chain", "transport", "shipping", "freight", "warehousing"], "Logistics & Transport"),
            (["fashion", "textile", "garment", "apparel", "clothing", "costume"], "Fashion & Textile"),
            (["journalism", "mass communication", "broadcast", "public relations", "media studies"], "Media & Communication"),
            (["real estate", "property", "land management", "valuation"], "Real Estate & Land Management"),
            (["military", "defense", "security", "peace studies"], "Security & Defense"),
            (["environment", "conservation", "sustainability", "climate"], "Environmental Studies"),
            (["food", "nutrition", "dietetics", "culinary"], "Food & Nutrition"),
        ]
        for keywords, dept in mapping:
            if any(k in name for k in keywords):
                return dept
        return "Other"

    if uploaded_file is not None:
        # Load file with robust error handling and preview
        try:
            # Support both CSV and Excel, handle encoding issues
            if uploaded_file.name.lower().endswith(".csv"):
                # Try utf-8, fallback to ISO-8859-1 if needed
                try:
                    df = pd.read_csv(uploaded_file, encoding="utf-8")
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
            elif uploaded_file.name.lower().endswith(".xlsx"):
                df = pd.read_excel(uploaded_file, engine="openpyxl")
            else:
                st.error("Unsupported file format. Please upload a CSV or .xlsx Excel file.")
                st.stop()
            # Check for empty file
            if df.empty:
                st.error("The uploaded file is empty. Please check your data and try again.")
                st.stop()
            # Check for minimum required columns
            required_cols = {"programme_name", "institution_name", "number_student_id"}
            if not required_cols.intersection(set(df.columns)):
                st.warning(
                    f"Warning: The uploaded file does not contain any of the required columns: {', '.join(required_cols)}. "
                    "Some dashboard features may not work as expected."
                )
        except Exception as e:
            st.error(f"❌ Error loading file: {e}")
            st.stop()

        # Clean column names: lower, underscores, remove special chars
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("#", "number")
            .str.replace(r"[^\w_]", "", regex=True)
        )

        # Convert 'application_day' like 'Day 1' → 1 (int)
        if "application_day" in df.columns:
            df["application_day"] = (
            df["application_day"]
            .astype(str)
            .str.extract(r'(\d+)')
            .astype(float)
            )
            # If all values are integers, cast to int for cleaner display
            if df["application_day"].dropna().apply(float.is_integer).all():
                df["application_day"] = df["application_day"].astype("Int64")

        # Categorize programmes into departments (robust to missing column)
        if "programme_name" in df.columns:
            df["department"] = df["programme_name"].apply(categorize_programme)
        else:
            df["department"] = "Other"

        # Remove duplicate rows if all columns are identical (optional, for cleaner data)
        df = df.drop_duplicates()

        # Show info about missing values
        missing_info = df.isnull().sum()
        missing_cols = missing_info[missing_info > 0]
        if not missing_cols.empty:
            st.warning(
            f"Columns with missing values: {', '.join(missing_cols.index)}. "
            "Consider cleaning your data for best results."
            )

        st.success("✅ File loaded successfully!")
        st.subheader("🔍 Data Preview")
        st.dataframe(df.head(20), use_container_width=True)

        # ========== Sidebar Filters (Enhanced & Robust) ==========
        st.sidebar.header("🔎 Filter Data")

        def sidebar_multiselect(label, col, default_all=True, help_text=None):
            """Reusable multiselect with graceful fallback if column missing."""
            if col in df.columns:
                options = sorted([str(x) for x in df[col].dropna().unique()])
                default = options if default_all else []
                return st.sidebar.multiselect(label, options=options, default=default, help=help_text)
            return []

        selected_sponsors = sidebar_multiselect(
            "Institution Sponsor", "institution_sponsor_id", help_text="Filter by sponsoring body (public/private)"
        )
        selected_stages = sidebar_multiselect(
            "Application Stage", "application_stage_id", help_text="Filter by stage of application process"
        )
        selected_types = sidebar_multiselect(
            "Programme Type", "programme_type_id", help_text="Filter by type of programme (degree, diploma, etc.)"
        )
        selected_programmes = sidebar_multiselect(
            "Programme Name", "programme_name", default_all=False, help_text="Select specific academic programmes"
        )
        selected_institutions = sidebar_multiselect(
            "Institution Name", "institution_name", default_all=False, help_text="Focus on one or more institutions"
        )
        selected_grades = sidebar_multiselect(
            "Mean Grade", "mean_grade_id", help_text="Filter by applicant's mean grade"
        )
        selected_cycles = sidebar_multiselect(
            "Placement Cycle", "placement_cycle_id", help_text="Filter by placement cycle"
        )
        selected_departments = sidebar_multiselect(
            "Department", "department", help_text="Filter by programme department"
        )

        # ========== Apply Filters (Robust & Null-safe) ==========
        filter_conditions = []
        if selected_sponsors:
            filter_conditions.append(df["institution_sponsor_id"].astype(str).isin(selected_sponsors))
        if selected_stages:
            filter_conditions.append(df["application_stage_id"].astype(str).isin(selected_stages))
        if selected_types:
            filter_conditions.append(df["programme_type_id"].astype(str).isin(selected_types))
        if selected_programmes:
            filter_conditions.append(df["programme_name"].astype(str).isin(selected_programmes))
        if selected_institutions:
            filter_conditions.append(df["institution_name"].astype(str).isin(selected_institutions))
        if selected_grades:
            filter_conditions.append(df["mean_grade_id"].astype(str).isin(selected_grades))
        if selected_cycles:
            filter_conditions.append(df["placement_cycle_id"].astype(str).isin(selected_cycles))
        if selected_departments:
            filter_conditions.append(df["department"].astype(str).isin(selected_departments))

        if filter_conditions:
            filtered_df = df[reduce(operator.and_, filter_conditions)].copy()
        else:
            filtered_df = df.copy()

        # Show quick filter summary in sidebar
        st.sidebar.markdown(
            f"<small><b>Rows after filtering:</b> {len(filtered_df):,}</small>",
            unsafe_allow_html=True
        )

    # ===== VISUALIZATIONS =====
    # ========== Chart 1: Programme Department Breakdown (Enhanced) ==========
    st.subheader("🧭 Programme Department Breakdown")

    if uploaded_file is not None and "department" in filtered_df.columns:
        # Allow user to choose chart type
        chart1_type = st.radio(
            "Select Chart Type for Department Breakdown:",
            options=["Pie", "Bar"],
            horizontal=True,
            key="department_chart_type"
        )

        dept_counts = (
            filtered_df["department"]
            .value_counts(dropna=False)
            .reset_index()
            .rename(columns={"index": "department", "department": "count"})
        )
        # Optionally, show as percentage
        show_dept_pct = st.checkbox("Show as Percentage (Department)", value=False, key="department_pct")
        if show_dept_pct:
            total_dept = dept_counts["count"].sum()
            # Avoid division by zero
            if total_dept == 0:
                dept_counts["percentage"] = 0
            else:
                dept_counts["percentage"] = (dept_counts["count"] / total_dept * 100).round(2)

        if chart1_type == "Pie":
            fig1 = px.pie(
            dept_counts,
            names="department",
            values="count" if not show_dept_pct else "percentage",
            hole=0.5,
            color_discrete_sequence=px.colors.sequential.RdBu,
            )
            fig1.update_traces(
            textinfo="percent+label" if not show_dept_pct else "label+value",
            pull=[0.05]*len(dept_counts)
            )
        else:
            fig1 = px.bar(
            dept_counts,
            x="department",
            y="count" if not show_dept_pct else "percentage",
            text="count" if not show_dept_pct else "percentage",
            color="department",
            color_discrete_sequence=px.colors.sequential.RdBu,
            )
            fig1.update_layout(
            xaxis_title="Department",
            yaxis_title="Number of Applications" if not show_dept_pct else "Percentage (%)",
            showlegend=False,
            xaxis_tickangle=-30,
            margin=dict(b=120),
            height=500,
            )
            fig1.update_traces(
            texttemplate='%{text}' + ('' if not show_dept_pct else '%'),
            textposition='outside'
            )

        st.plotly_chart(fig1, use_container_width=True)

        # Show table of department counts
        st.markdown("#### 📋 Department Breakdown Table")
        st.dataframe(dept_counts, use_container_width=True)

        # Download button for Chart 1 (using HTML export as fallback)
        try:
            img_html1 = pio.to_html(fig1, full_html=False, include_plotlyjs='cdn')
            st.download_button(
                "📥 Download Programme Breakdown (HTML)", 
                img_html1, 
                "programme_department_breakdown.html", 
                "text/html"
            )
            st.info("PNG export requires 'kaleido', which may not work on Streamlit Cloud. Use the HTML download instead.")
        except Exception as e:
            st.warning("⚠️ Unable to export image. Please try downloading as HTML.")
    else:
        st.warning("⚠️ 'department' column not found.")

    # ========== Chart 2: Public vs Private ==========
    st.subheader("🏫 Institution Sponsorship Summary")
    if uploaded_file is not None and "institution_sponsor_id" in filtered_df.columns and "number_student_id" in filtered_df.columns:
        sponsor_counts = (
            filtered_df.groupby("institution_sponsor_id")["number_student_id"]
            .nunique()
            .reset_index()
            .rename(columns={"institution_sponsor_id": "Sponsorship", "number_student_id": "Unique Students"})
            .sort_values(by="Unique Students", ascending=False)
        )

        # Optionally, show as percentage
        show_sponsor_pct = st.checkbox("Show as Percentage (Sponsorship)", value=False, key="sponsor_pct")
        if show_sponsor_pct:
            total_sponsor = sponsor_counts["Unique Students"].sum()
            if total_sponsor == 0:
                sponsor_counts["percentage"] = 0
            else:
                sponsor_counts["percentage"] = (sponsor_counts["Unique Students"] / total_sponsor * 100).round(2)

        chart2_type = st.radio(
            "Select Chart Type for Sponsorship Breakdown:",
            options=["Bar", "Pie"],
            horizontal=True,
            key="sponsor_chart_type"
        )

        if chart2_type == "Bar":
            fig2 = px.bar(
                sponsor_counts,
                x="Sponsorship",
                y="Unique Students" if not show_sponsor_pct else "percentage",
                text="Unique Students" if not show_sponsor_pct else "percentage",
                color="Sponsorship",
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            fig2.update_layout(
                xaxis_title="Institution Sponsor",
                yaxis_title="Number of Unique Students" if not show_sponsor_pct else "Percentage (%)",
                showlegend=False,
                bargap=0.3,
            )
            fig2.update_traces(
                texttemplate='%{text:,}' if not show_sponsor_pct else '%{text}%',
                textposition='outside'
            )
        else:
            fig2 = px.pie(
                sponsor_counts,
                names="Sponsorship",
                values="Unique Students" if not show_sponsor_pct else "percentage",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            fig2.update_traces(
                textinfo="percent+label" if not show_sponsor_pct else "label+value",
                pull=[0.05]*len(sponsor_counts)
            )

        st.plotly_chart(fig2, use_container_width=True)

        # Add a table for more detail
        st.markdown("#### 📋 Sponsorship Breakdown Table")
        st.dataframe(sponsor_counts, use_container_width=True)

        # Download button for Chart 2 (using HTML export as fallback)
        try:
            img_html2 = pio.to_html(fig2, full_html=False, include_plotlyjs='cdn')
            st.download_button(
                "📥 Download Institution Sponsorship Chart (HTML)", 
                img_html2, 
                "institution_sponsorship.html", 
                "text/html"
            )
            st.info("PNG export requires 'kaleido', which may not work on Streamlit Cloud. Use the HTML download instead.")
        except Exception as e:
            st.warning("⚠️ Unable to export image. Please try downloading as HTML.")
    else:
        st.warning("⚠️ 'institution_sponsor_id' or 'number_student_id' column not found.")

    # ========== Chart 3: Student Count per Programme (Enhanced) ==========
    st.subheader("📚 Student Count per Programme")
    if uploaded_file is not None and "programme_name" in filtered_df.columns and "number_student_id" in filtered_df.columns:
        # Group by programme and department for richer context
        student_counts = (
            filtered_df.groupby(["department", "programme_name"])["number_student_id"]
            .nunique()
            .reset_index()
            .rename(columns={"number_student_id": "student_count"})
        )
        # Sort by department and then by student count descending
        student_counts = student_counts.sort_values(
            by=["department", "student_count"], ascending=[True, False]
        )

        # Optionally, allow user to select top N programmes to display per department
        max_top_n = min(50, student_counts.groupby("department")["programme_name"].count().max())
        top_n = st.slider(
            "Show Top N Programmes per Department (by unique student count)",
            min_value=3,
            max_value=max_top_n if max_top_n >= 3 else 3,
            value=min(20, max_top_n),
            step=1,
            key="top_n_programmes_per_dept"
        )
        top_programmes = (
            student_counts.groupby("department", group_keys=False)
            .apply(lambda x: x.nlargest(top_n, "student_count"))
            .reset_index(drop=True)
        )

        # Allow user to filter by department for clarity
        departments_available = sorted(top_programmes["department"].unique())
        selected_depts = st.multiselect(
            "Filter by Department (optional):",
            options=departments_available,
            default=departments_available,
            key="programme_dept_filter"
        )
        filtered_top_programmes = top_programmes[top_programmes["department"].isin(selected_depts)]

        fig3 = px.bar(
            filtered_top_programmes,
            x="programme_name",
            y="student_count",
            color="department",
            text="student_count",
            color_discrete_sequence=px.colors.qualitative.Set2,
            category_orders={"programme_name": filtered_top_programmes["programme_name"].tolist()},
        )
        fig3.update_layout(
            xaxis_title="Programme Name",
            yaxis_title="Number of Unique Students",
            showlegend=True,
            xaxis_tickangle=-45,
            margin=dict(b=150),
            height=600,
        )
        fig3.update_traces(texttemplate='%{text:,}', textposition='outside')
        st.plotly_chart(fig3, use_container_width=True)

        # Add a table for more detail
        st.markdown("#### 📋 Student Count per Programme Table")
        st.dataframe(filtered_top_programmes, use_container_width=True)

        # Download button for Chart 3 (HTML export)
        try:
            img_html3 = pio.to_html(fig3, full_html=False, include_plotlyjs='cdn')
            st.download_button(
                "📥 Download Student Count per Programme Chart (HTML)",
                img_html3,
                "student_count_per_programme.html",
                "text/html"
            )
            st.info("PNG export requires 'kaleido', which may not work on Streamlit Cloud. Use the HTML download instead.")
        except Exception as e:
            st.warning("⚠️ Unable to export image. Please try downloading as HTML.")
    else:
        st.warning("⚠️ Required columns for student count per programme are missing.")

    # ========== Chart 4: Application Trend ==========
    st.subheader("📈 Application Trend by Day")
    if 'filtered_df' in locals() and "application_day" in filtered_df.columns and not filtered_df["application_day"].isna().all():
        # Group by application_day and optionally by department for richer insights
        trend_group = st.radio(
            "Group Application Trend By:",
            options=["Overall", "Department"],
            horizontal=True,
            key="trend_group"
        )

        if trend_group == "Department" and "department" in filtered_df.columns:
            day_dept_counts = (
                filtered_df.groupby(["application_day", "department"])["number_student_id"]
                .nunique()
                .reset_index()
                .rename(columns={"number_student_id": "count"})
            )
            fig4 = px.line(
                day_dept_counts,
                x="application_day",
                y="count",
                color="department",
                markers=True,
                labels={"application_day": "Application Day", "count": "Number of Unique Applications", "department": "Department"},
                color_discrete_sequence=px.colors.qualitative.Set1,
            )
            fig4.update_layout(
                legend_title_text="Department",
                xaxis=dict(dtick=1),
                yaxis_title="Number of Unique Applications",
                xaxis_title="Application Day",
                hovermode="x unified"
            )
        else:
            day_counts = (
                filtered_df.groupby("application_day")["number_student_id"]
                .nunique()
                .reset_index()
                .rename(columns={"number_student_id": "count"})
            )
            fig4 = px.line(
                day_counts,
                x="application_day",
                y="count",
                markers=True,
                labels={"application_day": "Application Day", "count": "Number of Unique Applications"},
                color_discrete_sequence=["#636EFA"],
            )
            fig4.update_layout(
                xaxis=dict(dtick=1),
                yaxis_title="Number of Unique Applications",
                xaxis_title="Application Day",
                hovermode="x unified"
            )

        fig4.update_traces(line_width=3, marker=dict(size=8))
        st.plotly_chart(fig4, use_container_width=True)
        # Download button for Chart 4 (using HTML export as alternative)
        try:
            img_html4 = pio.to_html(fig4, full_html=False, include_plotlyjs='cdn')
            st.download_button(
                "📥 Download Application Trend Chart (HTML)",
                img_html4,
                "application_trend.html",
                "text/html"
            )
            st.info("PNG export requires 'kaleido', which may not work on Streamlit Cloud. Use the HTML download instead.")
        except Exception as e:
            st.warning("⚠️ Unable to export image. Please try downloading as HTML.")
    else:
        st.warning("⚠️ 'application_day' column not found or contains only missing values.")

    # ========== Application Day Filter & Animated Programme Demand Chart ==========

    # Application Day Filter (Sidebar)
    if "df" in locals() and "application_day" in df.columns and not df["application_day"].isna().all():
        st.sidebar.markdown("### ⏱️ Filter by Application Day")
        min_day = int(df["application_day"].min())
        max_day = int(df["application_day"].max())
        # Show histogram for quick visual reference
        st.sidebar.plotly_chart(
            px.histogram(
                df,
                x="application_day",
                nbins=(max_day - min_day + 1),
                title="Application Day Distribution",
                color_discrete_sequence=["#636EFA"]
            ).update_layout(
                xaxis_title="Application Day",
                yaxis_title="Count",
                height=200,
                margin=dict(l=0, r=0, t=30, b=0)
            ),
            use_container_width=True
        )
        selected_days = st.sidebar.slider(
            "Select Application Day Range",
            min_value=min_day,
            max_value=max_day,
            value=(min_day, max_day),
            step=1
        )
        # Apply day filter to filtered_df
        filtered_df = filtered_df[
            (filtered_df["application_day"] >= selected_days[0]) &
            (filtered_df["application_day"] <= selected_days[1])
        ]
        st.sidebar.info(f"Showing applications from Day {selected_days[0]} to Day {selected_days[1]}")

        # ========== Enhanced Animated Chart: Programme Demand by Application Day ==========
        st.subheader("📊 Programme Demand by Application Day (Animated)")

        if (
            "programme_name" in filtered_df.columns
            and "number_student_id" in filtered_df.columns
            and "application_day" in filtered_df.columns
            and not filtered_df["application_day"].isna().all()
            and not filtered_df.empty
        ):
            st.markdown("**Tip:** Select fewer programmes in the sidebar for a clearer animation.")
            top_n_animated = st.slider(
                "Show Top N Programmes (by total student count, for animation)",
                min_value=3,
                max_value=min(30, filtered_df["programme_name"].nunique()),
                value=min(10, filtered_df["programme_name"].nunique()),
                help="Limits the number of programmes shown in the animation for clarity."
            )
            # Get top N programmes by total student count
            top_programmes_animated = (
                filtered_df.groupby("programme_name")["number_student_id"]
                .count()
                .sort_values(ascending=False)
                .head(top_n_animated)
                .index.tolist()
            )
            animated_df = filtered_df[filtered_df["programme_name"].isin(top_programmes_animated)]
            animated_df = (
                animated_df.groupby(["application_day", "programme_name"])["number_student_id"]
                .count()
                .reset_index()
                .rename(columns={"number_student_id": "student_count"})
            )
            # Ensure all days/programmes are present for smooth animation
            all_days = sorted(filtered_df["application_day"].dropna().unique())
            all_programmes = top_programmes_animated
            animated_df = animated_df.set_index(["application_day", "programme_name"]).reindex(
                pd.MultiIndex.from_product([all_days, all_programmes], names=["application_day", "programme_name"]),
                fill_value=0
            ).reset_index()

            fig_animated = px.bar(
                animated_df,
                x="programme_name",
                y="student_count",
                animation_frame="application_day",
                color="programme_name",
                range_y=[0, max(5, animated_df["student_count"].max() + 5)],
                labels={"programme_name": "Programme", "student_count": "Students", "application_day": "Application Day"},
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig_animated.update_layout(
                xaxis_title="Programme",
                yaxis_title="Student Count",
                showlegend=False,
                margin=dict(b=120),
                height=500,
            )
            fig_animated.update_xaxes(tickangle=-45, tickfont=dict(size=10))
            st.plotly_chart(fig_animated, use_container_width=True)

            # Download button for animated chart (HTML only)
            try:
                img_html_anim = pio.to_html(fig_animated, full_html=False, include_plotlyjs='cdn')
                st.download_button(
                    "📥 Download Animated Programme Demand Chart (HTML)",
                    img_html_anim,
                    "animated_programme_demand.html",
                    "text/html"
                )
                st.info("Animation export is only available as HTML. Open in a browser for playback.")
            except Exception as e:
                st.warning("⚠️ Unable to export animated chart. Please try downloading as HTML.")
        else:
            st.warning("⚠️ Required columns for animation are missing or no valid application day data.")
    else:
        st.sidebar.warning("No valid 'application_day' data available for filtering.")
        
        # ========== 📌 Enhanced Dynamic Summary KPIs ==========
        st.subheader("📌 Enhanced Summary Insights (Filtered View)")

        # Helper function for safe mode calculation
        def safe_mode(series):
            try:
                mode_val = series.mode()
                return int(mode_val[0]) if len(mode_val) > 0 else None
            except Exception:
                return None

        # Helper for top N values with counts
        def top_n(series, n=3):
            vc = series.value_counts(dropna=True)
            return list(vc.head(n).items())

        if "filtered_df" in locals() and hasattr(filtered_df, "columns") and not filtered_df.empty:
            # Students
            total_students = filtered_df["number_student_id"].nunique() if "number_student_id" in filtered_df.columns else 0
            # Institutions
            total_institutions = filtered_df["institution_name"].nunique() if "institution_name" in filtered_df.columns else 0
            # Programmes
            total_programmes = filtered_df["programme_name"].nunique() if "programme_name" in filtered_df.columns else 0
            # Most Active Day(s)
            top_days = top_n(filtered_df["application_day"].dropna(), n=2) if "application_day" in filtered_df.columns else []
            top_day_str = ", ".join([f"Day {int(day)} ({count:,})" for day, count in top_days]) if top_days else "N/A"
            # Top Departments
            top_depts = top_n(filtered_df["department"].dropna(), n=2) if "department" in filtered_df.columns else []
            top_dept_str = ", ".join([f"{dept} ({count:,})" for dept, count in top_depts]) if top_depts else "N/A"
            # Top Programmes
            top_progs = top_n(filtered_df["programme_name"].dropna(), n=2) if "programme_name" in filtered_df.columns else []
            top_prog_str = ", ".join([f"{prog} ({count:,})" for prog, count in top_progs]) if top_progs else "N/A"
            # Top Institutions
            top_insts = top_n(filtered_df["institution_name"].dropna(), n=2) if "institution_name" in filtered_df.columns else []
            top_inst_str = ", ".join([f"{inst} ({count:,})" for inst, count in top_insts]) if top_insts else "N/A"
            # Avg students per programme
            if "programme_name" in filtered_df.columns and "number_student_id" in filtered_df.columns:
                avg_students_per_programme = filtered_df.groupby("programme_name")["number_student_id"].nunique().mean()
            else:
                avg_students_per_programme = 0
            # Application period
            if "application_day" in filtered_df.columns and not filtered_df["application_day"].isna().all():
                min_day = int(filtered_df["application_day"].min())
                max_day = int(filtered_df["application_day"].max())
                app_period = f"Day {min_day} - Day {max_day}"
            else:
                app_period = "N/A"
        else:
            total_students = 0
            total_institutions = 0
            total_programmes = 0
            top_day_str = "N/A"
            top_dept_str = "N/A"
            top_prog_str = "N/A"
            top_inst_str = "N/A"
            avg_students_per_programme = 0
            app_period = "N/A"

        # Display KPIs in a visually rich layout
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("🎓 Unique Students", f"{total_students:,}")
        kpi2.metric("🏫 Institutions", f"{total_institutions:,}")
        kpi3.metric("📚 Programmes", f"{total_programmes:,}")
        kpi4.metric("⏳ Application Period", app_period)

        kpi5, kpi6, kpi7 = st.columns(3)
        kpi5.metric("📅 Most Active Day(s)", top_day_str)
        kpi6.metric("🏆 Top Department(s)", top_dept_str)
        kpi7.metric("⭐ Top Institution(s)", top_inst_str)

        st.markdown("---")
        st.markdown(f"**Top Programmes:** {top_prog_str}")
        st.markdown(f"**Average Students per Programme:** {avg_students_per_programme:.2f}")

        # ===== ENHANCED SUMMARY TABLE =====
        st.subheader("📋 Summary Table of Filtered Data")

        # Defensive check: ensure filtered_df exists and is a DataFrame
        if 'filtered_df' in locals() and hasattr(filtered_df, "columns"):
            all_columns = filtered_df.columns.tolist()
            default_cols = [col for col in [
            "number_student_id", "institution_name", "programme_name", "department", "mean_grade_id", "application_day"
            ] if col in all_columns]
            selected_columns = st.multiselect(
            "Select columns to display in the summary table:",
            options=all_columns,
            default=default_cols if default_cols else all_columns
            )

            # Option to set number of rows to show
            max_rows = min(200, len(filtered_df))
            num_rows = st.slider(
            "Number of rows to display:",
            min_value=5,
            max_value=max_rows if max_rows > 5 else 5,
            value=min(50, max_rows),
            step=5
            )

            # Show summary stats above table
            st.markdown(f"**Total Rows (after filtering):** {len(filtered_df):,}")
            st.markdown(f"**Columns Displayed:** {', '.join(selected_columns)}")

            # Display the table
            if not filtered_df.empty and selected_columns:
                st.dataframe(filtered_df[selected_columns].head(num_rows), use_container_width=True)
            else:
                st.info("No data available to display in the summary table.")

            # Download button for summary table as CSV
            if not filtered_df.empty and selected_columns:
                csv_summary = filtered_df[selected_columns].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Download Summary Table as CSV",
                    data=csv_summary,
                    file_name="summary_table.csv",
                    mime="text/csv"
                )

            # ===== DOWNLOAD OPTION =====
            if not filtered_df.empty:
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Download Filtered Data as CSV",
                    data=csv,
                    file_name="filtered_kuccps_data.csv",
                    mime="text/csv"
                )
        else:
            st.info("No filtered data available to display in the summary table.")

    # ===== Additional Visualizations =====

    # Chart 5: Mean Grade Distribution (Enhanced)
    st.subheader("🎯 Mean Grade Distribution")
    if 'filtered_df' in locals() and "mean_grade_id" in filtered_df.columns and not filtered_df["mean_grade_id"].isna().all():
        chart_type = st.radio(
            "Select Chart Type for Mean Grade Distribution:",
            options=["Bar", "Pie"],
            horizontal=True,
            key="mean_grade_chart_type"
        )

        grade_counts = (
            filtered_df["mean_grade_id"]
            .value_counts(dropna=False)
            .sort_index()
            .reset_index()
            .rename(columns={"index": "mean_grade_id", "mean_grade_id": "count"})
        )

        show_percentage = st.checkbox("Show as Percentage", value=False, key="mean_grade_percentage")
        if show_percentage:
            total = grade_counts["count"].sum()
            grade_counts["percentage"] = (grade_counts["count"] / total * 100).round(2)

        if chart_type == "Bar":
            fig5 = px.bar(
                grade_counts,
                x="mean_grade_id",
                y="count" if not show_percentage else "percentage",
                text="count" if not show_percentage else "percentage",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig5.update_layout(
                xaxis_title="Mean Grade",
                yaxis_title="Number of Students" if not show_percentage else "Percentage (%)",
                showlegend=False
            )
            fig5.update_traces(
                texttemplate='%{text}' + ('' if not show_percentage else '%'),
                textposition='outside'
            )
            st.plotly_chart(fig5, use_container_width=True)
        else:
            fig5 = px.pie(
                grade_counts,
                names="mean_grade_id",
                values="count" if not show_percentage else "percentage",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Pastel
            )
            fig5.update_traces(
                textinfo="percent+label" if not show_percentage else "label+value",
                pull=[0.05]*len(grade_counts)
            )
            st.plotly_chart(fig5, use_container_width=True)

        st.markdown("#### 📋 Mean Grade Distribution Table")
        st.dataframe(grade_counts, use_container_width=True)
        try:
            img_html5 = pio.to_html(fig5, full_html=False, include_plotlyjs='cdn')
            st.download_button(
                "📥 Download Mean Grade Chart (HTML)",
                img_html5,
                "mean_grade_distribution.html",
                "text/html"
            )
            st.info("PNG export requires 'kaleido', which may not work on Streamlit Cloud. Use the HTML download instead.")
        except Exception as e:
            st.warning("⚠️ Unable to export image. Please try downloading as HTML.")
    else:
        st.warning("⚠️ 'mean_grade_id' column not found or contains only missing values.")

    # Chart 6: Applications by Placement Cycle (Enhanced)
    st.subheader("🔄 Applications by Placement Cycle")
    if "placement_cycle_id" in filtered_df.columns and not filtered_df["placement_cycle_id"].isna().all():
        chart6_type = st.radio(
            "Select Chart Type for Placement Cycle:",
            options=["Bar", "Pie"],
            horizontal=True,
            key="placement_cycle_chart_type"
        )

        cycle_counts = (
            filtered_df["placement_cycle_id"]
            .value_counts(dropna=False)
            .sort_index()
            .reset_index()
            .rename(columns={"index": "placement_cycle_id", "placement_cycle_id": "count"})
        )

        show_cycle_pct = st.checkbox("Show as Percentage (Placement Cycle)", value=False, key="placement_cycle_pct")
        if show_cycle_pct:
            total_cycle = cycle_counts["count"].sum()
            cycle_counts["percentage"] = (cycle_counts["count"] / total_cycle * 100).round(2)

        if chart6_type == "Bar":
            fig6 = px.bar(
                cycle_counts,
                x="placement_cycle_id",
                y="count" if not show_cycle_pct else "percentage",
                text="count" if not show_cycle_pct else "percentage",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig6.update_layout(
                xaxis_title="Placement Cycle",
                yaxis_title="Number of Applications" if not show_cycle_pct else "Percentage (%)",
                showlegend=False
            )
            fig6.update_traces(
                texttemplate='%{text}' + ('' if not show_cycle_pct else '%'),
                textposition='outside'
            )
            st.plotly_chart(fig6, use_container_width=True)
        else:
            fig6 = px.pie(
                cycle_counts,
                names="placement_cycle_id",
                values="count" if not show_cycle_pct else "percentage",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            fig6.update_traces(
                textinfo="percent+label" if not show_cycle_pct else "label+value",
                pull=[0.05]*len(cycle_counts)
            )
            st.plotly_chart(fig6, use_container_width=True)

        st.markdown("#### 📋 Placement Cycle Distribution Table")
        st.dataframe(cycle_counts, use_container_width=True)

        try:
            img_html6 = pio.to_html(fig6, full_html=False, include_plotlyjs='cdn')
            st.download_button(
                "📥 Download Placement Cycle Chart (HTML)",
                img_html6,
                "applications_by_placement_cycle.html",
                "text/html"
            )
            st.info("PNG export requires 'kaleido', which may not work on Streamlit Cloud. Use the HTML download instead.")
        except Exception as e:
            st.warning("⚠️ Unable to export image. Please try downloading as HTML.")
    else:
        st.warning("⚠️ 'placement_cycle_id' column not found or contains only missing values.")

    # Chart 7: Top Institutions by Student Count (Enhanced)
    st.subheader("🏆 Top Institutions by Student Count")
    if 'filtered_df' in locals() and "institution_name" in filtered_df.columns and "number_student_id" in filtered_df.columns and not filtered_df["institution_name"].isna().all():
        max_top_n = min(30, filtered_df["institution_name"].nunique())
        top_n_institutions = st.slider(
            "Show Top N Institutions (by student count)",
            min_value=3,
            max_value=max_top_n if max_top_n >= 3 else 3,
            value=min(10, max_top_n),
            step=1,
            key="top_n_institutions"
        )
        top_institutions = (
            filtered_df.groupby("institution_name")["number_student_id"]
            .nunique()
            .reset_index()
            .rename(columns={"number_student_id": "student_count"})
            .sort_values(by="student_count", ascending=False)
            .head(top_n_institutions)
        )
        show_dept_breakdown = st.checkbox("Show Department Breakdown", value=False, key="inst_dept_breakdown")
        if show_dept_breakdown and "department" in filtered_df.columns:
            inst_dept_counts = (
                filtered_df[filtered_df["institution_name"].isin(top_institutions["institution_name"])]
                .groupby(["institution_name", "department"])["number_student_id"]
                .nunique()
                .reset_index()
                .rename(columns={"number_student_id": "student_count"})
            )
            fig7 = px.bar(
                inst_dept_counts,
                x="institution_name",
                y="student_count",
                color="department",
                text="student_count",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig7.update_layout(
                xaxis_title="Institution Name",
                yaxis_title="Student Count",
                barmode="stack",
                legend_title_text="Department",
                xaxis_tickangle=-30,
                margin=dict(b=120),
                height=500,
            )
            fig7.update_traces(texttemplate='%{text:,}', textposition='outside')
        else:
            fig7 = px.bar(
                top_institutions,
                x="institution_name",
                y="student_count",
                color="institution_name",
                text="student_count",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig7.update_layout(
                xaxis_title="Institution Name",
                yaxis_title="Student Count",
                showlegend=False,
                xaxis_tickangle=-30,
                margin=dict(b=120),
                height=500,
            )
            fig7.update_traces(texttemplate='%{text:,}', textposition='outside')
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown("#### 📋 Top Institutions Table")
        st.dataframe(top_institutions, use_container_width=True)
        try:
            img_html7 = pio.to_html(fig7, full_html=False, include_plotlyjs='cdn')
            st.download_button(
                "📥 Download Top Institutions Chart (HTML)",
                img_html7,
                "top_institutions.html",
                "text/html"
            )
            st.info("PNG export requires 'kaleido', which may not work on Streamlit Cloud. Use the HTML download instead.")
        except Exception as e:
            st.warning("⚠️ Unable to export image. Please try downloading as HTML.")
    else:
        st.warning("⚠️ Required columns for institution chart are missing or contain only missing values.")

    # Chart 8: Application Stage Distribution (Enhanced)
    st.subheader("📝 Application Stage Distribution")
    if 'filtered_df' in locals() and "application_stage_id" in filtered_df.columns and not filtered_df["application_stage_id"].isna().all():
        chart8_type = st.radio(
            "Select Chart Type for Application Stage Distribution:",
            options=["Bar", "Pie"],
            horizontal=True,
            key="application_stage_chart_type"
        )

        stage_counts = (
            filtered_df["application_stage_id"]
            .value_counts(dropna=False)
            .sort_index()
            .reset_index()
            .rename(columns={"index": "application_stage_id", "application_stage_id": "count"})
        )

        show_stage_pct = st.checkbox("Show as Percentage (Application Stage)", value=False, key="application_stage_pct")
        if show_stage_pct:
            total_stage = stage_counts["count"].sum()
            stage_counts["percentage"] = (stage_counts["count"] / total_stage * 100).round(2)

        if chart8_type == "Bar":
            fig8 = px.bar(
                stage_counts,
                x="application_stage_id",
                y="count" if not show_stage_pct else "percentage",
                text="count" if not show_stage_pct else "percentage",
                color_discrete_sequence=px.colors.qualitative.G10
            )
            fig8.update_layout(
                xaxis_title="Application Stage",
                yaxis_title="Number of Applications" if not show_stage_pct else "Percentage (%)",
                showlegend=False
            )
            fig8.update_traces(
                texttemplate='%{text}' + ('' if not show_stage_pct else '%'),
                textposition='outside'
            )
            st.plotly_chart(fig8, use_container_width=True)
        else:
            fig8 = px.pie(
                stage_counts,
                names="application_stage_id",
                values="count" if not show_stage_pct else "percentage",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            fig8.update_traces(
                textinfo="percent+label" if not show_stage_pct else "label+value",
                pull=[0.05]*len(stage_counts)
            )
            st.plotly_chart(fig8, use_container_width=True)

        st.markdown("#### 📋 Application Stage Distribution Table")
        st.dataframe(stage_counts, use_container_width=True)

        try:
            img_html8 = pio.to_html(fig8, full_html=False, include_plotlyjs='cdn')
            st.download_button(
                "📥 Download Application Stage Chart (HTML)",
                img_html8,
                "application_stage_distribution.html",
                "text/html"
            )
            st.info("PNG export requires 'kaleido', which may not work on Streamlit Cloud. Use the HTML download instead.")
        except Exception as e:
            st.warning("⚠️ Unable to export image. Please try downloading as HTML.")
    else:
        st.warning("⚠️ 'application_stage_id' column not found or contains only missing values.")
        # ====== ABOUT SECTION (Enhanced & Improved) ======
        with st.expander("ℹ️ About this Dashboard", expanded=False):
            st.markdown("""
            ## **KUCCPS Interactive Dashboard**

            Welcome to the KUCCPS Interactive Dashboard!  
            This tool empowers supervisors, analysts, and stakeholders to explore and analyze KUCCPS application data with ease and flexibility.

            **🔑 Key Features:**
            - **Programme Popularity:** Instantly see which programmes and departments are most sought after.
            - **Institution Sponsorship:** Compare application volumes between public and private institutions.
            - **Application Trends:** Track how applications evolve over time, including animated daily breakdowns.
            - **Academic Profile:** Visualize mean grade distributions and identify top-performing applicant groups.
            - **Placement Cycle Analysis:** Understand application flows across different placement cycles.
            - **Top Institutions:** Discover which institutions attract the highest number of students.
            - **Application Stages:** Monitor applicant progress through various stages.
            - **Dynamic Filtering:** All insights update in real time as you adjust filters for sponsor, stage, programme, institution, grade, cycle, and day.
            - **Summary KPIs:** Quick-glance metrics for students, institutions, programmes, and peak activity days.
            - **Data Export:** Download filtered data and all visualizations for further analysis or reporting.

            **💡 Pro Tips:**
            - Use the sidebar filters to drill down into specific cohorts or trends.
            - Download any chart or table for use in presentations or reports.
            - Hover over charts for interactive tooltips and deeper insights.
            - Try the animated charts to visualize how demand changes over time.

            _This dashboard is designed to support data-driven decision making and uncover actionable insights from KUCCPS application data._
            """)

        # ====== HELP & USAGE GUIDE (Enhanced & Improved) ======
        with st.expander("❓ Help & Usage Guide", expanded=False):
            st.markdown("""
            ### 📚 **How to Use the Dashboard**

            1. **Upload Data:**  
               Upload your KUCCPS dataset (CSV or Excel) using the uploader at the top of the page.

            2. **Apply Filters:**  
               Use the sidebar to filter by:
               - **Institution Sponsor:** (e.g., Public, Private)
               - **Application Stage:** (e.g., Submitted, Verified)
               - **Programme Type:** (e.g., Degree, Diploma)
               - **Programme Name:** (Select specific programmes)
               - **Institution Name:** (Focus on one or more institutions)
               - **Mean Grade:** (Academic performance)
               - **Placement Cycle:** (Application cycle)
               - **Application Day:** (Analyze trends by day)

            3. **Explore Visualizations:**  
               The main area displays interactive charts, tables, and summary metrics that update automatically as you change filters.

            4. **Download Results:**  
               Use the download buttons below each chart or table to export data and visualizations for further analysis or reporting.

            **🛠️ Filter Descriptions:**
            - **Institution Sponsor:** Sponsoring body of the institution (e.g., public, private).
            - **Application Stage:** Stage of the application process.
            - **Programme Type:** Type of programme (degree, diploma, etc.).
            - **Programme Name:** Specific academic programme.
            - **Institution Name:** Name of the institution.
            - **Mean Grade:** Applicant's mean grade.
            - **Placement Cycle:** Placement cycle identifier.
            - **Application Day:** Day of application submission.

            **_Need more help?_**  
            - Hover over any chart for detailed tooltips.
            - Use the "Download" buttons to save filtered data or charts.
            - For best results, use recent versions of Chrome or Edge browsers.

            _If you encounter issues or have suggestions, please contact the dashboard administrator._
            """)

        if uploaded_file is None:
            st.info("Please upload a KUCCPS dataset to get started. The dashboard will unlock all features once your data is loaded.")
