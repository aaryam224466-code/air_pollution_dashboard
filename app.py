import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------- Page configuration --------------------
st.set_page_config(
    page_title="DS413 Air Pollution Dashboard",
    layout="wide"
)

# -------------------- Header --------------------
st.markdown(
    """
    <h1 style="margin-bottom:0;">DS413 Phase II – Air Pollution Visualization Dashboard</h1>
    <p style="color: #555; font-size: 15px; margin-top:4px;">
    This interactive dashboard visualizes PM2.5 air pollution levels for cities and countries between 2017–2023.
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# -------------------- Load and prepare data --------------------
df = pd.read_csv("air_pollution new.csv")

# Year columns start from the 3rd column (index 2)
year_cols = df.columns[2:]

# Convert yearly columns to numeric
for col in year_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Clean country names
df["country"] = df["country"].astype(str).str.strip()

# Pre-compute overall country averages across 2017–2023
country_means_all = df.groupby("country")[year_cols].mean()
country_means_all["overall_mean"] = country_means_all.mean(axis=1)

highest_country = country_means_all["overall_mean"].idxmax()
highest_value = country_means_all["overall_mean"].max()

lowest_country = country_means_all["overall_mean"].idxmin()
lowest_value = country_means_all["overall_mean"].min()

overall_global_mean = df[year_cols].stack().mean()
total_cities = df["city"].nunique()

# -------------------- Sidebar filters --------------------
st.sidebar.title("Filters")

st.sidebar.markdown(
    "Use the filters below to explore air pollution patterns "
    "by year and country."
)

selected_year = st.sidebar.selectbox(
    "Select year:",
    options=list(year_cols)
)

countries = sorted(df["country"].unique())

selected_country = st.sidebar.selectbox(
    "Select country for detailed trend:",
    options=countries
)

show_data = st.sidebar.checkbox("Show raw data for selected year", value=False)

# -------------------- KPI section --------------------
kpi_container = st.container()
with kpi_container:
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

    col_kpi1.metric(
        label="Highest avg PM2.5 (2017–2023)",
        value=highest_country,
        delta=f"{highest_value:.1f}"
    )
    col_kpi2.metric(
        label="Lowest avg PM2.5 (2017–2023)",
        value=lowest_country,
        delta=f"{lowest_value:.1f}"
    )
    col_kpi3.metric(
        label="Number of cities with data",
        value=int(total_cities)
    )
    col_kpi4.metric(
        label="Overall global avg PM2.5 (2017–2023)",
        value=f"{overall_global_mean:.2f}"
    )

st.markdown("---")

# -------------------- First row: Map + Top 10 bar chart --------------------
row1 = st.container()
with row1:
    col1, col2 = st.columns(2)

    # Color theme for consistency
    color_theme = "Reds"

    # 1) Choropleth map
    with col1:
        st.subheader(f"Global Air Pollution Map – {selected_year}")

        avg_by_country = (
            df.groupby("country")[selected_year]
            .mean()
            .reset_index()
        )

        fig_map = px.choropleth(
            avg_by_country,
            locations="country",
            locationmode="country names",
            color=selected_year,
            color_continuous_scale=color_theme,
            title=f"Average PM2.5 by Country in {selected_year}",
            labels={selected_year: "PM2.5"}
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

    # 2) Top 10 bar chart
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
            labels={"country": "Country", selected_year: "PM2.5"},
            text_auto=".1f"
        )
        fig_bar.update_layout(
            xaxis_tickangle=-45,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# -------------------- Second row: Global trend + Country trend --------------------
row2 = st.container()
with row2:
    col3, col4 = st.columns(2)

    # 3) Global average trend
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
            labels={"PM2.5": "PM2.5"},
        )
        fig_global_line.update_traces(line=dict(width=3))
        fig_global_line.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_global_line, use_container_width=True)

    # 4) Country-specific trend
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

# -------------------- Optional raw data view --------------------
if show_data:
    st.subheader(f"Raw data for {selected_year}")
    st.dataframe(
        df[["city", "country", selected_year]]
        .dropna()
        .sort_values(by=selected_year, ascending=False)
        .reset_index(drop=True)
    )


