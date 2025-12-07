import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================
# Page setup
# =========================
st.set_page_config(
    page_title="DS413 Air Pollution Visualization Dashboard",
    layout="wide"
)

st.title("DS413 Phase II – Air Pollution Visualization Dashboard")
st.markdown(
    "This interactive dashboard visualizes PM2.5 air pollution levels "
    "for cities and countries between 2017–2023."
)

# =========================
# Load and preprocess data
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("air_pollution new.csv")

    # Identify year columns
    year_cols = [c for c in df.columns if c.isdigit()]

    # Convert to numeric
    for col in year_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Replace 0 with NaN (treat missing or zero values as not available)
    df[year_cols] = df[year_cols].replace(0, np.nan)

    # Convert to long format for easier plotting
    df_long = df.melt(
        id_vars=["city", "country"],
        value_vars=year_cols,
        var_name="year",
        value_name="pm25"
    )
    df_long["year"] = df_long["year"].astype(int)

    return df, df_long, year_cols

df, df_long, year_cols = load_data()

# =========================
# Sidebar filters
# =========================
st.sidebar.header("Filters")

# Select year
selected_year = st.sidebar.selectbox(
    "Select year:",
    options=sorted(year_cols)
)

# Select country
countries = sorted(df["country"].unique())
selected_country = st.sidebar.selectbox(
    "Select country:",
    options=["All"] + countries
)

# ----------------------------------------------
# Select city depending on selected country
# The 'key' below forces Streamlit to reload the city widget whenever the country changes.
# Without this key, the dropdown may appear frozen and not update correctly.
# ----------------------------------------------
if selected_country == "All":
    city_options = sorted(df["city"].unique())
else:
    city_options = sorted(df[df["country"] == selected_country]["city"].unique())

selected_city = st.sidebar.selectbox(
    "Select city (optional):",
    options=["All"] + city_options,
    key=f"city_{selected_country}"  # dynamic key refreshes the list when country changes
)

# =========================
# Filtered data
# =========================
# Full filters (country + city) – used in Analysis + Raw Data
df_filtered = df.copy()
if selected_country != "All":
    df_filtered = df_filtered[df_filtered["country"] == selected_country]
if selected_city != "All":
    df_filtered = df_filtered[df_filtered["city"] == selected_city]

df_long_filtered = df_long.merge(
    df_filtered[["city", "country"]],
    on=["city", "country"],
    how="inner"
)

# Only country filter – used in Overview charts
df_country_filtered = df.copy()
if selected_country != "All":
    df_country_filtered = df_country_filtered[df_country_filtered["country"] == selected_country]

# =========================
# Tabs layout
# =========================
tab1, tab2, tab3 = st.tabs(["Overview", "Analysis", "Raw Data"])

