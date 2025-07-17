import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from PIL import Image

# Load logo
logo = Image.open("logo/icct_logo.jpg")
spire_logo = Image.open("logo/LOGO_Spire_Aviation_Color_RGB.png") 
iba_logo = Image.open("logo/IBA Logo.png")      

# Display logo at the top of the sidebar
with st.sidebar:
    st.image(logo, use_container_width=True)
#   st.markdown("### Filter Airports")

# Set layout
st.set_page_config(layout="wide")

# Load data
df = pd.read_csv("Data_Explorer_Final_with_coordinates_500_example.csv")
df.columns = df.columns.str.strip()

# Sidebar Filters (default spacing)
st.sidebar.header("Filter Airports")

# Allow only one country selection
selected_country = st.sidebar.selectbox(
    "Select Country", 
    options=sorted(df['Country'].dropna().unique())
)
filtered_df = df[df['Country'] == selected_country]

# Allow multiple airports (still using multiselect)
selected_airports = st.sidebar.multiselect(
    "Select Airport", 
    options=sorted(filtered_df['Airport Name'].dropna().unique())
)
filtered_df = filtered_df[filtered_df['Airport Name'].isin(selected_airports)] if selected_airports else filtered_df

# Allow only one operation type
selected_op = st.sidebar.selectbox(
    "Select Operation Type", 
    options=sorted(filtered_df['Operation Type'].dropna().unique())
)
filtered_df = filtered_df[filtered_df['Operation Type'] == selected_op]


# Title
st.title("Top 500 Airports Based on Highest Number of Flights")
st.markdown(
    "This map displays the airports with the highest 500 flight counts with the greenhouse gas and pollution profile from aircraft landing and take off activity (LTO) . This serves as an example data from the International Council on Clean Transportation's Data Explorer. "
    "To request access to the full dataset, please click here: xxx"
)
# Map center logic
if not filtered_df.empty:
    center_lat = filtered_df['Airport Latitude'].mean()
    center_lon = filtered_df['Airport Longitude'].mean()
else:
    center_lat, center_lon = 20, 0

# Create Folium map
m = folium.Map(location=[center_lat, center_lon], zoom_start=2, min_zoom=2)

# Create and render map only if data exists
if not filtered_df.empty:
    center_lat = filtered_df['Airport Latitude'].mean()
    center_lon = filtered_df['Airport Longitude'].mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=2, min_zoom=2)

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

    st_folium(m, use_container_width=True, height=600, returned_objects=[])

else:
    st.warning("No data available for the selected filter. Please adjust your selection.")

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

# Format with commas
formatted_summary_df = summary_df.applymap(lambda x: f"{x:,}")

# Display the formatted DataFrame without the index
st.dataframe(formatted_summary_df, use_container_width=True, hide_index=True)

## Dispaly data partners
st.markdown("---")
st.header("Data Partners")

# Create columns for layout
col1, col2 = st.columns([1, 4])

with col1:
    st.image(spire_logo, width=150)

with col2:
    st.markdown("""
    **Spire Aviation** is the industry trustworthy source for global flight tracking data to power applications; drive decision making and improve cost efficiencies.  
    Spire’s 10+ satellites capture global aircraft movements using ADS-B signals, which combined with multi-terrestrial data sources provide enhanced global coverage, not just over inhabited regions, but also in remote locations and above the deep ocean.  

    From historical flight data, ADS-B tracking, to up-to-date data on weather impacting aviation operations, Spire’s versatile datasets help companies solve their business challenges and predict upcoming industry trends.  
    [Learn more](https://spire.com/aviation/)
    """)


col3, col4 = st.columns([1, 4])

with col3:
    st.image(iba_logo, width=150)

with col4:
    st.markdown("""
    **IBA** is a trusted provider of aviation intelligence and advisory services, supporting researchers and policy groups, investors, operators, and lessors with robust, data-driven insight.  
    Founded in 1988, IBA delivers comprehensive fleet, emissions, and valuation analytics that underpin high-impact research, regulatory assessments, and strategic decision-making across the global aviation sector.  

    For this project, IBA’s fleet intelligence—covering aircraft configuration, engine pairing, ownership, and operational status—was used to help link aircraft and engine configurations to emissions activity at the airport and aircraft class level.  
    The data is continuously updated and validated through integrations with global flight tracking providers and IBA’s in-house appraisal and consulting teams.  
    [Learn more](https://www.iba.aero)
    """)
