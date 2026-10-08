# backend/v2x_simulator.py
"""
Phase 8: Connected Vehicle V2X & Green Corridor Traffic Signal Preemption Engine
Implements:
1. V2X Communication Channel Model (DSRC 5.9GHz vs 5G C-V2X) with latency & packet loss.
2. Municipal Traffic Signal Controllers (TSC) with automated emergency "Green Corridor" preemption.
3. Multi-Ambulance dispatch & intersection priority arbitration.
4. Comprehensive timeline snapshot generation for real-time frontend visualization.
"""

import numpy as np
from typing import List, Dict, Any, Optional

# ==================== INTERSECTION CONFIGURATION ====================
DEFAULT_INTERSECTIONS = [
    {
        "id": "tsc_0",
        "segment": 4,
        "name": "Arterial Junction A (4th Ave)",
        "cycle_time": 60,      # total cycle seconds
        "green_time": 25,      # normal green phase for corridor
        "yellow_time": 5,      # yellow clearance phase
        "red_time": 30,        # cross-street red phase for corridor
        "offset": 0            # cycle time offset
    },
    {
        "id": "tsc_1",
        "segment": 8,
        "name": "City Center Overpass Crossroad",
        "cycle_time": 60,
        "green_time": 25,
        "yellow_time": 5,
        "red_time": 30,
        "offset": 15
    },
    {
        "id": "tsc_2",
        "segment": 12,
        "name": "Medical District Crossway",
        "cycle_time": 60,
        "green_time": 25,
        "yellow_time": 5,
        "red_time": 30,
        "offset": 30
    },
    {
        "id": "tsc_3",
        "segment": 16,
        "name": "Expressway Slip Road Concourse",
        "cycle_time": 60,
        "green_time": 25,
        "yellow_time": 5,
        "red_time": 30,
        "offset": 45
    }
]

# ==================== V2X COMMUNICATION MODEL ====================
V2X_PROTOCOLS = {
    "cv2x_5g": {
        "name": "5G C-V2X (Release 16+ NR-V2X)",
        "mean_latency_ms": 12.0,
        "jitter_ms": 3.0,
        "tx_range_segments": 8.0,
        "loss_gamma": 3.2
    },
    "dsrc": {
        "name": "DSRC / IEEE 802.11p (5.9 GHz)",
        "mean_latency_ms": 38.0,
        "jitter_ms": 12.0,
        "tx_range_segments": 5.0,
        "loss_gamma": 2.5
    }
}

def calculate_packet_success_rate(distance_segments: float, protocol: str = "cv2x_5g") -> float:
    """
    Computes packet reception probability using log-distance path loss shadow fading:
    P_success = exp(- (d / d_range)^gamma)
    """
    spec = V2X_PROTOCOLS.get(protocol, V2X_PROTOCOLS["cv2x_5g"])
    d_range = spec["tx_range_segments"]
    gamma = spec["loss_gamma"]

    if distance_segments <= 0:
        return 1.0
    
    loss_prob = 1.0 - np.exp(-((distance_segments / d_range) ** gamma))
    success_rate = max(0.02, min(1.0, 1.0 - loss_prob))
    return float(success_rate)

class TrafficSignalController:
    """Models a single intersection controller with normal cycling & emergency preemption."""
    def __init__(self, tsc_id: str, segment: int, name: str, cycle: int, green: int, yellow: int, red: int, offset: int):
        self.id = tsc_id
        self.segment = segment
        self.name = name
        self.cycle_time = cycle
        self.green_time = green
        self.yellow_time = yellow
        self.red_time = red
        self.offset = offset
        self.is_preempted = False
        self.preemption_hold_timer = 0.0

    def get_state(self, sim_time_sec: float) -> str:
        """Returns current light state: 'GREEN', 'YELLOW', 'RED', or 'PREEMPTED_GREEN'."""
        if self.is_preempted:
            return "PREEMPTED_GREEN"
        
        cycle_pos = (sim_time_sec + self.offset) % self.cycle_time
        if cycle_pos < self.green_time:
            return "GREEN"
        elif cycle_pos < (self.green_time + self.yellow_time):
            return "YELLOW"
        else:
            return "RED"

    def trigger_preemption(self, hold_seconds: float = 12.0):
        self.is_preempted = True
        self.preemption_hold_timer = hold_seconds

    def update_preemption(self, dt: float):
        if self.is_preempted:
            self.preemption_hold_timer -= dt
            if self.preemption_hold_timer <= 0:
                self.is_preempted = False

