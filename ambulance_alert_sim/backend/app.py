# backend/src/app.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from .simulator import simulate_step_history, get_base_density
    from .micro_simulator import run_microscopic_comparison, GIS_WAYPOINTS
    from .v2x_simulator import run_v2x_comparison, DEFAULT_INTERSECTIONS, V2X_PROTOCOLS
    from .config import N, H_default, alpha_default
    from .acoustic_detector import default_detector
except (ImportError, ValueError):
    from simulator import simulate_step_history, get_base_density
    from micro_simulator import run_microscopic_comparison, GIS_WAYPOINTS
    from v2x_simulator import run_v2x_comparison, DEFAULT_INTERSECTIONS, V2X_PROTOCOLS
    from config import N, H_default, alpha_default
    from acoustic_detector import default_detector

app = FastAPI(
    title="Ambulance Alert Simulator Backend API",
    version="2.3.0",
    description="Computational Engine for Macroscopic, Microscopic IDM, and V2X Green Corridor Traffic Signal Preemption Simulation"
)

# Enable CORS for decoupled local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationRequest(BaseModel):
    corridor_length: int = Field(default=N, ge=5, le=100)
    horizon: int = Field(default=H_default, ge=0, le=20)
    cooperation: float = Field(default=alpha_default, ge=0.0, le=1.0)

class MicroSimulationRequest(BaseModel):
    corridor_length: int = Field(default=N, ge=10, le=50)
    horizon: int = Field(default=H_default, ge=0, le=15)
    cooperation: float = Field(default=alpha_default, ge=0.0, le=1.0)

class V2XSimulationRequest(BaseModel):
    corridor_length: int = Field(default=N, ge=10, le=50)
    horizon: int = Field(default=H_default, ge=0, le=15)
    cooperation: float = Field(default=alpha_default, ge=0.0, le=1.0)
    protocol: str = Field(default="cv2x_5g")

@app.get("/api/health")
def health_check():
    return {"status": "operational", "system": "Ambulance Alert Engine", "version": "2.2.0"}

@app.get("/api/gis-corridor")
def get_gis_corridor():
    """Returns arterial GIS route nodes and geographic landmarks for Phase 7."""
    return {"waypoints": GIS_WAYPOINTS, "total_segments": N}

@app.get("/api/intersections")
def get_intersections():
    """Returns municipal traffic signal controllers & V2X protocol specifications for Phase 8."""
    return {
        "intersections": DEFAULT_INTERSECTIONS,
        "protocols": V2X_PROTOCOLS
    }

@app.post("/api/simulate")
def run_full_simulation(req: SimulationRequest):
    """Macroscopic corridor simulation."""
    try:
        baseline_frames, baseline_time = simulate_step_history(
            enable_alert=False,
            n=req.corridor_length
        )
        alert_frames, alert_time = simulate_step_history(
            enable_alert=True,
            H=req.horizon,
            alpha=req.cooperation,
            n=req.corridor_length
        )

        time_saved = baseline_time - alert_time
        pct_improvement = round((time_saved / baseline_time) * 100, 2) if baseline_time > 0 else 0.0

        return {
            "parameters": {
                "corridor_length": req.corridor_length,
                "horizon": req.horizon,
                "cooperation": req.cooperation
            },
            "metrics": {
                "baseline_time": baseline_time,
                "alert_time": alert_time,
                "time_saved": time_saved,
                "pct_improvement": pct_improvement
            },
            "summary": {
                "baseline_time_steps": baseline_time,
                "alert_time_steps": alert_time,
                "time_saved_steps": time_saved,
                "improvement_percentage": pct_improvement
            },
            "baseline_frames": baseline_frames,
            "alert_frames": alert_frames,
            "timeline": {
                "baseline": baseline_frames,
                "alert": alert_frames
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/simulate-micro")
def run_micro_simulation(req: MicroSimulationRequest):
    """Phase 7: Microscopic IDM multi-lane car-following & yielding simulation."""
    try:
        results = run_microscopic_comparison(
            N=req.corridor_length,
            H=req.horizon,
            alpha=req.cooperation
        )
        return {
            "parameters": {
                "corridor_length": req.corridor_length,
                "horizon": req.horizon,
                "cooperation": req.cooperation
            },
            "metrics": results["metrics"],
            "gis_corridor": results["gis_corridor"],
            "baseline_frames": results["baseline_frames"],
            "alert_frames": results["alert_frames"],
            "timeline": {
                "baseline": results["baseline_frames"],
                "alert": results["alert_frames"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/simulate-v2x")
def run_v2x_simulation(req: V2XSimulationRequest):
    """Phase 8: Connected Vehicle V2X & Green Corridor Traffic Signal Preemption simulation."""
    try:
        results = run_v2x_comparison(
            N=req.corridor_length,
            H=req.horizon,
            alpha=req.cooperation,
            protocol=req.protocol
        )
        return {
            "parameters": {
                "corridor_length": req.corridor_length,
                "horizon": req.horizon,
                "cooperation": req.cooperation,
                "protocol": req.protocol
            },
            "metrics": results["metrics"],
            "intersections": results["intersections"],
            "baseline_frames": results["baseline_frames"],
            "alert_frames": results["alert_frames"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from acoustic_detector import default_detector

class DetectionRequest(BaseModel):
    ambulance_x: float = Field(default=-100.0)
    ambulance_y: float = Field(default=0.0)
    siren_active: bool = Field(default=True)
    velocity_x: float = Field(default=20.0)
    velocity_y: float = Field(default=0.0)

@app.post("/api/detect-emergency-approach")
def detect_emergency_approach(req: DetectionRequest):
    """
    Automatic Emergency Vehicle Approach Detection Endpoint.
    Analyzes acoustic sensor array readings and detects which side the ambulance is coming from.
    """
    try:
        import numpy as np
        amb_pos = np.array([req.ambulance_x, req.ambulance_y])
        amb_vel = np.array([req.velocity_x, req.velocity_y])
        readings = default_detector.calculate_acoustic_field(amb_pos, siren_active=req.siren_active, ambulance_velocity=amb_vel)
        result = default_detector.detect_approaching_side(readings)
        return {
            "sensor_readings": readings,
            "detection_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    app_target = "src.app:app" if os.path.exists("src/app.py") else "app:app"
    uvicorn.run(app_target, host=host, port=port, reload=True)
