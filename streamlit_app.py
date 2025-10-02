import os
import json
import requests
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit.components.v1 import html

st.set_page_config(
    page_title="Data Explorer - AIRLIFT",
    page_icon="logo/icct-icon-tab.png",
    layout="wide"
)

# --- ENV VARS (Azure/App Service) ---
COUNTERAPI_KEY = os.getenv("COUNTERAPI_KEY", "")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

headers = {"Authorization": f"Bearer {COUNTERAPI_KEY}"} if COUNTERAPI_KEY else {}

up_url = "https://api.counterapi.dev/v2/aviation/airlift/up"
get_url = "https://api.counterapi.dev/v2/aviation/airlift"

# Initialize session state
if "counted" not in st.session_state:
    st.session_state.counted = False

# --- Logos ---
icon = Image.open("logo/icct-icon-tab.png")
logo = Image.open("logo/icct_logo.jpg")
spire_logo = Image.open("logo/LOGO_Spire_Aviation_Color_RGB.png")
iba_logo = Image.open("logo/IBA Logo.png")

# Display logo at the top of the sidebar
with st.sidebar:
    st.image(logo, use_container_width=True)

# --- Load Data ---
df = pd.read_csv("Data_Sample_with_coordinates_500_airports.csv")
df.columns = df.columns.str.strip()

# --- Sidebar Filters ---
st.sidebar.header("Filter Airports")

