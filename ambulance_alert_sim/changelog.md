# Project Changelog

All notable changes, bug fixes, architectural enhancements, and deliverable additions for the **Advance Ambulance-Alert Corridor Simulator** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.1] - 2026-10-09

### Fixed
- **Intersection Simulation Canvas & Signal Rendering Restoration:**
  - Resolved fatal unhandled JavaScript exception (`TypeError: Cannot set properties of null (setting 'innerText')`) in `intersection_simulation.html` animation `update()` loop caused by missing telemetry elements.
  - Implemented null-safe helper `setElemText(id, text, className)` ensuring missing DOM nodes never crash the 60 FPS animation/render loop.
  - Restored telemetry DOM elements (`tele-mode`, `tele-dist`, `tele-phase`, `tele-hold-countdown`, `tele-blue-dir`, `tele-warning-sound`, `tele-stopped`).
  - Synchronized `intersection_simulation.html` between project root and `frontend/public/intersection_simulation.html`.
  - Added explicit window binding in `frontend/src/app.js` (`window.switchTab`, `window.startActiveSimulation`, `window.togglePause`) to resolve Vite module scoping issues with inline `onclick` handlers.
  - Added service worker unregistration in `frontend/index.html` to eliminate stale cached shell responses from other local services.
  - Verified canvas rendering: animated 4-approach road grid, 4-aspect signal heads (including 4th color BLUE for emergency approach and RED for others), civilian cars stopping behind stop lines, siren Doppler audio, cross-traffic warning buzzer/horns, and live telemetry ribbons.

## [2.3.0] - 2026-10-09

### Added & Refactored
- **Complete Frontend and Backend Decoupled Subfolder Architecture:**
  - `frontend/`: Standalone Vite project containing `src/` (`app.js`, `style.css`), `public/` (simulation visualizers and technical guides), `index.html`, independent `package.json`, `vite.config.js`, and `frontend/.env`.
  - `backend/`: Standalone FastAPI service containing `src/` (`app.py`, `simulator.py`, `micro_simulator.py`, `v2x_simulator.py`, `acoustic_detector.py`), `tests/` (`test_*.py`), independent `package.json`, `requirements.txt`, and `backend/.env`.
  - **Isolated Environment Variables**: `frontend/.env` (`VITE_API_BASE_URL`) and `backend/.env` (`HOST`, `PORT`, `CORS_ORIGINS`).
  - **Root Workspace Scripts**: Root `package.json` with `concurrently` enabling single-command startup (`npm start`) to run both servers concurrently.
  - **Test Suite Integration**: All 36 unit tests pass from backend root via `npm test` or `pytest tests/`.
  - `decisions.md`: Added ADR-012 (Complete Decoupled Subfolder Architecture).

---

## [2.2.0] - 2026-10-09

### Added
- **Phase 8: Connected Vehicle V2X & Green Corridor Preemption:**
  - `backend/v2x_simulator.py`: Implemented distance-dependent shadow fading wireless channel model ($P_{loss}(d)$) for 5G C-V2X and DSRC 5.9GHz, and municipal Traffic Signal Controllers (TSCs) with automated emergency `PREEMPTED_GREEN` green wave triggering.
  - `test_v2x_simulator.py`: Dedicated unit test suite verifying log-distance packet loss decay, TSC 3-bulb cycle state transitions, emergency preemption override, and travel-time savings (6/6 tests passing).
  - `GET /api/intersections`: Endpoint exposing municipal traffic signal controller locations and V2X wireless protocols.
  - `POST /api/simulate-v2x`: Endpoint calculating V2X communication delivery ratios, latency jitter, signal wait delays, and corridor arrival metrics.
  - `frontend/index.html` & `frontend/style.css` & `frontend/app.js`: Added 3rd dedicated dashboard view for Phase 8 featuring 4 active traffic signal gantries, live `⚡ PREEMPTED` badges, animated V2X broadcast wavefront ripples, protocol dropdown selector (5G C-V2X vs DSRC), and real-time PDR/latency telemetry.
  - `phase.md`: Marked Phase 8 as `✅ Completed` in the implementation lifecycle matrix.
  - `decisions.md`: Added ADR-008 (V2X Protocol & Distance-Dependent Shadowing) and ADR-009 (Traffic Signal Preemption State Machine).
