// Decoupled API Configuration
const API_BASE = (typeof import.meta !== "undefined" && import.meta.env && import.meta.env.VITE_API_BASE_URL)
  || (typeof window !== "undefined" && window.__API_BASE_URL__)
  || "http://127.0.0.1:8000";

const API_MACRO_URL         = `${API_BASE}/api/simulate`;
const API_MICRO_URL         = `${API_BASE}/api/simulate-micro`;
const API_GIS_URL           = `${API_BASE}/api/gis-corridor`;
const API_V2X_URL           = `${API_BASE}/api/simulate-v2x`;
const API_INTERSECTIONS_URL = `${API_BASE}/api/intersections`;
const API_DETECTION_URL     = `${API_BASE}/api/detect-emergency-approach`;

let activeTab = "macro"; // "macro" | "micro" | "v2x"
let isFetching = false;

// State: Macroscopic
let baselineFrames = [];
let alertFrames = [];
let totalSteps = 0;
let currentFrame = 0;
let animTimer = null;
let isPaused = false;
let chartInstance = null;

// State: Microscopic
let microFrames = [];
let microGisData = [];
let microCurrentFrame = 0;
let microAnimTimer = null;
let microTotalSteps = 0;
let microMetrics = null;

// State: V2X & Green Corridor
let v2xFrames = [];
let v2xCurrentFrame = 0;
let v2xAnimTimer = null;
let v2xTotalSteps = 0;
let v2xMetrics = null;
let intersectionList = [];

// ==================== TAB SWITCHING ====================
function switchTab(tab) {
  activeTab = tab;
  stopAllAnimations();
  isPaused = false;
  document.getElementById("btn-pause").innerText = "Pause";

  const btnMacro = document.getElementById("tab-btn-macro");
  const btnMicro = document.getElementById("tab-btn-micro");
  const btnV2x   = document.getElementById("tab-btn-v2x");

  const viewMacro = document.getElementById("view-macro");
  const viewMicro = document.getElementById("view-micro");
  const viewV2x   = document.getElementById("view-v2x");

  btnMacro.classList.remove("active");
  btnMicro.classList.remove("active");
  btnV2x.classList.remove("active");

  viewMacro.classList.remove("active");
  viewMicro.classList.remove("active");
  viewV2x.classList.remove("active");

  const N = parseInt(document.getElementById("corridor").value, 10);

  if (tab === "macro") {
    btnMacro.classList.add("active");
    viewMacro.classList.add("active");
    initRoadTrack(N);
  } else if (tab === "micro") {
    btnMicro.classList.add("active");
    viewMicro.classList.add("active");
    loadGisWaypoints();
  } else if (tab === "v2x") {
    btnV2x.classList.add("active");
    viewV2x.classList.add("active");
    initV2XCorridorTrack(N);
    loadIntersections();
  }
}

function stopAllAnimations() {
  clearInterval(animTimer);
  clearInterval(microAnimTimer);
  clearInterval(v2xAnimTimer);
}

function setButtonLoading(loading) {
  const btn = document.getElementById("btn-run");
  if (!btn) return;
  if (loading) {
    btn.disabled = true;
    btn.dataset.prevText = btn.innerText;
    btn.innerText = "Simulating...";
    btn.style.opacity = "0.7";
  } else {
    btn.disabled = false;
    btn.innerText = btn.dataset.prevText || "Run Simulation";
    btn.style.opacity = "1.0";
  }
}

function startActiveSimulation() {
  if (isFetching) return;
  if (activeTab === "macro") {
    fetchAndStartSimulation();
  } else if (activeTab === "micro") {
    fetchAndStartMicroSimulation();
  } else if (activeTab === "v2x") {
    fetchAndStartV2XSimulation();
  }
}

// ==================== GIS WAYPOINTS ====================
async function loadGisWaypoints() {
  try {
    const res = await fetch(API_GIS_URL);
    if (!res.ok) return;
    const data = await res.json();
    microGisData = data.waypoints || [];
    renderGisRibbon(microGisData, -1);
  } catch (err) {
    console.warn("Failed to load GIS corridor:", err);
  }
}

function renderGisRibbon(waypoints, activeSeg) {
  const container = document.getElementById("gis-waypoints-list");
  if (!container) return;
  container.innerHTML = "";

  waypoints.forEach((wp, idx) => {
    const node = document.createElement("div");
    node.className = "gis-node";
    node.id = `gis-node-${idx}`;

    if (activeSeg >= wp.segment && (idx === waypoints.length - 1 || activeSeg < waypoints[idx + 1].segment)) {
      node.classList.add("active");
      const activeText = document.getElementById("gis-active-landmark");
      if (activeText) activeText.innerText = `Active Sector: ${wp.name}`;
    }

    node.innerHTML = `
      <div class="gis-node-seg">Seg ${wp.segment}</div>
      <div class="gis-node-name">${wp.name}</div>
      <div class="gis-node-coords">${wp.lat.toFixed(4)}°N, ${wp.lon.toFixed(4)}°E</div>
    `;
    container.appendChild(node);
  });
}

