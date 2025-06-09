# CSH Dashboard app.py - Updated version with Tabs and User-Selectable Metrics and UI enhancements

import streamlit as st
import pandas as pd
from streamlit_echarts import st_pyecharts
from pyecharts.charts import Pie, Bar
from pyecharts import options as opts

st.set_page_config(page_title="CSH Stats", page_icon="assets/csh_logo.png", layout="wide")

# Simple manual login with st.session_state

# Define your users and passwords
USER_CREDENTIALS = {
    "jf.papel@gmail.com": {"password": "csh@2025", "name": "João Filipe Papel"},
    "alessandro.tonacci@cnr.it": {"password": "csh@2025", "name": "Alessandro Tonacci"},
    "lucia.billeci@cnr.it": {"password": "csh@2025", "name": "Lucia Billeci"},
}

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "full_name" not in st.session_state:
    st.session_state.full_name = ""


# Login form
if not st.session_state.logged_in:
    st.title("Login to CSH Dashboard")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.full_name = USER_CREDENTIALS[username]["name"]
            st.rerun()
        else:
            st.error("Invalid username or password.")
    st.stop()

# After login — continue app
st.sidebar.success(f"Logged in as {st.session_state.full_name}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.full_name = ""
    st.rerun()

# Load cleaned CSV dataset
csv_path = "data/csh_member_data.csv"
df = pd.read_csv(csv_path)

# Pre-process dates (extract year)
df["Admission Year"] = pd.to_datetime(df["Admission Date"], format="%d/%m/%Y", errors="coerce").dt.year

# Sidebar layout
st.sidebar.title("\U0001F50D Filters")

# 1. Demographics
st.sidebar.subheader("1. Demographics")

# 1.1 Continent filter
continents = sorted(df["Continent"].dropna().unique())
continent_filter = st.sidebar.multiselect("1.1 Select Continent(s):", continents)

# 1.2 Region filter based on Continent
if continent_filter:
    region_options = df[df["Continent"].isin(continent_filter)]["Region"].dropna().unique()
else:
    region_options = df["Region"].dropna().unique()
region_filter = st.sidebar.multiselect("1.2 Select Region(s):", sorted(region_options))

# 1.3 Country filter based on Region
if region_filter:
    country_options = df[df["Region"].isin(region_filter)]["Country"].dropna().unique()
elif continent_filter:
    country_options = df[df["Continent"].isin(continent_filter)]["Country"].dropna().unique()
else:
    country_options = df["Country"].dropna().unique()
country_filter = st.sidebar.multiselect("1.3 Select Country(ies):", sorted(country_options))

# 2. Filters (Checkboxes with AND logic)
st.sidebar.subheader("2. Filters")

admission_year_options = sorted(df["Admission Year"].dropna().unique())
admission_year_filter = st.sidebar.multiselect("Admission Date:", admission_year_options)

academic_level_options = sorted(df["Academic Degree"].dropna().unique())
academic_level_filter = st.sidebar.multiselect("Academic Level:", academic_level_options)

gender_options = sorted(df["Gender"].dropna().unique())
gender_filter = st.sidebar.multiselect("Gender:", gender_options)

status_options = sorted(df["Status"].dropna().unique())
status_filter = st.sidebar.multiselect("Status:", status_options)

membership_options = sorted(df["Membership Status"].dropna().unique())
membership_filter = st.sidebar.multiselect("Membership:", membership_options)

# Apply filters (AND logic)
filtered_df = df.copy()

if continent_filter:
    filtered_df = filtered_df[filtered_df["Continent"].isin(continent_filter)]
if region_filter:
    filtered_df = filtered_df[filtered_df["Region"].isin(region_filter)]
if country_filter:
    filtered_df = filtered_df[filtered_df["Country"].isin(country_filter)]
if admission_year_filter:
    filtered_df = filtered_df[filtered_df["Admission Year"].isin(admission_year_filter)]
if academic_level_filter:
    filtered_df = filtered_df[filtered_df["Academic Degree"].isin(academic_level_filter)]
if gender_filter:
    filtered_df = filtered_df[filtered_df["Gender"].isin(gender_filter)]
if status_filter:
    filtered_df = filtered_df[filtered_df["Status"].isin(status_filter)]
if membership_filter:
    filtered_df = filtered_df[filtered_df["Membership Status"].isin(membership_filter)]

# Main Tabs
tab1, tab2 = st.tabs(["\U0001F4CA Statistics", "\U0001F4C8 Metrics"])

with tab1:
    st.header("Statistics")

    # User selects dimension for chart
    dim_col = st.radio(
        "Select Member Attribute to Visualize:",
        ["Continent", "Region", "Country", "Academic Degree", "Gender", "Status", "Membership Status", "Admission Year"],
        horizontal=True
    )

    # Prepare data
    value_counts = filtered_df[dim_col].value_counts().reset_index()
    value_counts.columns = ["Response", "Count"]
    value_counts["Percentage"] = (value_counts["Count"] / value_counts["Count"].sum() * 100).round(1)

    # Visualization type
    col1, col2, col3 = st.columns(3)

    with col1:
        chart_type = st.radio("Chart Type:", ["Bar", "Circular"])

    with col2:
        pie_shape = st.radio(
            "Shape:",
            ["Pie", "Donut"],
            disabled=(chart_type != "Circular")
        )

    with col3:
        value_display = st.radio(
            "Show Values As:",
            ["Count", "Percentage"],
            disabled=(chart_type != "Circular")
        )

    # Render charts
    if chart_type == "Bar":
        b = (
            Bar()
            .add_xaxis(value_counts["Response"].tolist())
            .add_yaxis("Members", value_counts["Count"].tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title=""),
                toolbox_opts=opts.ToolboxOpts(
                    is_show=True,
                    feature={
                        "magicType": {"show": True, "type": ["line", "bar"]}
                    },
                    orient="vertical",
                    pos_left="left",
                    pos_top="top"
                ),
            )
        )
        st_pyecharts(b, key="echarts-bar")

    elif chart_type == "Circular":
        if value_display == "Count":
            pie_data = [list(z) for z in zip(value_counts["Response"], value_counts["Count"])]
            label_fmt = "{b}: {c}"
        else:
            pie_data = [list(z) for z in zip(value_counts["Response"], value_counts["Percentage"])]
            label_fmt = "{b}: {c}%"

        radius_setting = ["40%", "70%"] if pie_shape == "Donut" else ["0%", "70%"]

        c = (
            Pie()
            .add("", pie_data, radius=radius_setting)
            .set_global_opts(
                title_opts=opts.TitleOpts(title=""),
                legend_opts=opts.LegendOpts(orient="horizontal", pos_top="top"),
                toolbox_opts=opts.ToolboxOpts(
                    is_show=True,
                    feature={"saveAsImage": {"show": True, "title": "Download Image", "type": "svg", "name": dim_col}}
                )
            )
            .set_series_opts(label_opts=opts.LabelOpts(formatter=label_fmt))
        )
        st_pyecharts(c, height=500)

    # Optional: Show filtered table
    with st.expander("⚠️ Filtered Data Table For Verification Purposes"):
        st.dataframe(filtered_df)

