// LandSafe AI dashboard — talks to the FastAPI backend running at API_BASE.
const API_BASE = "https://landsafe-ai-backend.onrender.com";

const map = L.map("map").setView([25.0, 92.5], 6);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

const riskColors = {
  Low: "#5b7553",
  Moderate: "#c17f2c",
  High: "#b4552f",
  Critical: "#a44a3f",
};

let markers = {};

async function checkApiStatus() {
  const el = document.getElementById("apiStatus");
  try {
    const res = await fetch(`${API_BASE}/`);
    if (!res.ok) throw new Error("bad response");
    el.textContent = "✅ Connected to backend";
    el.className = "api-status connected";
    return true;
  } catch (err) {
    el.textContent = "⚠️ Can't reach backend at " + API_BASE + " — is uvicorn running?";
    el.className = "api-status error";
    return false;
  }
}

async function loadZones() {
  const cardsEl = document.getElementById("zoneCards");
  try {
    const res = await fetch(`${API_BASE}/zones`);
    const data = await res.json();

    cardsEl.innerHTML = "";
    data.zones.forEach((zone) => {
      // Update or create map marker
      const color = riskColors[zone.risk_level] || "#888";
      if (markers[zone.id]) {
        markers[zone.id].setStyle({ fillColor: color, color: color });
        markers[zone.id]
          .getPopup()
          .setContent(`<b>${zone.name}</b><br>${zone.risk_level} risk (${(zone.risk_probability * 100).toFixed(0)}%)`);
      } else {
        markers[zone.id] = L.circleMarker([zone.lat, zone.lon], {
          radius: 10,
          color: color,
          fillColor: color,
          fillOpacity: 0.85,
        })
          .addTo(map)
          .bindPopup(`<b>${zone.name}</b><br>${zone.risk_level} risk (${(zone.risk_probability * 100).toFixed(0)}%)`);
      }

      // Zone card
      const card = document.createElement("div");
      card.className = "zone-card";
      card.innerHTML = `
        <span class="risk-badge risk-${zone.risk_level}">${zone.risk_level} — ${(zone.risk_probability * 100).toFixed(0)}%</span>
        <h3>${zone.name}</h3>
        <p class="reading-line">Rainfall: ${zone.reading.rainfall_mm} mm · Slope: ${zone.reading.slope_angle}°</p>
        <p class="reading-line">Soil moisture: ${zone.reading.soil_moisture_pct}% · Vegetation: ${zone.reading.vegetation_cover_pct}%</p>
      `;
      cardsEl.appendChild(card);
    });
  } catch (err) {
    cardsEl.innerHTML = `<p class="empty">Couldn't load zones — check the backend is running.</p>`;
  }
}

async function loadAlerts() {
  const logEl = document.getElementById("alertLog");
  try {
    const res = await fetch(`${API_BASE}/alerts`);
    const data = await res.json();

    if (data.alerts.length === 0) {
      logEl.innerHTML = `<p class="empty">No alerts yet — all zones currently below High risk.</p>`;
      return;
    }

    logEl.innerHTML = "";
    data.alerts.slice(0, 10).forEach((alert) => {
      const item = document.createElement("div");
      item.className = "alert-item";
      item.innerHTML = `
        ${alert.message}
        <time>${new Date(alert.timestamp).toLocaleString()}</time>
      `;
      logEl.appendChild(item);
    });
  } catch (err) {
    logEl.innerHTML = `<p class="empty">Couldn't load alerts.</p>`;
  }
}

async function refreshAll() {
  await loadZones();
  await loadAlerts();
}

document.getElementById("refreshBtn").addEventListener("click", refreshAll);

document.getElementById("predictForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const payload = {};
  new FormData(form).forEach((value, key) => {
    payload[key] = parseFloat(value);
  });

  const resultEl = document.getElementById("predictResult");
  resultEl.innerHTML = "Calculating…";

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    const color = riskColors[data.risk_level] || "#888";
    resultEl.innerHTML = `
      <div class="result-box" style="background:${color}">
        ${data.risk_level} risk — ${(data.risk_probability * 100).toFixed(1)}% probability
      </div>
    `;
  } catch (err) {
    resultEl.innerHTML = `<p class="empty">Couldn't reach backend for prediction.</p>`;
  }
});

// Initial load
(async () => {
  const connected = await checkApiStatus();
  if (connected) {
    refreshAll();
  }
})();
