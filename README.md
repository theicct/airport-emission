# AIRLIFT - Aircraft Local Impact Footprint Tool
Visualization by: Daniel Sitompul

This repository shares the full code to run the AIRLIFT data explorer visualization that shares 500 airports as an example to the main data explorer.
Related publication link: https://theicct.org/airlift-aircraft-local-impact-footprint-tool-nov25/

### Preparation to run this on your own machine

1. Google MAPs API
   To run this map, you need to have a google map API ready. You can create it through the Google Cloud Console (https://console.cloud.google.com).    

2. Counter API
   To enable the counter, create an API through https://counterapi.dev 

3. Prepare a folder for API code:
   i. Make a folder on the airport-emission directory '.streamlit'
   ii. Input the API code:
   ```
   COUNTERAPI_KEY = "[your_counter_api_code]"
   GOOGLE_MAPS_API_KEY = "[your_google_maps_api_code]"
   ```
   
### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
   
3. Open the website on your local machine by opening the local URL
   Example of local URL:
   ```
   $ http://localhost:8501
   ```