with tab2:
    st.header("Metrics")

    # User selects Start Year, End Year, Metric
    col1, col2 = st.columns(2)

    with col1:
        start_year = st.selectbox("Start Year:", sorted(df["Admission Year"].dropna().unique()))

    with col2:
        end_year = st.selectbox("End Year:", sorted(df["Admission Year"].dropna().unique()))

    metric_field = st.radio(
    "Metric Field:",[ "All Members", "Doctoral (PhDs)", "Female Members", "Male Members", "Students", "Researchers", "Professors", "Paid Members"], horizontal=True)

    # Calculate growth based on selected metric
    def calculate_growth(start_year, end_year, condition=None):
        df_start = df[df["Admission Year"] == start_year]
        df_end = df[df["Admission Year"] == end_year]

        if condition:
            df_start = df_start[condition(df_start)]
            df_end = df_end[condition(df_end)]

        count_start = df_start.shape[0]
        count_end = df_end.shape[0]
        growth_count = count_end - count_start
        growth_percent = (growth_count / count_start * 100) if count_start > 0 else 100.0

        return count_start, count_end, growth_count, growth_percent

    # Define condition function
    metric_conditions = {
        "Doctoral (PhDs)": lambda d: d["Academic Degree"] == "Doctoral",
        "Female Members": lambda d: d["Gender"] == "Female",
        "Male Members": lambda d: d["Gender"] == "Male",
        "Students": lambda d: d["Status"] == "Student",
        "Researchers": lambda d: d["Status"] == "Researcher",
        "Professors": lambda d: d["Status"] == "Professor",
        "Paid Members": lambda d: d["Membership Status"] == "Paid",
    }

    condition = metric_conditions.get(metric_field, None)

    # Show result
    start, end, diff, perc = calculate_growth(start_year, end_year, condition)
    st.metric(f"{metric_field} Growth {start_year} to {end_year}", f"{end} members", f"{diff} ({perc:.1f}%)")
