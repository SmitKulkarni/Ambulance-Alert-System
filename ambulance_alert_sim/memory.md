# Long-Term Project Memory

This document stores comprehensive persistent project context, business logic equations, completed features, known behaviors, and technical references for AI assistants.

---

## 1. Project Overview

The **Advance Ambulance-Alert Corridor Simulator** is an Intelligent Transportation Systems (ITS) simulation platform that models emergency vehicle transit through a congested 1D road corridor. It evaluates the impact of broadcasting advance digital alerts to upcoming drivers, allowing them to yield and clear the travel path before the ambulance arrives.

---

## 2. Technology Stack & Decoupled Architecture

| Layer | Subfolder | Technologies | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend & Engine** | `backend/` | Python 3.10+, FastAPI, Uvicorn, NumPy, Pydantic, Dotenv | Mathematical simulation, REST APIs, JSON timeline streaming, acoustic detection |
| **Backend Testing** | `backend/tests/` | Pytest, AnyIO | 36 automated invariant verification tests across all simulation models |
| **Frontend** | `frontend/` | Vite 6, HTML5, Vanilla CSS, ES6 JavaScript, Chart.js | Modern decoupled dashboard, real-time animation, multi-aspect signal display |
| **Standalones & Guides** | `frontend/public/` | Canvas, Web Audio API, PDF | 4-way intersection preemption visualizer, printable implementation guides |
| **Unity 3D Suite** | `unity_scripts/` | C# Unity Engine | 3D TrafficSignalController, AutomaticEmergencyDetector, Doppler siren audio |
| **Root Workspace** | Project Root | Node.js, Concurrently | Single-command startup (`npm start`) to run frontend & backend simultaneously |

---

## 3. Features Completed

