import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

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

# Clean country names
df["country"] = df["country"].astype(str).str.strip()

# Convert yearly columns to numeric and treat 0 as missing
year_cols = df.columns[2:]
for col in year_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    # In this dataset, 0 means no measurement, so we convert it to NaN
    df.loc[df[col] == 0, col] = np.nan

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

# ======================
# KPI section – summary
# ======================
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

# Global average in selected year
global_mean = df[selected_year].mean()

# Average for selected country in selected year
selected_country_values = df[df["country"] == selected_country][selected_year]
selected_country_mean = selected_country_values.mean()

# Number of cities with data in selected year
num_cities = df[df[selected_year].notna()]["city"].nunique()

# Format value for selected country
if pd.isna(selected_country_mean):
    country_metric_value = "No data"
else:
    country_metric_value = f"{selected_country_mean:.2f}"

col_kpi1.metric(
    label=f"Global average PM2.5 in {selected_year}",
    value=f"{global_mean:.2f}"
)
col_kpi2.metric(
    label=f"Average PM2.5 in {selected_country} ({selected_year})",
    value=country_metric_value
)
col_kpi3.metric(
    label="Number of cities with data",
    value=int(num_cities)
)

st.markdown("---")

# ================
# First row: Map + Top 10
# ================
color_theme = "Reds"
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Global Air Pollution Map – {selected_year}")
    avg_by_country = df.groupby("country")[selected_year].mean().reset_index()
    fig_map = px.choropleth(
        avg_by_country,
        locations="country",
        locationmode="country names",
        color=selected_year,
        color_continuous_scale=color_theme,
        title=f"Average PM2.5 by Country in {selected_year}",
        labels={selected_year: "PM2.5"}
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col2:
    st.subheader(f"Top 10 Most Polluted Countries in {selected_year}")
    top10 = avg_by_country.nlargest(10, selected_year)
    fig_bar = px.bar(
        top10,
        x="country",
        y=selected_year,
        color=selected_year,
        color_continuous_scale=color_theme,
        title=f"Top 10 Countries with Highest PM2.5 in {selected_year}",
        text_auto=".1f"
    )
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ==========================
# Second row: Global + Country trends
# ==========================
col3, col4 = st.columns(2)

with col3:
    st.subheader("Global Average PM2.5 Trend (2017–2023)")
    global_trend = df[year_cols].mean().reset_index()
    global_trend.columns = ["Year", "PM2.5"]
    fig_global_line = px.line(
        global_trend,
        x="Year",
        y="PM2.5",
        markers=True,
        color_discrete_sequence=["#e74c3c"],
        title="Global Average PM2.5 Over Time"
    )
    st.plotly_chart(fig_global_line, use_container_width=True)

with col4:
    st.subheader(f"PM2.5 Trend for {selected_country} (2017–2023)")
    country_trend = df[df["country"] == selected_country][year_cols].mean().reset_index()
    country_trend.columns = ["Year", "PM2.5"]
    fig_country_line = px.line(
        country_trend,
        x="Year",
        y="PM2.5",
        markers=True,
        color_discrete_sequence=["#2980b9"],
        title=f"PM2.5 Trend in {selected_country}"
    )
    st.plotly_chart(fig_country_line, use_container_width=True)