// ==================== MACROSCOPIC SIMULATION (PHASE 5) ====================
function initRoadTrack(segmentCount) {
  const trackAlert = document.getElementById("track-alert");
  const trackBase = document.getElementById("track-base");
  if (!trackAlert || !trackBase) return;

  trackAlert.innerHTML = '<div class="ambulance-marker alert-active" id="amb-alert">🚑</div>';
  trackBase.innerHTML = '<div class="ambulance-marker" id="amb-base">🚑</div>';

  trackAlert.style.gridTemplateColumns = `repeat(${segmentCount}, 1fr)`;
  trackBase.style.gridTemplateColumns = `repeat(${segmentCount}, 1fr)`;

  for (let i = 0; i < segmentCount; i++) {
    const sA = document.createElement("div");
    sA.className = "segment";
    sA.id = `alert-seg-${i}`;
    sA.innerText = i;
    trackAlert.appendChild(sA);

    const sB = document.createElement("div");
    sB.className = "segment";
    sB.id = `base-seg-${i}`;
    sB.innerText = i;
    trackBase.appendChild(sB);
  }
}

function initChart() {
  const chartElem = document.getElementById('trajectoryChart');
  if (!chartElem) return;
  const ctx = chartElem.getContext('2d');
  if (chartInstance) chartInstance.destroy();

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'With Advance Alert',
          borderColor: '#0284c7',
          backgroundColor: 'rgba(2, 132, 199, 0.1)',
          data: [],
          tension: 0.1,
          borderWidth: 2
        },
        {
          label: 'Baseline (No Alert)',
          borderColor: '#ef4444',
          borderDash: [5, 5],
          data: [],
          tension: 0.1,
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { title: { display: true, text: 'Time Step', color: '#94a3b8' }, ticks: { color: '#94a3b8' } },
        y: { title: { display: true, text: 'Position (Segments)', color: '#94a3b8' }, ticks: { color: '#94a3b8' } }
      },
      plugins: {
        legend: { labels: { color: '#f8fafc' } }
      }
    }
  });
}

async function fetchAndStartSimulation() {
  stopAllAnimations();
  isPaused = false;
  document.getElementById("btn-pause").innerText = "Pause";

  const H = parseInt(document.getElementById("horizon").value, 10);
  const alpha = parseFloat(document.getElementById("cooperation").value);
  const N = parseInt(document.getElementById("corridor").value, 10);

  initRoadTrack(N);
  initChart();

  isFetching = true;
  setButtonLoading(true);

  try {
    const response = await fetch(API_MACRO_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ corridor_length: N, horizon: H, cooperation: alpha })
    });

    if (!response.ok) throw new Error("Simulation calculation failed");

    const data = await response.json();
    baselineFrames = data.baseline_frames;
    alertFrames = data.alert_frames;

    document.getElementById("metric-baseline-time").innerText = `${data.metrics.baseline_time} steps`;
    document.getElementById("metric-alert-time").innerText = `${data.metrics.alert_time} steps`;
    document.getElementById("metric-saved").innerText = `${data.metrics.pct_improvement}% (${data.metrics.time_saved} steps saved)`;

    totalSteps = Math.max(baselineFrames.length, alertFrames.length);
    currentFrame = 0;

    animTimer = setInterval(renderMacroNextFrame, 120);
  } catch (err) {
    alert("Connection Error to Backend API: " + err.message);
  } finally {
    isFetching = false;
    setButtonLoading(false);
  }
}