- **Emergency Vehicle Traffic Signal Preemption (EVTSP) Unity & Web Suite:**
  - `unity_scripts/TrafficSignalController.cs`: 4-way intersection controller with phase snapshot caching and HDR emission bloom.
  - `unity_scripts/AmbulanceVehicle.cs`: Kinematics controller with 3D logarithmic audio rolloff and Doppler siren synthesis.
  - `unity_scripts/IntersectionTrigger.cs`: Arrival and departure collider triggers for emergency preemption.
  - `intersection_simulation.html`: Standalone interactive HTML5/Canvas 4-way intersection simulation with synthesized Web Audio Doppler siren and dynamic signal overrides.
  - **All-Signals-Stop & Sole-Approach-Green Override Rule**: Hardened preemption logic in both JavaScript and Unity C# controllers (`getSigColor`, `dispatchAmbulance`, `TriggerEmergencyPreemption`) ensuring *all competing signals immediately turn Solid Red (`#ef4444`)* and *only the arriving ambulance's direction turns Emergency Green (`#00ff88`)*, complete with civilian cross-traffic halting behind white stop lines and visual `STOP` badges.
  - **Extended Ambulance Signal Hold Duration & Steady Pace Controls**: Added adjustable hold window slider (8s to 30s, default 16s), steady ambulance pacing (1.4 px/f), on-canvas real-time priority hold countdown ribbon (`⏱️ PRIORITY HOLD: XX.Xs REMAINING`), and post-clearance safety buffer preventing cross-traffic from prematurely entering the intersection.
  - `traffic_signal_preemption_guide.html`: Printable 5-page implementation guide with `@page { size: A4; }` styling.
  - `report/traffic_signal_preemption_guide.pdf`: Exact 5-page publication-grade PDF manual.
  - `decisions.md`: Added ADR-010 (EVTSP State Memory Cache & Unity 3D Architecture).

---

## [2.1.0] - 2026-10-09


### Added
- **Phase 7: Microscopic IDM Traffic Simulation & GIS Integration:**
  - `backend/micro_simulator.py`: Implemented discrete vehicle car-following via the Intelligent Driver Model (IDM) and lateral emergency yielding (Lane 1 clearing into Lane 0).
  - `test_micro_simulator.py`: Dedicated unit test suite validating IDM acceleration laws, bumper headways, corridor completion, and GIS waypoint integrity (6/6 tests passing).
  - `GET /api/gis-corridor`: Endpoint exposing the 6-node arterial transit corridor from Metro Hub to City Memorial Hospital.
  - `POST /api/simulate-micro`: Endpoint calculating microscopic simulation frames and comparative metrics.
  - `frontend/index.html` & `frontend/style.css` & `frontend/app.js`: Interactive dual-mode dashboard adding a dedicated "Microscopic Multi-Lane & GIS (Phase 7)" view with dynamic cars (🚗), flashing yielding states, emergency ambulance sirens, and real-time GIS route ribbon tracking.
  - `phase.md`: Marked Phase 7 as `✅ Completed` in the implementation lifecycle matrix.
  - `decisions.md`: Added ADR-006 (Microscopic IDM Dynamics) and ADR-007 (Lateral Lane Clearing & GIS Mapping).

---

## [2.0.0] - 2026-10-09


### Added
- **Decoupled Architecture (`backend/` & `frontend/`):**
  - `backend/app.py`: FastAPI application serving REST endpoints (`/api/health`, `/api/simulate`) with CORS middleware.
  - `backend/config.py`: Centralized configuration constants for the API service.
  - `backend/simulator.py`: High-performance timeline simulation engine returning frame-by-frame snapshot states.
  - `frontend/index.html`: Responsive dark-themed control dashboard with interactive parameters, dual road tracks, and Chart.js integration.
  - `frontend/style.css`: Modern visual design system with custom CSS properties, responsive grid layouts, and animated ambulance markers.
  - `frontend/app.js`: Asynchronous fetch client and client-side animation loop updating corridor segments and trajectory curves.
