# Project Governance & Development Rules

This document specifies mandatory development rules, style conventions, and architectural constraints that any AI or human contributor must strictly adhere to when modifying this repository.

---

## 1. General Directives & Principles

1. **Preserve Existing Invariants:** Never break existing working endpoints, numerical equations, or CLI tools unless explicitly requested by the user.
2. **Backward Compatibility:** All new features (e.g., REST API, web dashboards) must coexist alongside existing CLI scripts (`main.py`, `experiments.py`, `test_simulator.py`).
3. **No Placeholders:** Never commit `TODO` comments, placeholder variables, or simulated outputs when actual computations can be executed.
4. **Self-Contained Execution:** Avoid introducing external runtime binary dependencies that require complex manual installation beyond `pip install -r requirements.txt`.

---

## 2. Directory Structure & Encapsulation Rules

All project source files and deliverables must reside inside the project structure without polluting parent directories:

```
ambulance_alert_sim/
├── backend/                  # FastAPI REST API & core simulation engine
├── frontend/                 # Decoupled web dashboard (HTML, CSS, JS)
├── plots/                    # Generated charts & visual outputs (PNG, 150 DPI)
├── results/                  # Generated CSV datasets & text summaries
├── report/                   # Submission PDF reports, PPTX decks & viva notes
├── .venv/                    # Isolated Python virtual environment
├── decisions.md              # Architectural Decision Records (ADR)
├── rules.md                  # Project rules & constraints (this file)
├── memory.md                 # Long-term AI context & architectural memory
├── changelog.md              # Versioned changelog history
├── requirements.txt          # Pinned Python package dependencies
└── README.md                 # Root onboarding & usage documentation
```

### Path Resolution Rules
- Never use relative string literals like `"plots/image.png"` directly without resolving them via `os.path.dirname(os.path.abspath(__file__))`.
- Always verify parent directory existence via `os.makedirs(target_dir, exist_ok=True)` before calling file write or `plt.savefig` operations.

---

## 3. Coding Standards & Naming Conventions

### Python Code (`backend/`, `*.py`)
- **PEP 8 Compliance:** 4 spaces indentation, max line length 100 characters where practical.
- **Naming Conventions:**
  - Modules and functions: `snake_case` (e.g., `effective_density_with_alert()`, `simulate_step_history()`).
  - Constants & Config variables: `UPPER_SNAKE_CASE` or baseline globals (e.g., `N`, `v_max`, `H_default`, `T_max`).
  - Pydantic Models / Classes: `PascalCase` (e.g., `SimulationRequest`, `NumberedCanvas`).
- **Type Annotations:** Function signatures must use Python 3 type hints (`int`, `float`, `np.ndarray`, `bool`, `list`).
- **Defensive Bounds Checking:** Always validate parameter boundaries ($H \ge 0$, $0.0 \le \alpha \le 1.0$, corridor length $N \ge 2$) before initiating numerical loops.

### Frontend Code (`frontend/`, `*.js`, `*.css`, `*.html`)
- **Modern JavaScript:** Use ES6+ syntax (`const`/`let`, arrow functions, `async/await`, template literals).
- **Naming Conventions:**
  - Variables & Functions: `camelCase` (e.g., `fetchAndStartSimulation()`, `stepSimulation()`).
  - DOM IDs & Classes: `kebab-case` (e.g., `metric-step`, `track-alert`, `btn-primary`).
  - CSS Custom Properties: `--kebab-case` (e.g., `--bg-main`, `--accent-blue`).
- **Zero-Dependency Core:** The frontend dashboard must not require a Node.js build pipeline or npm bundler; load Chart.js via CDN or local vendor files.

---

## 4. UI/UX Consistency Rules

1. **Color Palette System:**
   - Backgrounds: Dark slate tones (`#0b1120`, `#0f172a`, `#1e293b`).
   - Alerts / Speedup: Cyan / Emerald Green (`#38bdf8`, `#10b981`, `#22c55e`).
   - Baseline / Congestion: Crimson / Red (`#ef4444`, `#dc2626`).
   - Borders: Dark slate borders (`#334155`).
2. **Accessible Contrast:** Text on cards must maintain high contrast (e.g., `#f8fafc` for titles, `#94a3b8` for muted subtitles).
3. **Responsive Visuals:** Grids must collapse gracefully on mobile/tablet viewports using `repeat(auto-fit, minmax(..., 1fr))`.
4. **Animation Performance:** Keep UI tick intervals between 60ms and 100ms; avoid triggering heavy layout recalcs inside animation callbacks.

---

## 5. Testing & Quality Assurance Rules

1. **Mandatory Invariant Verification:**
   Before marking any implementation complete, run the automated test suite:
   ```bash
   pytest -v test_simulator.py
   ```
   All tests must pass with 100% success.
2. **Coverage Invariants:**
   - Any new simulator function must have a corresponding test verifying boundary limits, parameter validation, and expected time savings.
3. **Deterministic Outputs:**
   - The simulation must remain strictly deterministic given constant seeds and parameters ($N, H, \alpha$).

---

## 6. Git Commit & Version Control Rules

1. **Conventional Commits Format:**
   - `feat: <description>` for new features or endpoints.
   - `fix: <description>` for bug or mathematical fixes.
   - `test: <description>` for unit tests and verification scripts.
   - `docs: <description>` for updates to documentation, reports, or guides.
   - `refactor: <description>` for code cleanup without behavior change.
2. **Never Commit Artifact Cache:**
   - Ignore `__pycache__/`, `.pytest_cache/`, `.venv/`, and `.DS_Store`.

---

## 7. Security & API Rules

1. **Input Validation:** All FastAPI endpoints accepting request bodies must validate ranges using Pydantic `Field(ge=..., le=...)` to prevent denial-of-service via huge loops (e.g., $N \le 100$, $H \le 20$).
2. **CORS Governance:** Maintain explicit CORS headers for local decoupled dashboard communication.
3. **Error Responses:** Raise explicit `HTTPException(status_code=400, detail=...)` on invalid numerical parameters with human-readable error messages.