function renderMacroNextFrame() {
  if (isPaused) return;

  if (currentFrame >= totalSteps) {
    clearInterval(animTimer);
    document.getElementById("lane-alert-status").innerText = "Completed Arrival";
    document.getElementById("lane-base-status").innerText = "Completed Arrival";
    return;
  }

  document.getElementById("metric-step").innerText = currentFrame;

  const N = parseInt(document.getElementById("corridor").value, 10);

  if (currentFrame < alertFrames.length) {
    const fA = alertFrames[currentFrame];
    updateCorridorUI(fA, "alert-seg-", document.getElementById("amb-alert"), N);
    document.getElementById("lane-alert-status").innerText = `Pos: Seg ${fA.ambulance_pos} (Speed: ${fA.ambulance_speed.toFixed(2)})`;
    if (chartInstance) {
      chartInstance.data.labels.push(currentFrame);
      chartInstance.data.datasets[0].data.push(fA.ambulance_pos);
    }
  }

  if (currentFrame < baselineFrames.length) {
    const fB = baselineFrames[currentFrame];
    updateCorridorUI(fB, "base-seg-", document.getElementById("amb-base"), N);
    document.getElementById("lane-base-status").innerText = `Pos: Seg ${fB.ambulance_pos} (Speed: ${fB.ambulance_speed.toFixed(2)})`;
    if (chartInstance) {
      chartInstance.data.datasets[1].data.push(fB.ambulance_pos);
    }
  }

  if (chartInstance) chartInstance.update();
  currentFrame++;
}

function updateCorridorUI(frame, segPrefix, markerElem, N) {
  for (let i = 0; i < N; i++) {
    const seg = document.getElementById(`${segPrefix}${i}`);
    if (!seg) continue;
    const density = frame.density[i];
    const red = Math.floor(density * 220 + 20);
    const green = Math.floor((1 - density) * 180 + 20);
    seg.style.backgroundColor = `rgb(${red}, ${green}, 40)`;
  }
  const pct = (frame.ambulance_pos / N) * 100;
  markerElem.style.left = `calc(${pct}% - 13px)`;
}

// ==================== MICROSCOPIC SIMULATION (PHASE 7) ====================
async function fetchAndStartMicroSimulation() {
  stopAllAnimations();
  isPaused = false;
  document.getElementById("btn-pause").innerText = "Pause";

  const H = parseInt(document.getElementById("horizon").value, 10);
  const alpha = parseFloat(document.getElementById("cooperation").value);
  const N = parseInt(document.getElementById("corridor").value, 10);

  isFetching = true;
  setButtonLoading(true);

  try {
    const res = await fetch(API_MICRO_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ corridor_length: N, horizon: H, cooperation: alpha })
    });

    if (!res.ok) throw new Error("Micro simulation request failed");

    const data = await res.json();
    microMetrics = data.metrics;
    microFrames = data.alert_frames || [];
    microGisData = data.gis_corridor || [];
    microTotalSteps = microFrames.length;
    microCurrentFrame = 0;

    document.getElementById("micro-metric-base").innerText = `${microMetrics.baseline_seconds} s (${microMetrics.baseline_steps} steps)`;
    document.getElementById("micro-metric-alert").innerText = `${microMetrics.alert_seconds} s (${microMetrics.alert_steps} steps)`;
    document.getElementById("micro-metric-gain").innerText = `${microMetrics.percentage_gain}% (${microMetrics.time_saved_steps} steps saved)`;

    renderGisRibbon(microGisData, 0);

    microAnimTimer = setInterval(renderMicroNextFrame, 100);
  } catch (err) {
    alert("Backend Microscopic Engine Error: " + err.message);
  } finally {
    isFetching = false;
    setButtonLoading(false);
  }
}

function renderMicroNextFrame() {
  if (isPaused) return;

  if (microCurrentFrame >= microTotalSteps) {
    clearInterval(microAnimTimer);
    document.getElementById("micro-corridor-status").innerText = "Ambulance Reached Destination Gate";
    return;
  }

  const frame = microFrames[microCurrentFrame];
  const N = parseInt(document.getElementById("corridor").value, 10);

  document.getElementById("micro-metric-time").innerText = `${frame.sim_time_sec.toFixed(1)} s`;
  document.getElementById("micro-amb-speed").innerText = `${frame.ambulance.speed.toFixed(2)} seg/s`;
  document.getElementById("micro-amb-pos").innerText = `Position: Seg ${frame.ambulance.position.toFixed(2)} / ${N}`;

  const yieldingCount = frame.vehicles.filter(v => v.yielding).length;
  document.getElementById("micro-yield-count").innerText = `${yieldingCount} vehicles`;

  const lane1 = document.getElementById("micro-lane-1");
  const lane0 = document.getElementById("micro-lane-0");
  const horizonZone = document.getElementById("micro-horizon-zone");

  lane1.querySelectorAll(".micro-veh").forEach(el => el.remove());
  lane0.querySelectorAll(".micro-veh").forEach(el => el.remove());

  const ambEl = document.createElement("div");
  ambEl.className = "micro-veh ambulance";
  ambEl.innerText = "🚑";
  const ambPct = Math.min(96, (frame.ambulance.position / N) * 100);
  ambEl.style.left = `${ambPct}%`;

  if (frame.ambulance.lane === 1) {
    lane1.appendChild(ambEl);
  } else {
    lane0.appendChild(ambEl);
  }

  frame.vehicles.forEach(veh => {
    const vehEl = document.createElement("div");
    let cssClass = "micro-veh";
    if (veh.yielding) {
      cssClass += " civilian-yield";
    } else if (veh.lane === 1) {
      cssClass += " civilian-fast";
    } else {
      cssClass += " civilian-slow";
    }
    vehEl.className = cssClass;
    vehEl.innerText = "🚗";
    vehEl.title = `ID: ${veh.id} | Vel: ${veh.v.toFixed(2)}`;

    const vehPct = Math.min(96, Math.max(0, (veh.x / N) * 100));
    vehEl.style.left = `${vehPct}%`;

    if (veh.lane === 1) {
      lane1.appendChild(vehEl);
    } else {
      lane0.appendChild(vehEl);
    }
  });

  if (frame.alert_window && frame.alert_window.length === 2) {
    const leftPct = (frame.alert_window[0] / N) * 100;
    const rightPct = (frame.alert_window[1] / N) * 100;
    const widthPct = Math.max(0, rightPct - leftPct);
    horizonZone.style.display = "block";
    horizonZone.style.left = `${leftPct}%`;
    horizonZone.style.width = `${widthPct}%`;
  } else {
    horizonZone.style.display = "none";
  }

  renderGisRibbon(microGisData, frame.ambulance.position);

  microCurrentFrame++;
}

