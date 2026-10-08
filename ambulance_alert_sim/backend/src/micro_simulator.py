# backend/micro_simulator.py
"""
Phase 7: Microscopic Multi-Lane & GIS Corridor Simulation Engine
Implements:
1. Intelligent Driver Model (IDM) for car-following longitudinal dynamics.
2. Emergency Lateral Lane-Yielding model (civilian vehicles clearing Lane 1).
3. Multi-lane 2D roadway with discrete individual civilian vehicles.
4. Real-world GIS arterial corridor coordinates (Metropolitan Hospital Transit Corridor).
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional

# ==================== GIS CORRIDOR COORDINATES ====================
# GeoJSON-style arterial route connecting Central Metro Station to City Memorial Hospital
GIS_WAYPOINTS = [
    {"segment": 0,  "lat": 18.5204, "lon": 73.8567, "name": "Corridor Entrance (Metro Hub)"},
    {"segment": 4,  "lat": 18.5235, "lon": 73.8601, "name": "Arterial Junction A"},
    {"segment": 8,  "lat": 18.5270, "lon": 73.8645, "name": "City Center Overpass"},
    {"segment": 12, "lat": 18.5312, "lon": 73.8690, "name": "Medical District Crossway"},
    {"segment": 16, "lat": 18.5358, "lon": 73.8732, "name": "Expressway Slip Road"},
    {"segment": 19, "lat": 18.5395, "lon": 73.8770, "name": "City Memorial Hospital Emergency Gate"}
]

# ==================== IDM & MOBIL PARAMETERS ====================
IDM_PARAMS = {
    "v0_ambulance": 1.2,    # Desired speed for emergency ambulance (seg/s)
    "v0_civilian_base": 0.9,# Free-flow speed for civilian cars (seg/s)
    "T_gap": 1.2,           # Safe time headway (seconds)
    "s0": 0.25,             # Minimum standing bumper-to-bumper distance (segments)
    "a_max": 0.5,           # Maximum comfortable acceleration (seg/s^2)
    "b_comf": 0.6,          # Comfortable deceleration (seg/s^2)
    "delta": 4.0            # Acceleration exponent
}

class MicroVehicle:
    def __init__(self, vid: str, vtype: str, x: float, v: float, lane: int):
        self.id = vid
        self.type = vtype     # "civilian" or "ambulance"
        self.x = x            # Longitudinal position along corridor [0, N]
        self.v = v            # Instantaneous velocity
        self.lane = lane      # 0 = civilian slow lane, 1 = emergency corridor lane
        self.target_lane = lane
        self.is_yielding = False

def idm_acceleration(v: float, v_lead: float, gap: float, v_desired: float) -> float:
    """Computes acceleration using the Intelligent Driver Model (Treiber et al.)."""
    s0 = IDM_PARAMS["s0"]
    T = IDM_PARAMS["T_gap"]
    a = IDM_PARAMS["a_max"]
    b = IDM_PARAMS["b_comf"]
    delta = IDM_PARAMS["delta"]

    # Free road term towards local desired velocity
    acc_free = a * (1.0 - (v / max(v_desired, 1e-4)) ** delta)

    # Interaction braking term with leader
    if gap is not None and gap > 0:
        delta_v = v - v_lead
        s_star = s0 + max(0.0, v * T + (v * delta_v) / (2.0 * np.sqrt(a * b)))
        acc_int = -a * ((s_star / max(gap, 0.05)) ** 2)
    else:
        acc_int = 0.0

    acc = acc_free + acc_int
    return float(np.clip(acc, -1.4, a))

def simulate_microscopic_corridor(
    N: int = 20,
    H: int = 3,
    alpha: float = 0.5,
    civilian_count: Optional[int] = None,
    enable_alert: bool = True,
    dt: float = 0.5,
    max_steps: int = 300
) -> Dict[str, Any]:
    """
    Executes microscopic multi-lane traffic simulation with discrete vehicles
    and emergency yielding behavior.
    """
    np.random.seed(42)
    H = max(0, int(H))
    alpha = float(np.clip(alpha, 0.0, 1.0))

    if civilian_count is None:
        civilian_count = max(8, int(N * 1.2))

    # Initialize Civilian Vehicles distributed across both lanes
    vehicles: List[MicroVehicle] = []
    for i in range(civilian_count):
        pos = 2.0 + (i / float(civilian_count)) * (N - 3.2)
        # Downstream congestion profile (density rises from 0.2 to 0.8)
        local_density = 0.2 + 0.6 * (pos / float(N))
        v_init = IDM_PARAMS["v0_civilian_base"] * (1.0 - local_density)
        lane = 1 if (i % 2 == 0) else 0 # 50% in fast/emergency lane initially
        vehicles.append(MicroVehicle(f"car_{i}", "civilian", pos, v_init, lane))

    # Add Emergency Ambulance at corridor entry in emergency lane (lane 1)
    ambulance = MicroVehicle("ambulance_0", "ambulance", 0.0, 0.6, 1)
    vehicles.append(ambulance)

    timeline_frames = []
    time_step = 0
    ambulance_finished = False
    arrival_time = None

    while time_step < max_steps and not ambulance_finished:
        amb_x = ambulance.x
        amb_seg = int(np.floor(amb_x))
        alert_horizon_seg = amb_seg + H

        # 1. Update Lane Yielding (Proactive Lateral Clearing)
        for veh in vehicles:
            if veh.type == "ambulance":
                veh.lane = 1
                continue

            veh_seg = int(np.floor(veh.x))
            
            # If vehicle is in the emergency lane (1) and within the alert horizon ahead
            if enable_alert and (amb_seg < veh_seg <= alert_horizon_seg) and veh.lane == 1:
                # Driver yields into Lane 0 if compliance threshold met
                # Deterministic check based on vehicle index and alpha
                compliance_val = ((hash(veh.id) & 0xffff) % 100) / 100.0
                if compliance_val < alpha:
                    veh.is_yielding = True
                    veh.target_lane = 0
                else:
                    veh.is_yielding = False
            else:
                veh.is_yielding = False

            # Lateral lane change transition
            if veh.lane != veh.target_lane:
                same_target_vehs = [v for v in vehicles if v.lane == veh.target_lane and v.id != veh.id]
                lead = next((v for v in sorted(same_target_vehs, key=lambda o: o.x) if v.x > veh.x), None)
                trail = next((v for v in sorted(same_target_vehs, key=lambda o: o.x, reverse=True) if v.x <= veh.x), None)

                lead_gap = (lead.x - veh.x) if lead else 10.0
                trail_gap = (veh.x - trail.x) if trail else 10.0

                if lead_gap > 0.35 and trail_gap > 0.35:
                    veh.lane = veh.target_lane

        # 2. Update Longitudinal Dynamics using IDM
        sorted_vehs = sorted(vehicles, key=lambda v: v.x, reverse=True)
        for veh in sorted_vehs:
            # Find direct leader vehicle in the same lane
            same_lane_vehs = [v for v in sorted_vehs if v.lane == veh.lane and v.x > veh.x and v.id != veh.id]
            lead_veh = same_lane_vehs[-1] if same_lane_vehs else None
            
            lead_v = lead_veh.v if lead_veh else veh.v
            gap = (lead_veh.x - veh.x) if lead_veh else 100.0

            # Desired velocity diminishes downstream due to traffic density
            if veh.type == "ambulance":
                v_des = IDM_PARAMS["v0_ambulance"]
            else:
                local_density = 0.2 + 0.6 * min(1.0, veh.x / float(N))
                v_des = IDM_PARAMS["v0_civilian_base"] * (1.0 - local_density)

            acc = idm_acceleration(veh.v, lead_v, gap, v_des)
            veh.v = max(0.0, veh.v + acc * dt)
            veh.x += veh.v * dt

        # Check ambulance terminal arrival
        if ambulance.x >= N - 1 and not ambulance_finished:
            ambulance_finished = True
            ambulance.x = N - 1
            arrival_time = time_step

        # Record snapshot frame for visualization
        frame_state = {
            "step": time_step,
            "sim_time_sec": round(time_step * dt, 2),
            "ambulance": {
                "position": round(float(ambulance.x), 2),
                "speed": round(float(ambulance.v), 2),
                "lane": ambulance.lane
            },
            "vehicles": [
                {
                    "id": v.id,
                    "type": v.type,
                    "x": round(float(v.x), 2),
                    "v": round(float(v.v), 2),
                    "lane": v.lane,
                    "yielding": v.is_yielding
                }
                for v in vehicles if v.type != "ambulance"
            ],
            "alert_active": enable_alert,
            "alert_window": [amb_seg + 1, min(alert_horizon_seg, N - 1)] if enable_alert else []
        }
        timeline_frames.append(frame_state)
        time_step += 1

    return {
        "summary": {
            "mode": "with_advance_alert" if enable_alert else "baseline_no_alert",
            "corridor_segments": N,
            "alert_horizon": H,
            "cooperation_factor": alpha,
            "arrival_time_steps": arrival_time if arrival_time is not None else max_steps,
            "arrival_time_sec": round((arrival_time if arrival_time is not None else max_steps) * dt, 2),
            "civilian_vehicles_count": civilian_count
        },
        "gis_corridor": GIS_WAYPOINTS,
        "frames": timeline_frames
    }

def run_microscopic_comparison(N: int = 20, H: int = 3, alpha: float = 0.5) -> Dict[str, Any]:
    """Runs dual microscopic simulations (baseline vs. alert) and returns comparative analytics."""
    base_run = simulate_microscopic_corridor(N=N, H=H, alpha=alpha, enable_alert=False)
    alert_run = simulate_microscopic_corridor(N=N, H=H, alpha=alpha, enable_alert=True)

    base_time = base_run["summary"]["arrival_time_steps"]
    alert_time = alert_run["summary"]["arrival_time_steps"]
    time_saved = base_time - alert_time
    pct_gain = round((time_saved / base_time) * 100, 2) if base_time > 0 else 0.0

    return {
        "metrics": {
            "baseline_steps": base_time,
            "alert_steps": alert_time,
            "time_saved_steps": time_saved,
            "percentage_gain": pct_gain,
            "baseline_seconds": base_run["summary"]["arrival_time_sec"],
            "alert_seconds": alert_run["summary"]["arrival_time_sec"]
        },
        "gis_corridor": GIS_WAYPOINTS,
        "baseline_frames": base_run["frames"],
        "alert_frames": alert_run["frames"]
    }

if __name__ == "__main__":
    res = run_microscopic_comparison()
    print("=== Microscopic Simulation Results ===")
    print(f"Baseline Time : {res['metrics']['baseline_steps']} steps ({res['metrics']['baseline_seconds']}s)")
    print(f"Alert Time    : {res['metrics']['alert_steps']} steps ({res['metrics']['alert_seconds']}s)")
    print(f"Time Saved    : {res['metrics']['time_saved_steps']} steps")
    print(f"Improvement   : {res['metrics']['percentage_gain']}%")
