const DATA_URL = "Data_Explorer_Final_500_example_v3.csv";
const DEFAULT_CENTER = [20, 0];
const DEFAULT_ZOOM = 2;
const MAP_STYLE = [
  { featureType: "all", elementType: "labels", stylers: [{ visibility: "off" }] },
  {
    featureType: "road",
    elementType: "geometry",
    stylers: [{ lightness: 100 }, { visibility: "simplified" }],
  },
  {
    featureType: "water",
    elementType: "geometry",
    stylers: [{ visibility: "on" }, { color: "#C6E2FF" }],
  },
  {
    featureType: "administrative.country",
    elementType: "geometry.stroke",
    stylers: [{ visibility: "off" }],
  },
  {
    featureType: "administrative.province",
    elementType: "geometry.stroke",
    stylers: [{ visibility: "off" }],
  },
  {
    featureType: "administrative.locality",
    elementType: "geometry.stroke",
    stylers: [{ visibility: "off" }],
  },
  {
    featureType: "administrative.land_parcel",
    elementType: "geometry.stroke",
    stylers: [{ visibility: "off" }],
  },
];

const state = {
  rawData: [],
  filteredData: [],
  selectedCountry: "All",
  airportSearch: "",
  selectedAirports: [],
};

const urlParams = new URLSearchParams(window.location.search);
const isEmbedMode = urlParams.get("view") === "map" && urlParams.get("embed") === "true";

const dom = {
  page: document.body.dataset.page,
  countrySelect: document.getElementById("countrySelect"),
  airportSearch: document.getElementById("airportSearch"),
  airportChecklist: document.getElementById("airportChecklist"),
  clearAirports: document.getElementById("clearAirports"),
  selectVisibleAirports: document.getElementById("selectVisibleAirports"),
  summaryCards: document.getElementById("summaryCards"),
  topAirportsBody: document.getElementById("topAirportsBody"),
  mapSelectionLabel: document.getElementById("mapSelectionLabel"),
  tableCaption: document.getElementById("tableCaption"),
};

let map;
let markers = [];
let openInfoWindows = [];
let appBootstrapped = false;
let dataLoaded = false;

document.addEventListener("DOMContentLoaded", bootstrapApp);
window.initAirliftMap = handleGoogleMapsReady;

async function bootstrapApp() {
  if (appBootstrapped) {
    return;
  }

  appBootstrapped = true;

  if (isEmbedMode && dom.page === "main") {
    document.body.classList.add("embed-mode");
  }

  window.setTimeout(() => {
    if (!map) {
      renderMapUnavailable();
    }
  }, 2500);

  try {
    const text = await fetch(DATA_URL).then((response) => {
      if (!response.ok) {
        throw new Error(`Failed to load dataset (${response.status})`);
      }
      return response.text();
    });

    state.rawData = normalizeRows(parseCsv(text));
    dataLoaded = true;
    hydrateStateFromUrl();
    hydrateControls();
    bindEvents();
    applyFilters();
  } catch (error) {
    renderError(error);
  }
}

function handleGoogleMapsReady() {
  initMap();

  if (dataLoaded) {
    renderMap();
  }
}

function initMap() {
  if (map || typeof google === "undefined" || !google.maps) {
    return;
  }

  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: DEFAULT_CENTER[0], lng: DEFAULT_CENTER[1] },
    zoom: DEFAULT_ZOOM,
    styles: MAP_STYLE,
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: true,
    minZoom: 2,
    maxZoom: 12,
  });
}

function bindEvents() {
  if (!dom.countrySelect) {
    return;
  }

  dom.countrySelect.addEventListener("change", (event) => {
    state.selectedCountry = event.target.value;
    state.selectedAirports = [];
    syncAirportChecklist();
    applyFilters();
  });

  dom.airportSearch.addEventListener("input", (event) => {
    state.airportSearch = event.target.value.trim().toLowerCase();
    syncAirportChecklist();
  });

  dom.clearAirports.addEventListener("click", () => {
    state.selectedAirports = [];
    syncAirportChecklist();
    applyFilters();
  });

  dom.selectVisibleAirports.addEventListener("click", () => {
    const visibleAirportNames = getVisibleAirportNames();
    state.selectedAirports = visibleAirportNames;
    syncAirportChecklist();
    applyFilters();
  });

  dom.airportChecklist.addEventListener("change", (event) => {
    if (!(event.target instanceof HTMLInputElement) || event.target.type !== "checkbox") {
      return;
    }

    const airportName = event.target.value;

    if (event.target.checked) {
      state.selectedAirports = [...new Set([...state.selectedAirports, airportName])];
    } else {
      state.selectedAirports = state.selectedAirports.filter((name) => name !== airportName);
    }

    applyFilters();
  });
}