// ==================== PHASE 8: V2X & GREEN CORRIDOR ====================
function initV2XCorridorTrack(segmentCount) {
  const track = document.getElementById("v2x-road-track");
  if (!track) return;

  track.innerHTML = '<div class="ambulance-marker alert-active" id="v2x-amb-marker">🚑<div class="v2x-ripple"></div></div>';
  track.style.gridTemplateColumns = `repeat(${segmentCount}, 1fr)`;

  for (let i = 0; i < segmentCount; i++) {
    const seg = document.createElement("div");
    seg.className = "segment";
    seg.id = `v2x-seg-${i}`;
    seg.innerText = i;
    seg.style.backgroundColor = `rgb(${Math.floor(40 + (i / segmentCount) * 160)}, 120, 40)`;
    track.appendChild(seg);
  }
}

async function loadIntersections() {
  try {
    const res = await fetch(API_INTERSECTIONS_URL);
    if (!res.ok) return;
    const data = await res.json();
    intersectionList = data.intersections || [];
    renderTrafficSignalGantries(intersectionList);
  } catch (err) {
    console.warn("Failed to load intersections:", err);
  }
}

function renderTrafficSignalGantries(intersections) {
  const overlay = document.getElementById("v2x-gantries-overlay");
  if (!overlay) return;
  overlay.innerHTML = "";

  const N = parseInt(document.getElementById("corridor").value, 10);

  intersections.forEach(tsc => {
    if (tsc.segment >= N) return;
    const gantry = document.createElement("div");
    gantry.className = "tsc-gantry";
    gantry.id = `gantry-${tsc.id}`;
    
    const pct = ((tsc.segment + 0.5) / N) * 100;
    gantry.style.left = `${pct}%`;

    gantry.innerHTML = `
      <div class="traffic-light" id="light-${tsc.id}">
        <div class="bulb red" id="bulb-red-${tsc.id}"></div>
        <div class="bulb yellow" id="bulb-yellow-${tsc.id}"></div>
        <div class="bulb green active" id="bulb-green-${tsc.id}"></div>
      </div>
      <div class="preempt-flag" id="flag-${tsc.id}">TSC ${tsc.segment}</div>
    `;
    overlay.appendChild(gantry);
  });
}

