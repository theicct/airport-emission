import streamlit as st
import pandas as pd
import folium
#from streamlit_folium import st_folium

# Load your data
df = pd.read_csv("Data_Explorer_Final_with_coordinates.csv")  # Replace with your actual file path
df.columns = df.columns.str.strip()  # Clean column names

# Sidebar filters
st.sidebar.header("Filter Airports")

# Multiselect for country
selected_countries = st.sidebar.multiselect(
    "Select Country", 
    options=sorted(df['Country'].dropna().unique()), 
    default=sorted(df['Country'].dropna().unique())
)
filtered_df = df[df['Country'].isin(selected_countries)]

# Multiselect for airport name (filtered by selected countries)
selected_airports = st.sidebar.multiselect(
    "Select Airport", 
    options=sorted(filtered_df['Airport Name'].dropna().unique()), 
    default=sorted(filtered_df['Airport Name'].dropna().unique())
)
filtered_df = filtered_df[filtered_df['Airport Name'].isin(selected_airports)]

# Multiselect for operation type (filtered by selected airports)
selected_ops = st.sidebar.multiselect(
    "Select Operation Type", 
    options=sorted(filtered_df['Operation Type'].dropna().unique()), 
    default=sorted(filtered_df['Operation Type'].dropna().unique())
)
filtered_df = filtered_df[filtered_df['Operation Type'].isin(selected_ops)]

# Create map (centered around filtered data)
st.title("Global Airport Emissions Map")
if not filtered_df.empty:
    center_lat = filtered_df['Airport Latitude'].mean()
    center_lon = filtered_df['Airport Longitude'].mean()
else:
    center_lat, center_lon = 20, 0

m = folium.Map(location=[center_lat, center_lon], zoom_start=2)

# Add markers
for _, row in filtered_df.iterrows():
    popup_text = (
        f"<b>Airport:</b> {row['Airport Name']}<br>"
        f"<b>ICAO:</b> {row['Airport ICAO Code']}<br>"
        f"<b>Country:</b> {row['Country']}<br>"
        f"<b>Flights:</b> {row['Flights']}<br>"
        f"<b>Fuel LTO Cycle (kg):</b> {row['Fuel LTO Cycle (kg)']:,.2f}<br>"
        f"<b>HC LTO (g):</b> {row['HC LTO Total mass (g)']:,.2f}<br>"
        f"<b>CO LTO (g):</b> {row['CO LTO Total Mass (g)']:,.2f}<br>"
        f"<b>NOx LTO (g):</b> {row['NOx LTO Total mass (g)']:,.2f}<br>"
        f"<b>PM2.5 (g):</b> {row['PM2.5 LTO Emission (g)']:,.2f}<br>"
        f"<b>Operation Type:</b> {row['Operation Type']}"
    )
    folium.CircleMarker(
        location=[row['Airport Latitude'], row['Airport Longitude']],
        radius=6,
        color='blue',
        fill=True,
        fill_opacity=0.7,
        popup=folium.Popup(popup_text, max_width=300)
    ).add_to(m)

# Render map full width
st_data = st_folium(m, use_container_width=True, height=600)

# Summary section
st.subheader("Summary of Filtered Results")

summary = filtered_df[[
    'Flights',
    'Fuel LTO Cycle (kg)',
    'HC LTO Total mass (g)',
    'CO LTO Total Mass (g)',
    'NOx LTO Total mass (g)',
    'PM2.5 LTO Emission (g)'
]].sum().rename({
    'Fuel LTO Cycle (kg)': 'Fuel (kg)',
    'HC LTO Total mass (g)': 'HC (g)',
    'CO LTO Total Mass (g)': 'CO (g)',
    'NOx LTO Total mass (g)': 'NOx (g)',
    'PM2.5 LTO Emission (mg)': 'PM2.5 (g)'
})

st.dataframe(summary.to_frame(name="Total").style.format("{:,.2f}"))