function hydrateControls() {
  if (!dom.countrySelect) {
    return;
  }

  const countries = ["All", ...new Set(state.rawData.map((row) => row.country))].sort((a, b) => {
    if (a === "All") return -1;
    if (b === "All") return 1;
    return a.localeCompare(b);
  });

  dom.countrySelect.innerHTML = countries
    .map((country) => `<option value="${escapeHtml(country)}">${escapeHtml(country)}</option>`)
    .join("");
  dom.countrySelect.value = countries.includes(state.selectedCountry) ? state.selectedCountry : "All";

  syncAirportChecklist();
}

function syncAirportChecklist() {
  if (!dom.airportChecklist) {
    return;
  }

  const airportNames = getVisibleAirportNames();

  dom.airportChecklist.innerHTML = airportNames.length
    ? airportNames
        .map((name) => {
          const checked = state.selectedAirports.includes(name) ? " checked" : "";
          return `
            <label class="airport-option">
              <input type="checkbox" value="${escapeHtml(name)}"${checked} />
              <span>${escapeHtml(name)}</span>
            </label>
          `;
        })
        .join("")
    : '<div class="empty-state">No airports match this search.</div>';
}

function applyFilters() {
  const countryRows =
    state.selectedCountry === "All"
      ? state.rawData
      : state.rawData.filter((row) => row.country === state.selectedCountry);

  state.filteredData = state.selectedAirports.length
    ? countryRows.filter((row) => state.selectedAirports.includes(row.airportName))
    : countryRows;

  if (isEmbedMode) {
    state.filteredData = countryRows;
  }

  if (map) {
    renderMap();
  } else {
    renderMapUnavailable();
  }

  if (dom.page === "main") {
    renderSummary();
    renderTopAirports();
    renderLabels();
  }
}

function renderMap() {
  if (!map) {
    renderMapUnavailable();
    return;
  }

  markers.forEach((marker) => marker.setMap(null));
  markers = [];
  openInfoWindows.forEach((popup) => popup.close());
  openInfoWindows = [];

  if (!state.filteredData.length) {
    map.setCenter({ lat: DEFAULT_CENTER[0], lng: DEFAULT_CENTER[1] });
    map.setZoom(DEFAULT_ZOOM);
    return;
  }

  const bounds = new google.maps.LatLngBounds();

  state.filteredData.forEach((row) => {
    const marker = new google.maps.Marker({
      position: { lat: row.latitude, lng: row.longitude },
      map,
      title: row.airportName,
      icon: {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: "#ffffff",
        fillOpacity: 1,
        scale: getMarkerRadius(row.flights),
        strokeColor: "#007d93",
        strokeWeight: 3,
      },
    });

    const popupContent = `
      <div class="popup-card">
        <h4>${escapeHtml(row.airportName)}</h4>
        <p><strong>Country:</strong> ${escapeHtml(row.country)}</p>
        <p><strong>Flights:</strong> ${formatNumber(row.flights)}</p>
        <p><strong>Fuel LTO Cycle:</strong> ${formatNumber(row.fuelLtoKg)} kg</p>
        <p><strong>NOx LTO:</strong> ${formatNumber(row.noxLtoG)} g</p>
      </div>
    `;

    marker.addListener("click", () => {
      const infoWindow = new google.maps.InfoWindow({
        content: popupContent,
      });

      infoWindow.open({ anchor: marker, map });
      openInfoWindows.push(infoWindow);

      infoWindow.addListener("closeclick", () => {
        openInfoWindows = openInfoWindows.filter((popup) => popup !== infoWindow);
      });
    });

    markers.push(marker);
    bounds.extend(marker.getPosition());
  });

  if (state.filteredData.length === 1) {
    map.setCenter(bounds.getCenter());
    map.setZoom(6);
  } else {
    map.fitBounds(bounds, 40);
  }
}

function renderSummary() {
  if (!dom.summaryCards) {
    return;
  }

  const totals = state.filteredData.reduce(
    (accumulator, row) => {
      accumulator.airports.add(row.airportName);
      accumulator.flights += row.flights;
      accumulator.fuel += row.fuelLtoKg;
      accumulator.nox += row.noxLtoG;
      return accumulator;
    },
    { airports: new Set(), flights: 0, fuel: 0, nox: 0 }
  );

  const cards = [
    { label: "Airports", value: formatNumber(totals.airports.size) },
    { label: "Flights", value: formatNumber(totals.flights) },
    { label: "Fuel LTO Cycle (kg)", value: formatNumber(totals.fuel) },
    { label: "NOx LTO (g)", value: formatNumber(totals.nox) },
  ];

  dom.summaryCards.innerHTML = cards
    .map(
      (card) => `
        <article class="stat-card">
          <span class="toolbar-label">${card.label}</span>
          <span class="value">${card.value}</span>
          <span class="label">Current filtered total</span>
        </article>
      `
    )
    .join("");
}

