# Advance Ambulance-Alert Corridor Simulator

An Intelligent Transportation Systems (ITS) simulation project modeling emergency vehicle progression through a congested traffic corridor with advance driver awareness, Intelligent Driver Model (IDM) car-following, Connected Vehicle (V2X) Traffic Signal Preemption, and Directional Acoustic Siren Detection.

---

## 1. Project Overview & Architecture

The project is structured into fully decoupled **Frontend** and **Backend** subfolders, each with its own independent dependencies, configuration, environment variables, and execution lifecycles:

```
ambulance_alert_sim/
│
├── frontend/                              # Client-side user interface & simulation views
│   ├── src/
│   │   ├── app.js                         # Asynchronous client, animation loops & telemetry
│   │   └── style.css                      # Modern dark-mode styling & responsive grid layout
│   ├── public/
│   │   ├── intersection_simulation.html   # Standalone 4-Way intersection preemption visualizer
│   │   ├── project_guide.html             # Printable project documentation & formula manual
│   │   └── traffic_signal_preemption_guide.html # EVTSP Unity architecture & defense guide
│   ├── index.html                         # Entry HTML file
│   ├── package.json                       # Independent frontend dependencies (Vite)
│   ├── vite.config.js                     # Vite dev server & API proxy configuration
│   └── .env                               # Frontend environment variables (VITE_API_BASE_URL)
│
├── backend/                               # REST & computational simulation engine
│   ├── src/
│   │   ├── __init__.py
│   │   ├── app.py                         # FastAPI REST service & CORS middleware
│   │   ├── config.py                      # Simulation constants & hyperparameters
│   │   ├── simulator.py                   # Macroscopic 1D continuum simulation engine
│   │   ├── micro_simulator.py             # Microscopic IDM discrete car-following engine
│   │   ├── v2x_simulator.py               # 5G C-V2X / DSRC channel fading & TSC controllers
│   │   └── acoustic_detector.py           # Directional microphone array siren approach detector
│   ├── tests/
│   │   ├── conftest.py                    # Pytest environment & sys.path configuration
│   │   ├── test_simulator.py              # Macroscopic continuum unit tests
│   │   ├── test_micro_simulator.py        # Microscopic IDM unit tests
│   │   ├── test_v2x_simulator.py          # V2X shadow fading & preemption unit tests
│   │   ├── test_edge_cases.py             # Boundary condition unit tests
│   │   └── test_acoustic_detector.py      # Acoustic DoA & decibel gradient unit tests
│   ├── requirements.txt                   # Python dependencies (FastAPI, uvicorn, numpy, etc.)
│   ├── package.json                       # Independent backend npm scripts
│   └── .env                               # Backend environment variables (HOST, PORT)
│
├── unity_scripts/                         # Unity 3D C# codebase for 3D simulations
│   ├── TrafficSignalController.cs         # 4-aspect signal controller with 4th color BLUE
│   ├── AutomaticEmergencyDetector.cs      # Directional acoustic sensor scanning script
│   ├── AmbulanceVehicle.cs                # Kinematics controller with Doppler audio rolloff
│   └── IntersectionTrigger.cs             # Arrival & departure preemption colliders
│
├── package.json                           # Root scripts for running frontend + backend together
├── .gitignore                             # Git ignore rules for node_modules, .venv, caches
└── README.md                              # This documentation file
```

---

## 2. Prerequisites

Ensure you have the following installed on your system:
- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher
- **Python**: v3.10.0 or higher
- **pip**: v23.0.0 or higher

---

## 3. Installation Instructions

### Step 1: Install Backend Dependencies
Open your terminal in the `backend/` directory:
```bash
cd backend
pip install -r requirements.txt
```
*(Optional: Use a Python virtual environment)*
```bash
python -m venv .venv
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Install Frontend Dependencies
Open your terminal in the `frontend/` directory:
```bash
cd frontend
npm install
```

### Step 3: Install Root Workspace Dependencies (Optional - for running concurrently)
In the project root:
```bash
npm install
```

---

## 4. Running the Application

### Option A: Running Both Frontend & Backend Together (Recommended)
From the project root:
```bash
npm start
```
*This uses `concurrently` to start both the FastAPI backend on `http://127.0.0.1:8000` and the Vite frontend on `http://localhost:3000` simultaneously.*

---

### Option B: Running Separately in Independent Terminals

#### 1. Starting the Backend:
```bash
cd backend
npm start
# OR directly via uvicorn:
python -m uvicorn src.app:app --host 127.0.0.1 --port 8000 --reload
```
- **Backend API**: `http://127.0.0.1:8000`
- **Interactive OpenAPI Docs**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/api/health`

#### 2. Starting the Frontend:
```bash
cd frontend
npm run dev
```
- **Frontend Dashboard**: `http://localhost:3000`
- **4-Way Intersection Simulator**: `http://localhost:3000/intersection_simulation.html`
- **EVTSP Implementation Guide**: `http://localhost:3000/traffic_signal_preemption_guide.html`

---

## 5. Environment Variables Configuration

Both environments maintain dedicated `.env` configuration files:

### Frontend Environment (`frontend/.env`):
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
PORT=3000
```

### Backend Environment (`backend/.env`):
```env
HOST=127.0.0.1
PORT=8000
ENVIRONMENT=development
CORS_ORIGINS=*
SIREN_DETECTION_THRESHOLD_DB=75.0
```

---

## 6. Running the Automated Test Suite

All 36 unit tests cover macroscopic continuum physics, microscopic IDM car-following, V2X packet loss, and acoustic directional siren detection:

```bash
cd backend
npm test
# OR directly via pytest:
pytest tests/
```

**Test Suite Coverage Summary:**
- `test_simulator.py`: 11 tests passing (density gradients, velocity models, horizon limits)
- `test_micro_simulator.py`: 6 tests passing (IDM acceleration, lateral yielding, GIS pathing)
- `test_v2x_simulator.py`: 6 tests passing (shadow fading, packet delivery ratio, TSC preemption)
- `test_edge_cases.py`: 7 tests passing (extreme alpha, zero horizon, boundary values)
- `test_acoustic_detector.py`: 6 tests passing (directional microphone DoA, sound decay, 4-aspect signal states)
- **Total: 36 / 36 unit tests passing (100% pass rate)**

---

## 7. API Endpoint Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status and version identifier |
| `GET` | `/api/intersections` | Municipal traffic signal controllers & V2X protocol specs |
| `GET` | `/api/gis-corridor` | Arterial GIS GPS route coordinates & landmarks |
| `POST` | `/api/simulate` | Macroscopic 1D traffic density timeline engine |
| `POST` | `/api/simulate-micro` | Microscopic IDM vehicle trajectory & lateral lane yielding |
| `POST` | `/api/simulate-v2x` | 5G C-V2X vs DSRC communication & green corridor preemption |
| `POST` | `/api/detect-emergency-approach` | Acoustic sensor array directional approach identification |
