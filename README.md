# AIRLIFT - Aircraft Local Impact Footprint Tool

AIRLIFT is now set up as a lightweight web application instead of a Streamlit app. The new frontend keeps the core experience from the original prototype while introducing a more polished ICCT-aligned presentation layer, responsive layout, and a dedicated embed page.

## What is included

- `index.html`: main AIRLIFT experience
- `embed.html`: map-only embed view
- `styles.css`: shared visual system and layout
- `app.js`: dataset loading, filtering, map rendering, summaries, and tables
- `Data_Explorer_Final_500_example_v3.csv`: local sample dataset used by the app

The original `streamlit_app.py` is still in the repository for reference during migration, but the new web version does not depend on Streamlit.

## How to run locally

Because the app fetches the CSV in the browser, serve the folder over HTTP instead of opening `index.html` directly as a file.

Before starting the app, generate a local `config.js` from `.streamlit/secrets.toml`. Do not commit `config.js`.

```bash
cd "[repo-location]"
python3 generate_config.py
python3 -m http.server 8000
```

Then open:

- `http://localhost:8000/index.html`
- `http://localhost:8000/embed.html`

## Notes

- The current version uses Google Maps JavaScript API for the map layer and marker styling.
- `config.js` is intentionally ignored by git so the browser key is not committed to the repository.
- `generate_config.py` reads `GOOGLE_MAPS_API_KEY` from `.streamlit/secrets.toml` and writes the browser config file used by the app.
- The previous visitor counter depended on a protected API key. It is not wired into the static frontend to avoid exposing secrets client-side.
- If you want the counter back, the next step is to add a tiny backend or serverless endpoint that proxies the counter service securely.
