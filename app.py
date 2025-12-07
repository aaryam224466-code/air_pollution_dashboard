# Divider
st.markdown("---")

# Define custom color template
color_theme = "Reds"  # يمكنك تغييره إلى "Blues" أو "Viridis"

# Create two columns for the first row (Map + Bar)
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

# Divider
st.markdown("---")

# Second row (Global Trend + Country Trend)
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