- [x] **Core Physics Engine ([`backend/simulator.py`](file:///d:/Aarya%20Kulkarni%20Project/ambulance_alert_sim/backend/simulator.py), [`simulator.py`](file:///d:/Aarya%20Kulkarni%20Project/ambulance_alert_sim/simulator.py)):**
  - Linear base traffic density ramp: $\rho_{base} \in [0.2, 0.8]$ over $N=20$ segments.
  - Driver yielding clearance logic: $\rho_{eff}[i] = \rho_{base}[i] \cdot (1 - \alpha)$ over horizon $[pos+1, pos+1+H]$.
  - Speed transfer law: $v = v_{max} \cdot (1 - \rho_{eff}[next\_idx])$, linking velocity to upcoming road resistance.
- [x] **Decoupled FastAPI Backend ([`backend/app.py`](file:///d:/Aarya%20Kulkarni%20Project/ambulance_alert_sim/backend/app.py)):**
  - `GET /api/health`: Health monitoring endpoint.
  - `POST /api/simulate`: High-performance simulation execution returning baseline vs. alert metrics and frame-by-frame snapshot timelines.
  - CORS middleware enabled for local cross-origin frontend communication.
- [x] **Modern Web Dashboard ([`frontend/`](file:///d:/Aarya%20Kulkarni%20Project/ambulance_alert_sim/frontend/)):**
  - Real-time animated road tracks rendering dual ambulances (🚑) across discrete road segments.
  - Dynamic segment color transitions (green clearing highlights vs. deep red congestion).
  - Synchronized real-time Chart.js trajectory curve rendering.
  - Parameter controls for $H$, $\alpha$, and $N$ with run/pause/resume functionality.
- [x] **Interactive Desktop Visualizer ([`visual_simulator.py`](file:///d:/Aarya%20Kulkarni%20Project/ambulance_alert_sim/visual_simulator.py)):**
  - Dual-pane Matplotlib animation window visualizing live road clearing and trajectory curves simultaneously.
- [x] **Automated Invariant Test Suite ([`test_simulator.py`](file:///d:/Aarya%20Kulkarni%20Project/ambulance_alert_sim/test_simulator.py)):**
  - 11 unit tests verifying density bounds, lookahead clearing, parameter validation, clipping, float safety, and boundary edge cases.
- [x] **Parametric Experimentation Suite ([`experiments.py`](file:///d:/Aarya%20Kulkarni%20Project/ambulance_alert_sim/experiments.py)):**
  - Automated parameter sweeps for $H \in [0, 5]$ and $\alpha \in [0.0, 1.0]$.
  - Exports structured CSV data: `results/results_H.csv`, `results/results_alpha.csv`.
  - Generates publication-ready plots: `plots/time_saved_vs_H.png`, `plots/time_saved_vs_alpha.png`.
- [x] **Academic Deliverables & Documentation:**
  - `report/project_report.pdf`: Formatted 4-page technical project report.
  - `report/presentation.pptx`: 6-slide presentation deck.
  - `report/viva_notes.txt`: 1-page viva voce defense speaking cheatsheet.
  - `project_guide.html`: Printable single-document comprehensive guide with print CSS.
  - `demo_notebook.ipynb`: 4-cell Jupyter notebook with pre-rendered results.
- [x] **Microscopic IDM & GIS Corridor Engine (Phase 7):**
  - Discrete vehicle longitudinal dynamics governed by the Intelligent Driver Model (IDM).
  - Lateral emergency yielding: Vehicles in Lane 1 within alert horizon $H$ yield to Lane 0 based on cooperation factor $\alpha$.
  - GIS arterial route with 6 realistic waypoints from Metro Hub to City Memorial Hospital.
  - Interactive dual-tab UI with live 2D multi-lane canvas and real-time GIS tracking ribbon.
  - Dedicated unit tests in `test_micro_simulator.py` (6 unit tests).
- [x] **Connected Vehicle V2X & Green Corridor Preemption (Phase 8):**
  - Wireless V2X channel modeling with distance-decay shadow fading ($P_{loss}(d)$) for 5G C-V2X (Release 16+ NR-V2X) and DSRC 5.9GHz.
  - Municipal Traffic Signal Controllers (TSCs) with automated emergency `PREEMPTED_GREEN` green wave triggering.
  - Interactive Phase 8 UI tab with live 3-bulb traffic light gantries, preemption badge pulses, and V2X wavefront animation ripples.
  - Dedicated unit tests in `test_v2x_simulator.py` (6 unit tests, total 23 repository-wide tests passing).

---

## 4. Pending & Optional Features

- [ ] **Bidirectional WebSocket Streaming:** Streaming simulation ticks over WebSockets rather than HTTP batch payload.
- [ ] **SUMO / TraCI Full Network Integration:** Connecting the backend to open-source SUMO simulation via TraCI sockets.



---

## 5. API Endpoints Specification

### `GET /api/health`
- **Description:** Basic service health status.
- **Response:**
  ```json
  {
    "status": "operational",
    "system": "Ambulance Alert Engine"
  }
  ```

### `POST /api/simulate`
- **Description:** Runs the numerical simulation for both baseline and alert scenarios and returns summaries and step timelines.
- **Request Body (`SimulationRequest`):**
  ```json
  {
    "corridor_length": 20,
    "horizon": 3,
    "cooperation": 0.5
  }
  ```
- **Response:**
  ```json
  {
    "parameters": {
      "corridor_length": 20,
      "horizon": 3,
      "cooperation": 0.5
    },
    "summary": {
      "baseline_time_steps": 45,
      "alert_time_steps": 26,
      "time_saved_steps": 19,
      "improvement_percentage": 42.22
    },
    "timeline": {
      "baseline": [
        { "step": 0, "position": 0.0, "density": [...], "speed": 0.768 },
        ...
      ],
      "alert": [
        { "step": 0, "position": 0.0, "density": [...], "speed": 0.884 },
        ...
      ]
    }
  }
  ```

### `GET /api/gis-corridor`
- **Description:** Returns the real-world arterial GIS route nodes, geographic coordinates, and landmark descriptions.
- **Response:**
  ```json
  {
    "waypoints": [
      { "segment": 0, "lat": 18.5204, "lon": 73.8567, "name": "Corridor Entrance (Metro Hub)" },
      ...
      { "segment": 19, "lat": 18.5395, "lon": 73.8770, "name": "City Memorial Hospital Emergency Gate" }
    ],
    "total_segments": 20
  }
  ```

### `POST /api/simulate-micro`
- **Description:** Executes microscopic multi-lane simulation using the Intelligent Driver Model (IDM) and lateral emergency yielding.
- **Request Body (`MicroSimulationRequest`):**
  ```json
  {
    "corridor_length": 20,
    "horizon": 3,
    "cooperation": 0.5
  }
  ```
- **Response:**
  ```json
  {
    "status": "success",
    "metrics": {
      "baseline_steps": 140,
      "alert_steps": 130,
      "time_saved_steps": 10,
      "percentage_gain": 7.14,
      "baseline_seconds": 70.0,
      "alert_seconds": 65.0
    },
    "gis_corridor": [...],
    "alert_frames": [
      {
        "step": 0,
        "sim_time_sec": 0.0,
        "ambulance": { "position": 0.0, "speed": 0.6, "lane": 1 },
        "vehicles": [ { "id": "car_0", "x": 2.0, "v": 0.66, "lane": 1, "yielding": false }, ... ],
        "alert_window": [1, 3]
      }
    ]
  }
  ```

### `GET /api/intersections`
- **Description:** Returns the municipal traffic signal controller locations and V2X wireless protocol parameters.
- **Response:**
  ```json
  {
    "intersections": [
      { "id": "tsc_0", "segment": 4, "name": "Arterial Junction A (4th Ave)", "cycle_time": 60, "green_time": 25 },
      ...
    ],
    "protocols": { "cv2x_5g": {...}, "dsrc": {...} }
  }
  ```

### `POST /api/simulate-v2x`
- **Description:** Simulates Connected Vehicle V2X communication (5G / DSRC) coupled with automated Traffic Signal Preemption ("Green Corridor").
- **Request Body (`V2XSimulationRequest`):**
  ```json
  {
    "corridor_length": 20,
    "horizon": 3,
    "cooperation": 0.5,
    "protocol": "cv2x_5g"
  }
  ```
- **Response:**
  ```json
  {
    "metrics": {
      "baseline_seconds": 38.0,
      "alert_seconds": 23.0,
      "time_saved_seconds": 15.0,
      "percentage_gain": 39.47,
      "baseline_signal_delay_s": 2.0,
      "alert_signal_delay_s": 0.0,
      "preemption_events_triggered": 4,
      "v2x_pdr_pct": 95.6
    },
    "intersections": [...],
    "alert_frames": [...]
  }
  ```

---



## 6. Data Storage & Persistence Summary

*Note: The project operates without an SQL/NoSQL database to maintain lightweight portability.*
- **Structured Metrics Storage:**
  - `results/results_H.csv`: Comma-separated values for alert horizon sweeps.
  - `results/results_alpha.csv`: Comma-separated values for cooperation sweeps.
  - `results/summary.txt`: Plain text tabular summaries.
- **Plot Image Storage:**
  - `plots/ambulance_comparison.png`
  - `plots/time_saved_vs_H.png`
  - `plots/time_saved_vs_alpha.png`
  - `plots/corridor_diagram.png`

---

## 7. Important Mathematical & Business Logic

1. **Base Density Ramp:**
   $$\rho_{base}[i] = 0.2 + (0.8 - 0.2) \cdot \frac{i}{N - 1}, \quad i \in [0, N-1]$$
2. **Effective Density Modification:**
   $$\rho_{eff}[i] = \rho_{base}[i] \cdot (1 - \alpha), \quad \forall i \in [pos + 1, \min(pos + 1 + H, N - 1)]$$
3. **Ambulance Velocity Model:**
   $$v = v_{max} \cdot (1 - \text{clip}(\rho_{eff}[next\_idx], 0.0, 1.0))$$
   where $next\_idx = \min(\lfloor pos \rfloor + 1, N - 1)$.
4. **Time Step Progression:**
   $$pos_{t+1} = pos_t + v_t$$
   $$\text{Terminates when } pos \ge N - 1 \text{ or } t \ge T_{max}$$

---

## 8. Verified Experimental Results Reference

- **Baseline Travel Time ($No Alert$):** 45 time steps
- **With Advance Alert ($H=3, \alpha=0.5$):** 26 time steps
- **Net Time Saved:** 19 time steps (**42.22% reduction**)
- **Horizon Sensitivity ($H \in [0, 5]$):**
  - $H=0 \implies 45$ steps (0 saved)
  - $H \ge 1 \implies 26$ steps (19 saved)
- **Cooperation Sensitivity ($\alpha \in [0.0, 1.0]$):**
  - $\alpha = 0.0 \implies 45$ steps (0 saved)
  - $\alpha = 0.2 \implies 34$ steps (11 saved)
  - $\alpha = 0.4 \implies 28$ steps (17 saved)
  - $\alpha = 0.6 \implies 24$ steps (21 saved)
  - $\alpha = 0.8 \implies 22$ steps (23 saved)
  - $\alpha = 1.0 \implies 19$ steps (26 saved, 57.8% speedup)
