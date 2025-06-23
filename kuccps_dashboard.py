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
    st.subheader("🧭 Programme Department Breakdown")
    if "department" in filtered_df.columns:
        dept_counts = filtered_df["department"].value_counts().reset_index()
        dept_counts.columns = ["department", "count"]

        fig1 = px.pie(
            dept_counts,
            names="department",
            values="count",
            hole=0.5,
            color_discrete_sequence=px.colors.sequential.RdBu,
        )
        fig1.update_traces(textinfo="percent+label")
        st.plotly_chart(fig1, use_container_width=True)

        # Download button for Chart 1 (using HTML export as fallback)
        try:
            img_html1 = pio.to_html(fig1, full_html=False, include_plotlyjs='cdn')
            st.download_button(
                "📥 Download Programme Breakdown (HTML)", 
                img_html1, 
                "programme_pie.html", 
                "text/html"
            )
            st.info("PNG export requires 'kaleido', which may not work on Streamlit Cloud. Use the HTML download instead.")
        except Exception as e:
            st.warning("⚠️ Unable to export image. Please try downloading as HTML.")

    # ========== Chart 2: Public vs Private ==========
    st.subheader("🏫 Institution Sponsorship Summary")
    if "institution_sponsor_id" in filtered_df.columns:
        sponsor_counts = (
            filtered_df.groupby("institution_sponsor_id")["number_student_id"]
            .nunique()
            .reset_index()
            .rename(columns={"institution_sponsor_id": "Sponsorship", "number_student_id": "Unique Students"})
            .sort_values(by="Unique Students", ascending=False)
        )

        fig2 = px.bar(
            sponsor_counts,
            x="Sponsorship",
            y="Unique Students",
            color="Sponsorship",
            text="Unique Students",
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        fig2.update_layout(
            xaxis_title="Institution Sponsor",
            yaxis_title="Number of Unique Students",
            showlegend=False,
            bargap=0.3,
        )
        fig2.update_traces(texttemplate='%{text:,}', textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)

        # Add a table for more detail
        st.markdown("#### 📋 Sponsorship Breakdown Table")
        st.dataframe(sponsor_counts, use_container_width=True)
    else:
        st.warning("⚠️ 'institution_sponsor_id' column not found.")
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

    # ========== Chart 3: Student Count per Programme ==========
    st.subheader("📚 Student Count per Programme")
    if "programme_name" in filtered_df.columns and "number_student_id" in filtered_df.columns:
        # Group by programme and department for richer context
        student_counts = (
            filtered_df.groupby(["department", "programme_name"])["number_student_id"]
            .count()
            .reset_index()
            .rename(columns={"number_student_id": "student_count"})
        )
        # Sort by department and then by student count descending
        student_counts = student_counts.sort_values(
            by=["department", "student_count"], ascending=[True, False]
        )

        # Optionally, allow user to select top N programmes to display
        top_n = st.slider("Show Top N Programmes (by student count)", 5, 50, 20)
        top_programmes = (
            student_counts.groupby("department")
            .head(top_n)
            .reset_index(drop=True)
        )

        fig3 = px.bar(
            top_programmes,
            x="programme_name",
            y="student_count",
            color="department",
            text="student_count",
            color_discrete_sequence=px.colors.qualitative.Set2,
            category_orders={"programme_name": top_programmes["programme_name"].tolist()},
        )
        fig3.update_layout(
            xaxis_title="Programme Name",
            yaxis_title="Number of Students",
            showlegend=True,
            xaxis_tickangle=-45,
            margin=dict(b=150),
            height=600,
        )
        fig3.update_traces(texttemplate='%{text:,}', textposition='outside')
        st.plotly_chart(fig3, use_container_width=True)

        # Add a table for more detail
        st.markdown("#### 📋 Student Count per Programme Table")
        st.dataframe(top_programmes, use_container_width=True)
    else:
        st.warning("⚠️ Required columns for student count per programme are missing.")
        # Download button for Chart 3 (HTML export as alternative to 'kaleido')
        try:
            img_html3 = pio.to_html(fig3, full_html=False, include_plotlyjs='cdn')
            st.download_button(
            "📥 Download Student Count Chart (HTML)",
            img_html3,
            "student_count_per_programme.html",
            "text/html"
            )
            st.info("PNG export requires 'kaleido', which may not work on Streamlit Cloud. Use the HTML download instead.")
        except Exception as e:
            st.warning("⚠️ Unable to export image. Please try downloading as HTML.")
        st.warning("⚠️ Required columns missing.")

    # ========== Chart 4: Application Trend ==========
    st.subheader("📈 Application Trend by Day")
    if "application_day" in filtered_df.columns:
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
                .count()
                .reset_index()
                .rename(columns={"number_student_id": "count"})
            )
            fig4 = px.line(
                day_dept_counts,
                x="application_day",
                y="count",
                color="department",
                markers=True,
                labels={"application_day": "Application Day", "count": "Number of Applications", "department": "Department"},
                color_discrete_sequence=px.colors.qualitative.Set1,
            )
            fig4.update_layout(
                legend_title_text="Department",
                xaxis=dict(dtick=1),
                yaxis_title="Number of Applications",
                xaxis_title="Application Day",
                hovermode="x unified"
            )
        else:
            day_counts = (
                filtered_df.groupby("application_day")["number_student_id"]
                .count()
                .reset_index()
                .rename(columns={"number_student_id": "count"})
            )
            fig4 = px.line(
                day_counts,
                x="application_day",
                y="count",
                markers=True,
                labels={"application_day": "Application Day", "count": "Number of Applications"},
                color_discrete_sequence=["#636EFA"],
            )
            fig4.update_layout(
                xaxis=dict(dtick=1),
                yaxis_title="Number of Applications",
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
        st.warning("⚠️ 'application_day' column not found.")

    # ========== Application Day Filter ==========
    if "application_day" in df.columns and not df["application_day"].isna().all():
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
    else:
        st.sidebar.warning("No valid 'application_day' data available for filtering.")
        # ========== Enhanced Animated Chart: Programme Demand by Application Day ==========
        st.subheader("📊 Programme Demand by Application Day (Animated)")

        if (
            "programme_name" in filtered_df.columns
            and "number_student_id" in filtered_df.columns
            and "application_day" in filtered_df.columns
            and not filtered_df["application_day"].isna().all()
        ):
            # Optionally, allow user to select top N programmes to animate
            st.markdown("**Tip:** Select fewer programmes in the sidebar for a clearer animation.")
            top_n_animated = st.slider(
                "Show Top N Programmes (by total student count, for animation)",
                min_value=3,
                max_value=30,
                value=10,
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

    # ========== 📌 Dynamic Summary KPIs (Enhanced) ==========
    st.subheader("📌 Summary Insights (Filtered View)")

    total_students = filtered_df["number_student_id"].nunique() if "number_student_id" in filtered_df.columns else 0
    total_institutions = filtered_df["institution_name"].nunique() if "institution_name" in filtered_df.columns else 0
    total_programmes = filtered_df["programme_name"].nunique() if "programme_name" in filtered_df.columns else 0
    top_day = (
        filtered_df["application_day"].mode()[0]
        if "application_day" in filtered_df.columns and not filtered_df["application_day"].isna().all()
        else "N/A"
    )
    top_department = (
        filtered_df["department"].value_counts().idxmax()
        if "department" in filtered_df.columns and not filtered_df["department"].isna().all() and not filtered_df.empty
        else "N/A"
    )
    avg_students_per_programme = (
        filtered_df.groupby("programme_name")["number_student_id"].nunique().mean()
        if "programme_name" in filtered_df.columns and "number_student_id" in filtered_df.columns and not filtered_df.empty
        else 0
    )
    top_institution = (
        filtered_df["institution_name"].value_counts().idxmax()
        if "institution_name" in filtered_df.columns and not filtered_df["institution_name"].isna().all() and not filtered_df.empty
        else "N/A"
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎓 Students", f"{total_students:,}")
    col2.metric("🏫 Institutions", f"{total_institutions:,}")
    col3.metric("📚 Programmes", f"{total_programmes:,}")
    col4.metric("📅 Most Active Day", f"Day {top_day}" if top_day != "N/A" else "N/A")

    col5, col6, col7 = st.columns(3)
    col5.metric("🏆 Top Department", f"{top_department}")
    col6.metric("📈 Avg Students/Programme", f"{avg_students_per_programme:.1f}")
    col7.metric("⭐ Top Institution", f"{top_institution}")

    # ===== ENHANCED SUMMARY TABLE =====
    st.subheader("📋 Summary Table of Filtered Data")

    # Option to select columns to display
    all_columns = filtered_df.columns.tolist()
    default_cols = [col for col in all_columns if col in [
        "number_student_id", "institution_name", "programme_name", "department", "mean_grade_id", "application_day"
    ]]
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
    st.dataframe(filtered_df[selected_columns].head(num_rows), use_container_width=True)

    # Download button for summary table as CSV
    csv_summary = filtered_df[selected_columns].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Summary Table as CSV",
        data=csv_summary,
        file_name="summary_table.csv",
        mime="text/csv"
    )

    # ===== DOWNLOAD OPTION =====
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_kuccps_data.csv",
        mime="text/csv"
    )

    # Additional Visualizations
    # Chart 5: Mean Grade Distribution (Enhanced)
    st.subheader("🎯 Mean Grade Distribution")
    if "mean_grade_id" in filtered_df.columns:
        # Allow user to choose chart type
        chart_type = st.radio(
            "Select Chart Type for Mean Grade Distribution:",
            options=["Bar", "Pie"],
            horizontal=True,
            key="mean_grade_chart_type"
        )

        grade_counts = (
            filtered_df["mean_grade_id"]
            .value_counts()
            .sort_index()
            .reset_index()
            .rename(columns={"index": "mean_grade_id", "mean_grade_id": "count"})
        )

        # Optionally, show as percentage
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

        # Show table of grade counts
        st.markdown("#### 📋 Mean Grade Distribution Table")
        st.dataframe(grade_counts, use_container_width=True)
        # Download button for Chart 5 (using HTML export as alternative to 'kaleido')
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
        st.warning("⚠️ 'mean_grade_id' column not found.")

    # Chart 6: Applications by Placement Cycle (Enhanced)
    st.subheader("🔄 Applications by Placement Cycle")
    if "placement_cycle_id" in filtered_df.columns:
        # Allow user to choose chart type
        chart6_type = st.radio(
            "Select Chart Type for Placement Cycle:",
            options=["Bar", "Pie"],
            horizontal=True,
            key="placement_cycle_chart_type"
        )

        cycle_counts = (
            filtered_df["placement_cycle_id"]
            .value_counts()
            .sort_index()
            .reset_index()
            .rename(columns={"index": "placement_cycle_id", "placement_cycle_id": "count"})
        )

        # Optionally, show as percentage
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

        # Show table of placement cycle counts
        st.markdown("#### 📋 Placement Cycle Distribution Table")
        st.dataframe(cycle_counts, use_container_width=True)

        # Download button for Chart 6 (using HTML export as alternative to 'kaleido')
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
        st.warning("⚠️ 'placement_cycle_id' column not found.")

    # Chart 7: Top 10 Institutions by Student Count (Enhanced)
    st.subheader("🏆 Top 10 Institutions by Student Count")
    if "institution_name" in filtered_df.columns and "number_student_id" in filtered_df.columns:
        # Optionally, allow user to select how many top institutions to show
        top_n_institutions = st.slider(
            "Show Top N Institutions (by student count)", 
            min_value=5, 
            max_value=30, 
            value=10, 
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
        # Optionally, show department breakdown for each institution
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
        # Show table for more detail
        st.markdown("#### 📋 Top Institutions Table")
        st.dataframe(top_institutions, use_container_width=True)
        # Download button for Chart 7 (using HTML export as alternative to 'kaleido')
        try:
            img_html7 = pio.to_html(fig7, full_html=False, include_plotlyjs='cdn')
            st.download_button(
            "📥 Download Top Institutions Chart (HTML)",
            img_html7,
            "top_10_institutions.html",
            "text/html"
            )
            st.info("PNG export requires 'kaleido', which may not work on Streamlit Cloud. Use the HTML download instead.")
        except Exception as e:
            st.warning("⚠️ Unable to export image. Please try downloading as HTML.")
    else:
        st.warning("⚠️ Required columns for institution chart are missing.")

    # Chart 8: Application Stage Distribution (Enhanced)
    st.subheader("📝 Application Stage Distribution")
    if "application_stage_id" in filtered_df.columns:
        # Allow user to choose chart type
        chart8_type = st.radio(
            "Select Chart Type for Application Stage Distribution:",
            options=["Bar", "Pie"],
            horizontal=True,
            key="application_stage_chart_type"
        )

        stage_counts = (
            filtered_df["application_stage_id"]
            .value_counts()
            .sort_index()
            .reset_index()
            .rename(columns={"index": "application_stage_id", "application_stage_id": "count"})
        )

        # Optionally, show as percentage
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

        # Show table of stage counts
        st.markdown("#### 📋 Application Stage Distribution Table")
        st.dataframe(stage_counts, use_container_width=True)

        # Download button for Chart 8 (using HTML export as alternative to 'kaleido')
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
        st.warning("⚠️ 'application_stage_id' column not found.")

# ====== ABOUT SECTION (Enhanced) ======
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

# ====== HELP & USAGE GUIDE (Enhanced) ======
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
st.info("Please upload a KUCCPS dataset to get started. The dashboard will unlock all features once your data is loaded.")