async function fetchAndStartV2XSimulation() {
  stopAllAnimations();
  isPaused = false;
  document.getElementById("btn-pause").innerText = "Pause";

  const H = parseInt(document.getElementById("horizon").value, 10);
  const alpha = parseFloat(document.getElementById("cooperation").value);
  const N = parseInt(document.getElementById("corridor").value, 10);
  const proto = document.getElementById("v2x-protocol").value;

  initV2XCorridorTrack(N);

  isFetching = true;
  setButtonLoading(true);

  try {
    const res = await fetch(API_V2X_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ corridor_length: N, horizon: H, cooperation: alpha, protocol: proto })
    });

    if (!res.ok) throw new Error("V2X Green Corridor calculation failed");

    const data = await res.json();
    v2xMetrics = data.metrics;
    v2xFrames = data.alert_frames || [];
    v2xTotalSteps = v2xFrames.length;
    v2xCurrentFrame = 0;

    renderTrafficSignalGantries(data.intersections);

    document.getElementById("v2x-metric-base").innerText = `${v2xMetrics.baseline_seconds} s (Delay: ${v2xMetrics.baseline_signal_delay_s}s)`;
    document.getElementById("v2x-metric-alert").innerText = `${v2xMetrics.alert_seconds} s (Delay: ${v2xMetrics.alert_signal_delay_s}s)`;
    document.getElementById("v2x-metric-gain").innerText = `${v2xMetrics.percentage_gain}% (${v2xMetrics.time_saved_seconds}s saved)`;

    document.getElementById("v2x-pdr").innerText = `${v2xMetrics.v2x_pdr_pct}%`;
    document.getElementById("v2x-delay-avoided").innerText = `${(v2xMetrics.baseline_signal_delay_s - v2xMetrics.alert_signal_delay_s).toFixed(1)} s`;
    document.getElementById("v2x-preempt-count").innerText = `${v2xMetrics.preemption_events_triggered} Preemptions Executed`;

    v2xAnimTimer = setInterval(renderV2XNextFrame, 100);
  } catch (err) {
    alert("V2X Backend Simulation Error: " + err.message);
  } finally {
    isFetching = false;
    setButtonLoading(false);
  }
}

function renderV2XNextFrame() {
  if (isPaused) return;

  if (v2xCurrentFrame >= v2xTotalSteps) {
    clearInterval(v2xAnimTimer);
    document.getElementById("v2x-corridor-status").innerText = "Green Wave Complete — Ambulance Cleared All Intersections";
    return;
  }

  const frame = v2xFrames[v2xCurrentFrame];
  const N = parseInt(document.getElementById("corridor").value, 10);

  document.getElementById("v2x-metric-time").innerText = `${frame.sim_time_sec.toFixed(1)} s`;
  document.getElementById("v2x-corridor-status").innerText = `Speed: ${frame.ambulance_speed.toFixed(2)} seg/s | Pos: ${frame.ambulance_pos.toFixed(1)}`;
  
  if (frame.v2x_stats) {
    document.getElementById("v2x-latency").innerText = `${frame.v2x_stats.latency_ms.toFixed(1)} ms`;
    document.getElementById("v2x-proto-active").innerText = `Protocol: ${frame.v2x_stats.active_protocol}`;
    document.getElementById("v2x-packets-count").innerText = `${frame.v2x_stats.packets_sent} sent / ${frame.v2x_stats.packets_received} acked`;
  }

  const ambMarker = document.getElementById("v2x-amb-marker");
  if (ambMarker) {
    const pct = (frame.ambulance_pos / N) * 100;
    ambMarker.style.left = `calc(${pct}% - 13px)`;
  }

  if (frame.intersections) {
    frame.intersections.forEach(tsc => {
      const redBulb = document.getElementById(`bulb-red-${tsc.id}`);
      const yellowBulb = document.getElementById(`bulb-yellow-${tsc.id}`);
      const greenBulb = document.getElementById(`bulb-green-${tsc.id}`);
      const flag = document.getElementById(`flag-${tsc.id}`);

      if (!redBulb || !yellowBulb || !greenBulb) return;

      redBulb.classList.remove("active");
      yellowBulb.classList.remove("active");
      greenBulb.classList.remove("active");

      if (tsc.state === "RED") {
        redBulb.classList.add("active");
      } else if (tsc.state === "YELLOW") {
        yellowBulb.classList.add("active");
      } else if (tsc.state === "GREEN" || tsc.state === "PREEMPTED_GREEN") {
        greenBulb.classList.add("active");
      }

      if (flag) {
        if (tsc.is_preempted) {
          flag.classList.add("active");
          flag.innerText = `⚡ PREEMPTED`;
        } else {
          flag.classList.remove("active");
          flag.innerText = `TSC ${tsc.segment}`;
        }
      }
    });
  }

  v2xCurrentFrame++;
}

// Pause / Resume Toggle
function togglePause() {
  isPaused = !isPaused;
  const btn = document.getElementById("btn-pause");
  btn.innerText = isPaused ? "Resume" : "Pause";
}

// Event Listeners for parameter inputs
document.getElementById("corridor").addEventListener("change", (e) => {
  const newN = parseInt(e.target.value, 10);
  if (activeTab === "macro") initRoadTrack(newN);
  else if (activeTab === "v2x") initV2XCorridorTrack(newN);
});

// Initial Boot
window.onload = () => {
  initRoadTrack(20);
  initChart();
  loadGisWaypoints();
};

// Expose handlers to window for inline onclick attributes
window.switchTab = switchTab;
window.startActiveSimulation = startActiveSimulation;
window.togglePause = togglePause;
