import streamlit as st
import pandas as pd
import folium
import requests
import json
from streamlit.components.v1 import html
from PIL import Image

st.set_page_config(
    page_title="Data Explorer - AIRLIFT",
    page_icon="logo/icct-icon-tab.png",
    layout="wide"
)

api_key = st.secrets["COUNTERAPI_KEY"]
up_url = "https://api.counterapi.dev/v2/aviation/airlift/up"
get_url = "https://api.counterapi.dev/v2/aviation/airlift"


# Set API details
headers = {
    "Authorization": f"Bearer {api_key}"
}

# Initialize session state
if "counted" not in st.session_state:
    st.session_state.counted = False

        
# Load logo
icon = Image.open("logo/icct-icon-tab.png")
logo = Image.open("logo/icct_logo.jpg")
spire_logo = Image.open("logo/LOGO_Spire_Aviation_Color_RGB.png") 
iba_logo = Image.open("logo/IBA Logo.png")      

# Display logo and title
st.set_page_config(
    page_title="Data Explorer - AIRLIFT",
    page_icon=icon,  # optional emoji or use image below
)

# Display logo at the top of the sidebar
with st.sidebar:
    st.image(logo, use_container_width=True)

# Set layout
st.set_page_config(layout="wide")

# Load data
df = pd.read_csv("Data_Sample_with_coordinates_500_airports.csv")
df.columns = df.columns.str.strip()

# Sidebar Filters (default spacing)
st.sidebar.header("Filter Airports")

# Create country options with "All" on top and allow one country selection
country_options = ["All"] + sorted(df['Country'].dropna().unique().tolist())

# Select box with "All" option
selected_country = st.sidebar.selectbox(
    "Select Country", 
    options=country_options
)

# Filter data based on selected country
filtered_df = df if selected_country == "All" else df[df['Country'] == selected_country]


# Allow multiple airports (still using multiselect)
selected_airports = st.sidebar.multiselect(
    "Select Airport", 
    options=sorted(filtered_df['Airport Name'].dropna().unique())
)
filtered_df = filtered_df[filtered_df['Airport Name'].isin(selected_airports)] if selected_airports else filtered_df

# Title
st.title("AIRLIFT - Aircraft Local Impact Footprint Tool ")
st.markdown(
    "This map displays the top 500 airports with the highest flight counts. Click to see the greenhouse gas and NO<sub>x</sub> pollution profile from aircraft landing and take-off activity (LTO). This serves as an example data from the International Council on Clean Transportation's Data Explorer.",
    unsafe_allow_html=True
)
st.markdown(
    'To request access to the full dataset of 5,000 airports with different flight categories and other pollutants (PM<sub>2.5</sub>, HC, and CO), please request access here: <a href="https://forms.office.com/pages/responsepage.aspx?id=n9G9f4nD7UyKBAtQkLgM_hpDOkQLJf9JslWw2OJPUpNUNElSSkJBOTdQVU1WOFBQWkE0SUxIMU9BWC4u&route=shorturl" target="_blank">Request Access Form</a>.',
    unsafe_allow_html=True
)

# Map center logic
if not filtered_df.empty:
    center_lat = filtered_df['Airport Latitude'].mean()
    center_lon = filtered_df['Airport Longitude'].mean()
else:
    center_lat, center_lon = 20, 0

# Summary
st.subheader("Summary of Filtered Results")

# Compute summary
summary = filtered_df[[
    'Flights',
    'Fuel LTO Cycle (kg)',
    'NOx LTO Total mass (g)'
]].sum()

summary.index = [
    'Total Flights',
    'Total LTO Fuel (kg)',
    'Total LTO NOx pollution (g)'
]

# Add number of airports
summary_df = pd.DataFrame(summary).T
summary_df.insert(0, 'Number of Airports', filtered_df['Airport Name'].nunique())
summary_df = summary_df.astype(int)
summary_df.reset_index(drop=True, inplace=True)

# Format with commas
formatted_summary_df = summary_df.map(lambda x: f"{x:,}")

# Display the formatted DataFrame without the index
st.dataframe(formatted_summary_df, use_container_width=True, hide_index=True)

## Dispaly data partners
st.markdown("---")
st.subheader("Data Partners")

# === Spire Section ===
spire_col1, spire_col2 = st.columns([1, 4])
with spire_col1:
    st.write("")
    st.image(spire_logo)
with spire_col2:
    st.markdown("""
    <div style='font-size: 0.85rem; color: gray;'>
        <strong>Spire Aviation</strong> is the industry trustworthy source for global flight tracking data to power applications, drive decision making and improve cost efficiencies. 
        Spire’s 10+ satellites capture global aircraft movements using ADS-B signals, which combined with multi-terrestrial data sources provide enhanced global coverage, not just over inhabited regions, but also in remote locations and above the deep ocean.  
        From historical flight data, ADS-B tracking, to up-to-date data on weather impacting aviation operations, Spire’s versatile datasets help companies solve their business challenges and predict upcoming industry trends.  
        To learn more, visit <a href="https://spire.com/aviation/" target="_blank">https://spire.com/aviation/</a>
        <br><br>
    </div>
    """, unsafe_allow_html=True)


# === IBA Section ===
iba_col1, iba_col2 = st.columns([1, 4])
with iba_col1:
    st.write("")
    st.image(iba_logo)
with iba_col2:
    st.markdown("""
    <div style='font-size: 0.85rem; color: gray;'>
        <strong>IBA</strong> is a trusted provider of aviation intelligence and advisory services, supporting researchers and policy groups, investors, operators, and lessors with robust, data-driven insight. Founded in 1988, IBA delivers comprehensive fleet, emissions, and valuation analytics that underpin high-impact research, regulatory assessments, and strategic decision-making across the global aviation sector.  
        For this project, IBA’s fleet intelligence—covering aircraft configuration, engine pairing, ownership, and operational status—was used to help link aircraft and engine configurations to emissions activity at the airport and aircraft class level. The data is continuously updated and validated through integrations with global flight tracking providers and IBA’s in-house appraisal and consulting teams.  
        Learn more at <a href="https://www.iba.aero" target="_blank">https://www.iba.aero</a>
        <br><br>
    </div>
    """, unsafe_allow_html=True)

# --- Visitor Counter at bottom of main page ---
# Only increment once per session
if not st.session_state.counted:
    post_response = requests.get(up_url, headers=headers)
    if post_response.status_code == 200:
        st.session_state.counted = True  # Mark as counted
        
if not st.session_state.counted:
    if post_response.status_code == 200:
            st.markdown("---")  # separator line

# Always get and display the current count
response = requests.get(get_url, headers=headers)
if response.status_code == 200:
    data = response.json()["data"]
    count = int(data.get("up_count", 0))

    st.markdown(
        f"<div style='text-align: center; font-size: 0.85rem; color: gray;'>"
        f"👥 Total Activities: <b>{count:,}</b> | © 2025 International Council on Clean Transportation. All Rights Reserved.</div>",
        unsafe_allow_html=True
    )
else:
    st.warning("⚠️ Failed to retrieve visit counter.")
