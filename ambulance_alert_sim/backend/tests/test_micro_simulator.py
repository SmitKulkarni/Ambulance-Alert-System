# test_micro_simulator.py
import pytest
import numpy as np
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from micro_simulator import (
    MicroVehicle,
    idm_acceleration,
    simulate_microscopic_corridor,
    run_microscopic_comparison,
    GIS_WAYPOINTS,
)

def test_idm_acceleration_free_flow():
    """Vehicle far from any leader should accelerate smoothly toward desired velocity."""
    v = 0.0
    v_des = 1.0
    acc = idm_acceleration(v=v, v_lead=None, gap=None, v_desired=v_des)
    # At v=0 and no leader, acc should be equal to a_max (0.5)
    assert np.isclose(acc, 0.5, atol=1e-2)

def test_idm_acceleration_at_desired_speed():
    """Vehicle already at desired speed without leader should have negligible acceleration."""
    v = 1.0
    v_des = 1.0
    acc = idm_acceleration(v=v, v_lead=None, gap=None, v_desired=v_des)
    assert np.isclose(acc, 0.0, atol=1e-2)

def test_idm_braking_near_leader():
    """Vehicle close to a slower leader should brake (negative acceleration)."""
    v = 1.0
    v_lead = 0.1
    gap = 0.15  # very tight gap below s0=0.25
    acc = idm_acceleration(v=v, v_lead=v_lead, gap=gap, v_desired=1.0)
    assert acc < 0.0, "Vehicle should brake to maintain safe headway"

def test_gis_waypoints_integrity():
    """Check GIS arterial waypoints coverage and coordinate validities."""
    assert len(GIS_WAYPOINTS) >= 6
    first = GIS_WAYPOINTS[0]
    last = GIS_WAYPOINTS[-1]
    assert "Metro" in first["name"]
    assert "Hospital" in last["name"]
    for wp in GIS_WAYPOINTS:
        assert 18.0 <= wp["lat"] <= 19.5, "Latitude within metro bounds"
        assert 73.0 <= wp["lon"] <= 74.5, "Longitude within metro bounds"
        assert "segment" in wp
        assert "name" in wp

def test_simulate_microscopic_corridor_completion():
    """Simulate microscopic run and verify vehicles and ambulance reach destination."""
    res = simulate_microscopic_corridor(N=20, H=3, alpha=0.5, enable_alert=False)
    summary = res["summary"]
    assert summary["corridor_segments"] == 20
    assert summary["arrival_time_steps"] > 0
    assert summary["arrival_time_sec"] > 0
    assert len(res["frames"]) > 10
    
    # Check frame structure
    frame0 = res["frames"][0]
    assert "step" in frame0
    assert "sim_time_sec" in frame0
    assert "ambulance" in frame0
    assert "vehicles" in frame0
    assert frame0["ambulance"]["lane"] == 1
    assert len(frame0["vehicles"]) > 0

def test_alert_saves_travel_time():
    """Microscopic simulation with alert should enable ambulance travel time reduction."""
    comparison = run_microscopic_comparison(N=20, H=3, alpha=0.6)
    assert "metrics" in comparison
    assert "gis_corridor" in comparison
    assert "baseline_frames" in comparison
    assert "alert_frames" in comparison
    
    metrics = comparison["metrics"]
    assert metrics["baseline_steps"] >= metrics["alert_steps"]
    assert metrics["time_saved_steps"] >= 0
    assert metrics["percentage_gain"] >= 0
    assert metrics["baseline_seconds"] >= metrics["alert_seconds"]