# =========================
# Tab 1: Overview
# =========================
with tab1:
    st.subheader("Global Overview")

    # KPIs are based on all countries (global)
    country_mean_all_years = (
        df_long.groupby("country")["pm25"].mean().dropna().sort_values(ascending=False)
    )

    if not country_mean_all_years.empty:
        highest_country = country_mean_all_years.idxmax()
        highest_value = country_mean_all_years.max()
        lowest_country = country_mean_all_years.idxmin()
        lowest_value = country_mean_all_years.min()
        global_mean = country_mean_all_years.mean()
        num_countries = country_mean_all_years.index.nunique()
    else:
        highest_country = lowest_country = "N/A"
        highest_value = lowest_value = global_mean = 0.0
        num_countries = 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Highest average PM2.5 (country)", f"{highest_country}", f"{highest_value:.1f}")
    col2.metric("Lowest average PM2.5 (country)", f"{lowest_country}", f"{lowest_value:.1f}")
    col3.metric("Number of countries", f"{num_countries}")
    col4.metric("Global mean PM2.5", f"{global_mean:.1f}")

    # Global PM2.5 trend (2017–2023)
    global_trend = (
        df_long.groupby("year")["pm25"]
        .mean()
        .reset_index()
        .dropna()
    )
    st.markdown("#### Global PM2.5 trend (2017–2023)")
    if not global_trend.empty:
        fig_line = px.line(
            global_trend,
            x="year",
            y="pm25",
            markers=True,
            labels={"pm25": "PM2.5 (µg/m³)", "year": "Year"},
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No data available to display the global trend.")

    # Choropleth map – reacts to selected country (filters countries)
    st.markdown(f"#### Country-level PM2.5 in {selected_year}")
    country_year = (
        df_country_filtered.groupby("country")[selected_year]
        .mean()
        .reset_index()
        .rename(columns={selected_year: "pm25"})
        .dropna()
    )

    if not country_year.empty:
        fig_map = px.choropleth(
            country_year,
            locations="country",
            locationmode="country names",
            color="pm25",
            color_continuous_scale="Viridis",
            labels={"pm25": f"PM2.5 {selected_year} (µg/m³)"},
            title=f"Average PM2.5 by Country in {selected_year}",
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No country data available for the selected filters.")

    # Top 10 countries bar chart – also uses country filter
    st.markdown(f"#### Top 10 countries by PM2.5 in {selected_year}")
    top10 = country_year.sort_values("pm25", ascending=False).head(10)

    if not top10.empty:
        fig_bar = px.bar(
            top10,
            x="country",
            y="pm25",
            labels={"pm25": f"PM2.5 {selected_year} (µg/m³)", "country": "Country"},
        )
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No data available to display the top 10 countries.")

# =========================
# Tab 2: Analysis (4 plots side by side in 2×2 grid)
# =========================
with tab2:
    st.subheader("Detailed Analysis")

    colA, colB = st.columns(2)

    # 1) Violin plot: distribution by year
    with colA:
        st.markdown("##### PM2.5 distribution by year (filtered)")
        if not df_long_filtered.empty:
            fig_violin = px.violin(
                df_long_filtered,
                x="year",
                y="pm25",
                box=True,
                points="outliers",
                labels={"pm25": "PM2.5 (µg/m³)", "year": "Year"},
            )
            st.plotly_chart(fig_violin, use_container_width=True)
        else:
            st.info("No data available for the current filters.")

    # 2) Scatter plot: 2019 vs 2023
    with colB:
        st.markdown("##### Country PM2.5: 2019 vs 2023 (filtered by country)")
        if "2019" in year_cols and "2023" in year_cols:
            scatter_df = (
                df_country_filtered.groupby("country")[["2019", "2023"]]
                .mean()
                .reset_index()
                .dropna()
            )
            if not scatter_df.empty:
                fig_scatter = px.scatter(
                    scatter_df,
                    x="2019",
                    y="2023",
                    hover_name="country",
                    labels={"2019": "PM2.5 (2019)", "2023": "PM2.5 (2023)"},
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("No 2019/2023 data available for the current filters.")
        else:
            st.info("2019 and 2023 columns are not available in the dataset.")

    colC, colD = st.columns(2)

    # 3) Line chart: trend for selected country/city
    with colC:
        st.markdown("##### PM2.5 trend for selected filters")
        if not df_long_filtered.empty:
            trend_filtered = (
                df_long_filtered.groupby("year")["pm25"]
                .mean()
                .reset_index()
                .dropna()
            )
            fig_trend_f = px.line(
                trend_filtered,
                x="year",
                y="pm25",
                markers=True,
                labels={"pm25": "PM2.5 (µg/m³)", "year": "Year"},
            )
            st.plotly_chart(fig_trend_f, use_container_width=True)
        else:
            st.info("No data available to display the trend for the current filters.")

    # 4) Bar chart: city-level PM2.5 in selected year
    with colD:
        st.markdown(f"##### City-level PM2.5 in {selected_year}")
        city_year = (
            df_filtered[["city", "country", selected_year]]
            .rename(columns={selected_year: "pm25"})
            .dropna()
        )
        if not city_year.empty:
            fig_city_bar = px.bar(
                city_year,
                x="city",
                y="pm25",
                hover_data=["country"],
                labels={"pm25": f"PM2.5 {selected_year} (µg/m³)", "city": "City"},
            )
            fig_city_bar.update_layout(xaxis_tickangle=-60)
            st.plotly_chart(fig_city_bar, use_container_width=True)
        else:
            st.info("No city data available for the current filters.")

# =========================
# Tab 3: Raw Data
# =========================
with tab3:
    st.subheader("Raw Data (after applying filters)")

    st.markdown(
        f"- Year filter: **{selected_year}**  \n"
        f"- Country filter: **{selected_country}**  \n"
        f"- City filter: **{selected_city}**"
    )

    st.dataframe(df_filtered, use_container_width=True)

    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered data as CSV",
        data=csv,
        file_name="filtered_air_pollution_filtered.csv",
        mime="text/csv"
    )
