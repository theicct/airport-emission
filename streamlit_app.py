import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from PIL import Image

# Load logo
logo = Image.open("icct_logo.jpg")

# Display logo at the top of the sidebar
with st.sidebar:
    st.image(logo, use_container_width=True)
#   st.markdown("### Filter Airports")

# Set layout
st.set_page_config(layout="wide")

# Load data
df = pd.read_csv("Data_Explorer_Final_with_coordinates_500.csv")
df.columns = df.columns.str.strip()

# Sidebar Filters (default spacing)
st.sidebar.header("Filter Airports")

selected_countries = st.sidebar.multiselect(
    "Select Country", 
    options=sorted(df['Country'].dropna().unique())
)
filtered_df = df[df['Country'].isin(selected_countries)] if selected_countries else df

selected_airports = st.sidebar.multiselect(
    "Select Airport", 
    options=sorted(filtered_df['Airport Name'].dropna().unique())
)
filtered_df = filtered_df[filtered_df['Airport Name'].isin(selected_airports)] if selected_airports else filtered_df

selected_ops = st.sidebar.multiselect(
    "Select Operation Type", 
    options=sorted(filtered_df['Operation Type'].dropna().unique())
)
filtered_df = filtered_df[filtered_df['Operation Type'].isin(selected_ops)] if selected_ops else filtered_df

# Title
st.title("Global Airport Emissions Map")

# Map center logic
if not filtered_df.empty:
    center_lat = filtered_df['Airport Latitude'].mean()
    center_lon = filtered_df['Airport Longitude'].mean()
else:
    center_lat, center_lon = 20, 0

# Create Folium map
m = folium.Map(location=[center_lat, center_lon], zoom_start=2, min_zoom=2)

# Add markers
for _, row in filtered_df.iterrows():
    popup_text = (
        f"<b>Airport:</b> {row['Airport Name']}<br>"
        f"<b>ICAO:</b> {row['Airport ICAO Code']}<br>"
        f"<b>Country:</b> {row['Country']}<br>"
        f"<b>Flights:</b> {row['Flights']}<br>"
        f"<b>Fuel LTO Cycle (kg):</b> {row['Fuel LTO Cycle (kg)']:,.0f}<br>"
        f"<b>HC LTO (g):</b> {row['HC LTO Total mass (g)']:,.0f}<br>"
        f"<b>CO LTO (g):</b> {row['CO LTO Total Mass (g)']:,.0f}<br>"
        f"<b>NOx LTO (g):</b> {row['NOx LTO Total mass (g)']:,.0f}<br>"
        f"<b>PM2.5 (g):</b> {row['PM2.5 LTO Emission (g)']:,.0f}<br>"
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

st_folium(m, use_container_width=True, height=600)

# Summary
st.subheader("Summary of Filtered Results")

# Compute summary
summary = filtered_df[[
    'Flights',
    'Fuel LTO Cycle (kg)',
    'HC LTO Total mass (g)',
    'CO LTO Total Mass (g)',
    'NOx LTO Total mass (g)',
    'PM2.5 LTO Emission (g)'
]].sum()

summary.index = [
    'Total Flights',
    'Total LTO Fuel (kg)',
    'Total LTO HC pollution (g)',
    'Total LTO CO pollution (g)',
    'Total LTO NOx pollution (g)',
    'Total LTO PM2.5 pollution (g)'
]

# Add number of airports
summary_df = pd.DataFrame(summary).T
summary_df.insert(0, 'Number of Airports', filtered_df['Airport Name'].nunique())
summary_df = summary_df.astype(int)
summary_df.reset_index(drop=True, inplace=True)

# Display
st.dataframe(summary_df)