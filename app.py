import streamlit as st
import pandas as pd
import plotly.express as px

# Page setup
st.set_page_config(
    page_title="DS413 Air Pollution Dashboard",
    layout="wide"
)

st.title("DS413 Phase II – Air Pollution Visualization Dashboard")
st.markdown(
    "This interactive dashboard visualizes PM2.5 air pollution levels "
    "for cities and countries between 2017–2023."
)

# Load dataset
df = pd.read_csv("air_pollution new.csv")

# Convert yearly columns to numeric
year_cols = df.columns[2:]
for col in year_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Sidebar filters (Year and Country)
st.sidebar.header("Filters")

selected_year = st.sidebar.selectbox(
    "Select year:",
    options=list(year_cols)
)

countries = sorted(df["country"].unique())
selected_country = st.sidebar.selectbox(
    "Select country (for detailed trend):",
    options=countries
)

# KPI section – quick summary metrics
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

global_mean = df[selected_year].mean()
max_country_row = df.groupby("country")[selected_year].mean().idxmax()
max_country_value = df.groupby("country")[selected_year].mean().max()
num_cities = df[df[selected_year].notna()]["city"].nunique()

col_kpi1.metric(
    label=f"Global average PM2.5 in {selected_year}",
    value=f"{global_mean:.2f}"
)
col_kpi2.metric(
    label=f"Most polluted country in {selected_year}",
    value=max_country_row,
    delta=f"{max_country_value:.1f}"
)
col_kpi3.metric(
    label="Number of cities with data",
    value=int(num_cities)
)

st.markdown("---")

# =========================
# First row: Map + Top 10
# =========================
row1 = st.container()
with row1:
    col1, col2 = st.columns(2)

    # Pre-compute average by country for the selected year
    avg_by_country = (
        df.groupby("country")[selected_year]
        .mean()
        .reset_index()
    )

    # 1) Choropleth Map – Global overview
    with col1:
        st.subheader(f"Global Air Pollution Map – {selected_year}")

        fig_map = px.choropleth(
            avg_by_country,
            locations="country",
            locationmode="country names",
            color=selected_year,
            color_continuous_scale="Reds",
            title=f"Average PM2.5 by Country in {selected_year}",
            labels={selected_year: "PM2.5"}
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

    # 2) Bar Chart – Top 10 most polluted countries
    with col2:
        st.subheader(f"Top 10 Most Polluted Countries in {selected_year}")

        top10 = avg_by_country.nlargest(10, selected_year)

        fig_bar = px.bar(
            top10,
            x="country",
            y=selected_year,
            title=f"Top 10 Countries with Highest PM2.5 in {selected_year}",
            labels={"country": "Country", selected_year: "PM2.5"},
            text_auto=".1f"
        )
        fig_bar.update_layout(
            xaxis_tickangle=-45,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# =========================
# Second row: Global trend + Country trend
# =========================
row2 = st.container()
with row2:
    col3, col4 = st.columns(2)

    # 3) Line Chart – Global average trend (2017–2023)
    with col3:
        st.subheader("Global Average PM2.5 Trend (2017–2023)")

        global_trend = df[year_cols].mean().reset_index()
        global_trend.columns = ["Year", "PM2.5"]

        fig_global_line = px.line(
            global_trend,
            x="Year",
            y="PM2.5",
            markers=True,
            title="Global Average PM2.5 Over Time",
            labels={"PM2.5": "PM2.5"}
        )
        fig_global_line.update_traces(line=dict(width=3))
        fig_global_line.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_global_line, use_container_width=True)

    # 4) Line Chart – Country-specific trend
    with col4:
        st.subheader(f"PM2.5 Trend for {selected_country} (2017–2023)")

        country_trend = (
            df[df["country"] == selected_country][year_cols]
            .mean()
            .reset_index()
        )
        country_trend.columns = ["Year", "PM2.5"]

        fig_country_line = px.line(
            country_trend,
            x="Year",
            y="PM2.5",
            markers=True,
            title=f"PM2.5 Trend in {selected_country}",
            labels={"PM2.5": "PM2.5"}
        )
        fig_country_line.update_traces(line=dict(width=3))
        fig_country_line.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_country_line, use_container_width=True)

st.markdown("---")

# Insights section
st.markdown("### Insights")
st.markdown(
    "- Use the year filter to see how the map and top countries change over time.\n"
    "- The global trend plot summarizes overall changes in air pollution from 2017–2023.\n"
    "- The country trend helps you focus on one country’s pattern in detail."
)