- **Persistent AI Context Documentation:**
  - `decisions.md`: Architectural Decision Records (ADRs) covering forward lookahead velocity coupling, safe integer slicing, decoupled architecture, and timeline streaming.
  - `rules.md`: Comprehensive development rules, naming conventions, coding standards, and testing protocols.
  - `memory.md`: Long-term technical context, mathematical models, API schemas, and experimental benchmarks.
  - `changelog.md`: Chronological history of all project iterations.

### Changed
- Updated `requirements.txt` to include `fastapi`, `uvicorn[standard]`, and `pydantic`.
- Replaced monolithic simulation execution with decoupled client-server interaction while preserving standalone script capabilities.

---

## [1.2.0] - 2026-10-08

### Added
- **Real-Time 2D Animated Corridor Visualizer (`visual_simulator.py`):**
  - Dual-pane Matplotlib animation window using `matplotlib.animation.FuncAnimation`.
  - Top Road Visualizer showing live ambulance markers (🚑) gliding over segments with dynamic color transitions.
  - Bottom Progress Graph dynamically plotting continuous displacement curves side by side.
- **Standalone Web Visualizer (`index.html`):**
  - Zero-dependency single-file HTML/CSS/JS simulation with real-time DOM element animation and print styling.
- **Printable Single-Document Comprehensive Guide (`project_guide.html`):**
  - Complete technical implementation guide with `@page { size: A4; }` print styles.

### Changed
- Standardized all script paths using script-relative anchors (`os.path.dirname(os.path.abspath(__file__))`) to prevent directory pollution.

---

## [1.1.0] - 2026-10-08

### Fixed
- **Kinematic Lookahead Coupling Bug:**
  - Resolved the zero-time-saved disconnect where ambulance velocity was queried against the current segment `rho_eff[idx]` instead of the upcoming segment `rho_eff[next_idx]`.
  - Validated that alerted drivers clearing ahead physically reduce road resistance, yielding **42.22% time reduction** (saving 19 time steps).
- **Float Horizon Slice `TypeError`:**
  - Enforced `int(H)` casting in `effective_density_with_alert()` to prevent slicing exceptions when float horizons are passed.
- **Hardcoded Test Constants:**
  - Updated assertions in `test_simulator.py` to reference `N` and `T_max` from `config.py` rather than hardcoded magic numbers.

### Added
- **Automated Invariant Test Suite (`test_simulator.py`):**
  - Expanded unit test suite from 5 to 11 test cases covering boundary densities, parameter validation errors, float safety, zero-horizon invariants, speed clipping, and short-array guards.
- **CSV Data Exporters (`experiments.py`):**
  - Added structured CSV exports: `results/results_H.csv` and `results/results_alpha.csv`.
- **Academic Project Deliverables:**
  - `report/project_report.pdf`: Exact 4-page academic submission report with measured experimental statistics.
  - `report/presentation.pptx`: 6-slide presentation deck formatted in 16:9 widescreen.
  - `report/viva_notes.txt`: 1-page viva voce defense speaking cheatsheet.

---

## [1.0.0] - 2026-10-08

### Added
- Initial project prototype based on 3-member team role split (Member A = Simulation Core, Member B = Experiments & Plots, Member C = Demo & Viva).
- `config.py`: Core simulation parameters ($N=20, v_{max}=1.0, H=3, \alpha=0.5, T_{max}=200$).
- `simulator.py`: Density generation, speed model, and simulation functions.
- `main.py`: Baseline vs. alert comparison script generating `plots/ambulance_comparison.png`.
- `experiments.py`: Parametric sweep script generating `plots/time_saved_vs_H.png`, `plots/time_saved_vs_alpha.png`, and `results/summary.txt`.
- `demo_notebook.ipynb`: 4-cell Jupyter notebook demo.