country_options = ["All"] + sorted(df['Country'].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", options=country_options)

filtered_df = df if selected_country == "All" else df[df['Country'] == selected_country]

selected_airports = st.sidebar.multiselect(
    "Select Airport",
    options=sorted(filtered_df['Airport Name'].dropna().unique())
)
filtered_df = filtered_df[filtered_df['Airport Name'].isin(selected_airports)] if selected_airports else filtered_df

# --- Title & Intro ---
st.title("AIRLIFT - Aircraft Local Impact Footprint Tool")
st.markdown(
    "This map displays the top 500 airports with the highest flight counts. "
    "Click to see the greenhouse gas and NO<sub>x</sub> pollution profile from "
    "aircraft landing and take-off activity (LTO). This serves as an example "
    "dataset from the International Council on Clean Transportation's Data Explorer.",
    unsafe_allow_html=True
)
st.markdown(
    'To request access to the full dataset of 5,000 airports with different flight categories '
    'and other pollutants (PM<sub>2.5</sub>, HC, and CO), please request access here: '
    '<a href="https://forms.office.com/pages/responsepage.aspx?id=n9G9f4nD7UyKBAtQkLgM_hpDOkQLJf9JslWw2OJPUpNUNElSSkJBOTdQVU1WOFBQWkE0SUxIMU9BWC4u&route=shorturl" target="_blank">Request Access Form</a>.',
    unsafe_allow_html=True
)

# --- Map Center ---
if not filtered_df.empty:
    center_lat = filtered_df['Airport Latitude'].mean()
    center_lon = filtered_df['Airport Longitude'].mean()
else:
    center_lat, center_lon = 20, 0

# --- Map CSS ---
st.markdown(
    """
    <style>
    .full-width-container {
        width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Map Rendering ---
if not filtered_df.empty:
    zoom_level = 2 if selected_country == "All" else 5

    snazzy_style = [
        {"featureType": "all", "elementType": "labels", "stylers": [{"visibility": "off"}]},
        {"featureType": "road", "elementType": "geometry", "stylers": [{"lightness": 100}, {"visibility": "simplified"}]},
        {"featureType": "water", "elementType": "geometry", "stylers": [{"visibility": "on"}, {"color": "#C6E2FF"}]},
        {"featureType": "administrative.country", "elementType": "geometry.stroke", "stylers": [{"visibility": "off"}]},
        {"featureType": "administrative.province", "elementType": "geometry.stroke", "stylers": [{"visibility": "off"}]},
        {"featureType": "administrative.locality", "elementType": "geometry.stroke", "stylers": [{"visibility": "off"}]},
        {"featureType": "administrative.land_parcel", "elementType": "geometry.stroke", "stylers": [{"visibility": "off"}]}
    ]

    airport_data = filtered_df.to_dict(orient='records')
    for row in airport_data:
        row['Airport Latitude'] = float(row['Airport Latitude'])
        row['Airport Longitude'] = float(row['Airport Longitude'])
        row['Flights'] = int(row['Flights'])
        row['Fuel LTO Cycle (kg)'] = int(row['Fuel LTO Cycle (kg)'])
        row['NOx LTO Total mass (g)'] = int(row['NOx LTO Total mass (g)'])

    map_html = f"""
      <div id="map" style="height: 600px; width: 100%;"></div>
      <script>
        function initMap() {{
          var center = {{lat: {center_lat}, lng: {center_lon} }};
          var map = new google.maps.Map(document.getElementById('map'), {{
            center: center,
            zoom: {zoom_level},
            styles: {json.dumps(snazzy_style)},
            mapTypeControl: false,
            streetViewControl: false,
            minZoom: 2,
            maxZoom: 10
          }});

          var bounds = new google.maps.LatLngBounds();
          var airports = {json.dumps(airport_data)};

          airports.forEach(function(airport) {{
            var latLng = new google.maps.LatLng(airport["Airport Latitude"], airport["Airport Longitude"]);
            var marker = new google.maps.Marker({{
              position: latLng,
              map: map,
              title: airport["Airport Name"],
              icon: {{
                path: google.maps.SymbolPath.CIRCLE,
                fillColor: "#ffffff",
                fillOpacity: 1,
                scale: 6,
                strokeColor: "#007D93",
                strokeWeight: 3
              }}
            }});

            var popup = new google.maps.InfoWindow({{
              content: `
                <div style="font-size: 14px;">
                  <b>Airport:</b> ${{airport["Airport Name"]}}<br>
                  <b>Country:</b> ${{airport["Country"]}}<br>
                  <b>Flights:</b> ${{airport["Flights"].toLocaleString()}}<br>
                  <b>Fuel LTO Cycle (kg):</b> ${{airport["Fuel LTO Cycle (kg)"].toLocaleString()}}<br>
                  <b>NOx LTO (g):</b> ${{airport["NOx LTO Total mass (g)"].toLocaleString()}}
                </div>
              `
            }});

            marker.addListener('click', function() {{
              popup.open(map, marker);
            }});

            bounds.extend(latLng);
          }});

          if (airports.length > 1) {{
            map.fitBounds(bounds);
          }}
        }}
      </script>
      <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}&callback=initMap" async defer></script>
      """

    with st.container():
        html(map_html, height=650)
else:
    st.warning("No data available for the selected filter. Please adjust your selection.")

# --- Summary ---
st.subheader("Summary of Filtered Results")
summary = filtered_df[['Flights', 'Fuel LTO Cycle (kg)', 'NOx LTO Total mass (g)']].sum()
summary.index = ['Total Flights', 'Total LTO Fuel (kg)', 'Total LTO NOx pollution (g)']

summary_df = pd.DataFrame(summary).T
summary_df.insert(0, 'Number of Airports', filtered_df['Airport Name'].nunique())
summary_df = summary_df.astype(int).reset_index(drop=True)

formatted_summary_df = summary_df.map(lambda x: f"{x:,}")
st.dataframe(formatted_summary_df, use_container_width=True, hide_index=True)

# --- Data Partners ---
st.markdown("---")
st.subheader("Data Partners")

spire_col1, spire_col2 = st.columns([1, 4])
with spire_col1:
    st.image(spire_logo)
with spire_col2:
    st.markdown("""
    <div style='font-size: 0.85rem; color: gray;'>
        <strong>Spire Aviation</strong> is the industry trustworthy source for global flight tracking data...
        To learn more, visit <a href="https://spire.com/aviation/" target="_blank">https://spire.com/aviation/</a>
    </div>
    """, unsafe_allow_html=True)

iba_col1, iba_col2 = st.columns([1, 4])
with iba_col1:
    st.image(iba_logo)
with iba_col2:
    st.markdown("""
    <div style='font-size: 0.85rem; color: gray;'>
        <strong>IBA</strong> is a trusted provider of aviation intelligence and advisory services...
        Learn more at <a href="https://www.iba.aero" target="_blank">https://www.iba.aero</a>
    </div>
    """, unsafe_allow_html=True)

# --- Visitor Counter ---
if COUNTERAPI_KEY and not st.session_state.counted:
    try:
        post_response = requests.get(up_url, headers=headers, timeout=5)
        if post_response.status_code == 200:
            st.session_state.counted = True
    except Exception:
        pass

if COUNTERAPI_KEY:
    try:
        response = requests.get(get_url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json().get("data", {})
            count = int(data.get("up_count", 0))
            st.markdown(
                f"<div style='text-align: center; font-size: 0.85rem; color: gray;'>"
                f"👥 Total Activities: <b>{count:,}</b> | © 2025 International Council on Clean Transportation. All Rights Reserved.</div>",
                unsafe_allow_html=True
            )
    except Exception:
        st.warning("⚠️ Failed to retrieve visit counter.")