def simulate_v2x_green_corridor(
    N: int = 20,
    H: int = 3,
    alpha: float = 0.5,
    enable_v2x: bool = True,
    enable_preemption: bool = True,
    protocol: str = "cv2x_5g",
    preemption_distance: float = 3.5,
    dt: float = 0.5,
    max_steps: int = 300
) -> Dict[str, Any]:
    """
    Simulates emergency transit under V2X communication and automated
    Green Corridor traffic signal preemption.
    """
    H = max(0, int(H))
    alpha = float(np.clip(alpha, 0.0, 1.0))
    protocol = protocol if protocol in V2X_PROTOCOLS else "cv2x_5g"

    # Initialize Traffic Signal Controllers
    intersections = [
        TrafficSignalController(
            cfg["id"], cfg["segment"], cfg["name"],
            cfg["cycle_time"], cfg["green_time"], cfg["yellow_time"], cfg["red_time"], cfg["offset"]
        )
        for cfg in DEFAULT_INTERSECTIONS if cfg["segment"] < N
    ]

    amb_pos = 0.0
    amb_speed = 0.8  # initial velocity (segments / sec)
    v_max = 1.2
    v_free = 1.0

    # Downstream base congestion density
    densities = [0.2 + 0.6 * (i / float(max(1, N - 1))) for i in range(N)]

    timeline_frames = []
    step = 0
    total_signal_delay_sec = 0.0
    packets_sent = 0
    packets_received = 0
    preemption_events = 0
    arrival_time_step = None

    spec = V2X_PROTOCOLS.get(protocol, V2X_PROTOCOLS["cv2x_5g"])

    while step < max_steps and amb_pos < (N - 1):
        sim_time = step * dt
        amb_seg = int(np.floor(amb_pos))

        # 1. Update Traffic Signal Preemption Logic
        preempted_in_step = 0
        for tsc in intersections:
            dist_to_intersection = tsc.segment - amb_pos

            if enable_preemption and (0.0 < dist_to_intersection <= preemption_distance):
                if not tsc.is_preempted:
                    tsc.trigger_preemption(hold_seconds=14.0)
                    preemption_events += 1
                preempted_in_step += 1
            
            tsc.update_preemption(dt)

        # 2. V2X Communication Packet Transmission
        step_packet_sent = 0
        step_packet_recv = 0
        if enable_v2x:
            # Broadcast V2X alert to civilian vehicles & upcoming infrastructure
            for s in range(amb_seg + 1, min(N, amb_seg + H + 3)):
                dist = s - amb_pos
                p_success = calculate_packet_success_rate(dist, protocol)
                step_packet_sent += 1
                if np.random.rand() < p_success:
                    step_packet_recv += 1
            packets_sent += step_packet_sent
            packets_received += step_packet_recv

        # 3. Check Traffic Signal Obstruction at Current Segment
        nearest_ahead_tsc = next((tsc for tsc in intersections if 0.0 <= (tsc.segment - amb_pos) < 0.6), None)
        signal_speed_factor = 1.0

        if nearest_ahead_tsc:
            sig_state = nearest_ahead_tsc.get_state(sim_time)
            if sig_state == "RED":
                # Red light forced deceleration / wait penalty
                signal_speed_factor = 0.15
                total_signal_delay_sec += dt
            elif sig_state == "YELLOW":
                signal_speed_factor = 0.6
            elif sig_state in ("GREEN", "PREEMPTED_GREEN"):
                signal_speed_factor = 1.05  # clear free flow priority wave

        # 4. Effective Density & Advance Driver Yielding
        local_density = densities[min(N - 1, amb_seg + 1)]
        if enable_v2x:
            # Yielding efficiency scaled by cooperation factor
            effective_density = local_density * (1.0 - alpha * 0.75)
        else:
            effective_density = local_density

        target_speed = v_max * (1.0 - effective_density) * signal_speed_factor
        amb_speed = float(np.clip(amb_speed + 0.4 * (target_speed - amb_speed), 0.1, v_max))
        amb_pos = float(min(N - 1, amb_pos + amb_speed * dt))

        # Check arrival
        if amb_pos >= (N - 1) and arrival_time_step is None:
            arrival_time_step = step

        # Record snapshot frame
        tsc_states = [
            {
                "id": tsc.id,
                "segment": tsc.segment,
                "name": tsc.name,
                "state": tsc.get_state(sim_time),
                "is_preempted": tsc.is_preempted
            }
            for tsc in intersections
        ]

        frame = {
            "step": step,
            "sim_time_sec": round(sim_time, 2),
            "ambulance_pos": round(amb_pos, 2),
            "ambulance_speed": round(amb_speed, 2),
            "signal_speed_factor": round(signal_speed_factor, 2),
            "intersections": tsc_states,
            "v2x_stats": {
                "active_protocol": spec["name"],
                "packets_sent": packets_sent,
                "packets_received": packets_received,
                "pdr_pct": round((packets_received / max(1, packets_sent)) * 100, 1),
                "latency_ms": round(spec["mean_latency_ms"] + np.random.uniform(-1, 1) * spec["jitter_ms"], 1)
            }
        }
        timeline_frames.append(frame)
        step += 1

    final_steps = arrival_time_step if arrival_time_step is not None else max_steps
    final_seconds = round(final_steps * dt, 2)

    return {
        "summary": {
            "mode": "green_corridor_v2x" if (enable_v2x and enable_preemption) else "baseline_no_v2x",
            "arrival_time_steps": final_steps,
            "arrival_time_seconds": final_seconds,
            "signal_delay_seconds": round(total_signal_delay_sec, 2),
            "preemption_events": preemption_events,
            "packet_delivery_ratio": round((packets_received / max(1, packets_sent)) * 100, 1) if enable_v2x else 0.0
        },
        "intersections": [
            {"id": t.id, "segment": t.segment, "name": t.name} for t in intersections
        ],
        "frames": timeline_frames
    }