function renderMapUnavailable() {
  const mapElement = document.getElementById("map");

  if (!mapElement || map) {
    return;
  }

  mapElement.innerHTML = `
    <div class="empty-state">
      Google Maps did not load. This usually means the API key is restricted, invalid, or blocked for the current URL.
    </div>
  `;
}

function renderTopAirports() {
  if (!dom.topAirportsBody) {
    return;
  }

  if (!state.filteredData.length) {
    dom.topAirportsBody.innerHTML = `
      <tr>
        <td colspan="5">
          <div class="empty-state">No airports match the current filters.</div>
        </td>
      </tr>
    `;
    return;
  }

  const rows = [...state.filteredData]
    .sort((left, right) => right.flights - left.flights)
    .slice(0, 5)
    .map(
      (row) => `
        <tr>
          <td>${escapeHtml(row.airportName)}</td>
          <td>${escapeHtml(row.country)}</td>
          <td>${formatNumber(row.flights)}</td>
          <td>${formatNumber(row.fuelLtoKg)} kg</td>
          <td>${formatNumber(row.noxLtoG)} g</td>
        </tr>
      `
    )
    .join("");

  dom.topAirportsBody.innerHTML = rows;
}

function renderLabels() {
  if (!dom.mapSelectionLabel || !dom.tableCaption) {
    return;
  }

  const countryLabel = state.selectedCountry === "All" ? "All countries" : state.selectedCountry;
  const airportCount = new Set(state.filteredData.map((row) => row.airportName)).size;

  dom.mapSelectionLabel.textContent = `${countryLabel} • ${formatNumber(airportCount)} airports`;
  dom.tableCaption.textContent = `Showing the top ${Math.min(
    5,
    airportCount
  )} airports by flights in the current filtered view.`;
}

function renderError(error) {
  console.error(error);
  if (dom.page === "main") {
    if (dom.summaryCards) {
      dom.summaryCards.innerHTML = `
        <div class="empty-state">The dataset could not be loaded. Check the browser console for details.</div>
      `;
    }

    if (dom.topAirportsBody) {
      dom.topAirportsBody.innerHTML = `
        <tr>
          <td colspan="5">
            <div class="empty-state">The dataset could not be loaded.</div>
          </td>
        </tr>
      `;
    }
  }
}

function hydrateStateFromUrl() {
  const countryParam = urlParams.get("country");

  if (countryParam) {
    const matchingCountry = state.rawData.find(
      (row) => row.country.toLowerCase() === countryParam.trim().toLowerCase()
    );

    if (matchingCountry) {
      state.selectedCountry = matchingCountry.country;
    }
  }
}

function getVisibleAirportNames() {
  const baseRows =
    state.selectedCountry === "All"
      ? state.rawData
      : state.rawData.filter((row) => row.country === state.selectedCountry);

  return [...new Set(baseRows.map((row) => row.airportName))]
    .filter((name) => name.toLowerCase().includes(state.airportSearch))
    .sort((a, b) => a.localeCompare(b));
}

function parseCsv(text) {
  const rows = [];
  let current = "";
  let row = [];
  let inQuotes = false;

  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];
    const nextCharacter = text[index + 1];

    if (character === '"') {
      if (inQuotes && nextCharacter === '"') {
        current += '"';
        index += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if (character === "," && !inQuotes) {
      row.push(current);
      current = "";
      continue;
    }

    if ((character === "\n" || character === "\r") && !inQuotes) {
      if (character === "\r" && nextCharacter === "\n") {
        index += 1;
      }
      row.push(current);
      if (row.some((value) => value !== "")) {
        rows.push(row);
      }
      current = "";
      row = [];
      continue;
    }

    current += character;
  }

  if (current || row.length) {
    row.push(current);
    rows.push(row);
  }

  const [header, ...dataRows] = rows;
  return dataRows.map((dataRow) =>
    header.reduce((record, column, columnIndex) => {
      record[column.trim()] = dataRow[columnIndex] ?? "";
      return record;
    }, {})
  );
}

function normalizeRows(rows) {
  return rows.map((row) => ({
    countryCode: row["Country Code"],
    country: row.Country,
    airportCode: row["Airport ICAO Code"],
    airportName: row["Airport Name"],
    latitude: Number(row["Airport Latitude"]),
    longitude: Number(row["Airport Longitude"]),
    operationType: row["Operation Type"],
    flights: Number(row.Flights),
    fuelLtoKg: Number(row["Fuel LTO Cycle (kg)"]),
    noxLtoG: Number(row["NOx LTO Total mass (g)"]),
    pm25LtoG: Number(row["PM2.5 LTO Emission (g)"]),
    hcLtoG: Number(row["HC LTO Total mass (g)"]),
    coLtoG: Number(row["CO LTO Total Mass (g)"]),
  }));
}

function getMarkerRadius(flights) {
  if (flights > 150000) return 10;
  if (flights > 75000) return 8;
  if (flights > 25000) return 6;
  return 5;
}

function formatNumber(value) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
