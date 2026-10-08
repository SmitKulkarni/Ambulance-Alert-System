# test_v2x_simulator.py
import pytest
import numpy as np
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from v2x_simulator import (
    TrafficSignalController,
    calculate_packet_success_rate,
    simulate_v2x_green_corridor,
    run_v2x_comparison,
    DEFAULT_INTERSECTIONS,
    V2X_PROTOCOLS,
)

def test_v2x_packet_success_rate_distance_decay():
    """Packet reception probability should strictly decrease as distance increases."""
    p_near = calculate_packet_success_rate(1.0, protocol="cv2x_5g")
    p_mid = calculate_packet_success_rate(5.0, protocol="cv2x_5g")
    p_far = calculate_packet_success_rate(12.0, protocol="cv2x_5g")

    assert p_near >= p_mid >= p_far, "V2X PDR should decay with distance"
    assert 0.0 <= p_far <= 1.0

def test_v2x_protocol_specs():
    """Ensure both 5G C-V2X and DSRC protocols are configured properly."""
    assert "cv2x_5g" in V2X_PROTOCOLS
    assert "dsrc" in V2X_PROTOCOLS
    assert V2X_PROTOCOLS["cv2x_5g"]["mean_latency_ms"] < V2X_PROTOCOLS["dsrc"]["mean_latency_ms"]

def test_traffic_signal_state_transitions():
    """TSC should cycle correctly through Green, Yellow, and Red states."""
    tsc = TrafficSignalController("tsc_test", segment=5, name="Test Node", cycle=60, green=25, yellow=5, red=30, offset=0)
    assert tsc.get_state(10.0) == "GREEN"
    assert tsc.get_state(27.0) == "YELLOW"
    assert tsc.get_state(40.0) == "RED"
    assert tsc.get_state(70.0) == "GREEN"  # next cycle (70 % 60 = 10)

def test_traffic_signal_emergency_preemption():
    """Triggering preemption should immediately force PREEMPTED_GREEN until timer expires."""
    tsc = TrafficSignalController("tsc_test", segment=5, name="Test Node", cycle=60, green=25, yellow=5, red=30, offset=0)
    # At t=40s, light would normally be RED
    assert tsc.get_state(40.0) == "RED"
    
    # Emergency preemption triggered
    tsc.trigger_preemption(hold_seconds=10.0)
    assert tsc.get_state(40.0) == "PREEMPTED_GREEN"
    
    # Advance timer past expiration
    tsc.update_preemption(11.0)
    assert tsc.is_preempted is False
    assert tsc.get_state(40.0) == "RED"

def test_v2x_green_corridor_simulation():
    """Simulate single V2X corridor and verify frame integrity."""
    res = simulate_v2x_green_corridor(N=20, H=3, alpha=0.5, enable_v2x=True, enable_preemption=True)
    summary = res["summary"]
    assert summary["mode"] == "green_corridor_v2x"
    assert summary["arrival_time_seconds"] > 0
    assert summary["preemption_events"] > 0
    assert summary["packet_delivery_ratio"] > 80.0
    assert len(res["frames"]) > 10

def test_green_corridor_saves_travel_time_over_baseline():
    """Connected Green corridor must eliminate signal delays and reduce travel time."""
    comparison = run_v2x_comparison(N=20, H=3, alpha=0.5)
    metrics = comparison["metrics"]
    
    assert metrics["baseline_seconds"] > metrics["alert_seconds"]
    assert metrics["time_saved_seconds"] > 0
    assert metrics["percentage_gain"] > 0
    assert metrics["alert_signal_delay_s"] < metrics["baseline_signal_delay_s"]