def run_v2x_comparison(
    N: int = 20,
    H: int = 3,
    alpha: float = 0.5,
    protocol: str = "cv2x_5g"
) -> Dict[str, Any]:
    """
    Runs side-by-side comparison between:
    1. Baseline Conventional Corridor (No V2X, No Traffic Signal Preemption - stops at red lights)
    2. Connected Green Corridor (5G C-V2X Geo-broadcasting + Automated Signal Preemption)
    """
    np.random.seed(42)
    baseline_run = simulate_v2x_green_corridor(
        N=N, H=H, alpha=alpha, enable_v2x=False, enable_preemption=False, protocol=protocol
    )

    np.random.seed(42)
    alert_run = simulate_v2x_green_corridor(
        N=N, H=H, alpha=alpha, enable_v2x=True, enable_preemption=True, protocol=protocol
    )

    base_time = baseline_run["summary"]["arrival_time_seconds"]
    alert_time = alert_run["summary"]["arrival_time_seconds"]
    time_saved = round(base_time - alert_time, 2)
    pct_saved = round((time_saved / base_time) * 100, 2) if base_time > 0 else 0.0

    return {
        "metrics": {
            "baseline_seconds": base_time,
            "alert_seconds": alert_time,
            "time_saved_seconds": time_saved,
            "percentage_gain": pct_saved,
            "baseline_signal_delay_s": baseline_run["summary"]["signal_delay_seconds"],
            "alert_signal_delay_s": alert_run["summary"]["signal_delay_seconds"],
            "preemption_events_triggered": alert_run["summary"]["preemption_events"],
            "v2x_pdr_pct": alert_run["summary"]["packet_delivery_ratio"]
        },
        "intersections": alert_run["intersections"],
        "baseline_frames": baseline_run["frames"],
        "alert_frames": alert_run["frames"]
    }

if __name__ == "__main__":
    res = run_v2x_comparison()
    print("=== Phase 8: V2X & Green Corridor Results ===")
    print(f"Baseline Time  : {res['metrics']['baseline_seconds']}s (Signal Delay: {res['metrics']['baseline_signal_delay_s']}s)")
    print(f"Green Corridor : {res['metrics']['alert_seconds']}s (Signal Delay: {res['metrics']['alert_signal_delay_s']}s)")
    print(f"Time Saved     : {res['metrics']['time_saved_seconds']}s ({res['metrics']['percentage_gain']}%)")
    print(f"Preemptions    : {res['metrics']['preemption_events_triggered']}")
    print(f"V2X PDR        : {res['metrics']['v2x_pdr_pct']}%")
