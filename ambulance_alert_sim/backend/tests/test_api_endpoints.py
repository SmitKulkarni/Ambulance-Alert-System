import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"

def test_gis_corridor():
    response = client.get("/api/gis-corridor")
    assert response.status_code == 200
    data = response.json()
    assert "waypoints" in data
    assert len(data["waypoints"]) > 0

def test_intersections():
    response = client.get("/api/intersections")
    assert response.status_code == 200
    data = response.json()
    assert "intersections" in data
    assert "protocols" in data

def test_macroscopic_simulation():
    payload = {"corridor_length": 20, "horizon": 3, "cooperation": 0.5}
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "baseline_time" in data["metrics"]
    assert "alert_time" in data["metrics"]
    assert data["metrics"]["alert_time"] <= data["metrics"]["baseline_time"]

def test_microscopic_simulation():
    payload = {"corridor_length": 20, "horizon": 3, "cooperation": 0.5}
    response = client.post("/api/simulate-micro", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "gis_corridor" in data

def test_v2x_simulation():
    payload = {
        "corridor_length": 20,
        "horizon": 3,
        "cooperation": 0.5,
        "protocol": "cv2x_5g"
    }
    response = client.post("/api/simulate-v2x", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "intersections" in data

def test_acoustic_detection():
    payload = {
        "ambulance_x": -80.0,
        "ambulance_y": 0.0,
        "siren_active": True,
        "velocity_x": 15.0,
        "velocity_y": 0.0
    }
    response = client.post("/api/detect-emergency-approach", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "sensor_readings" in data
    assert "detection_result" in data
    assert data["detection_result"]["detected"] is True
    assert data["detection_result"]["approaching_side"] == "WEST"
    assert data["detection_result"]["signal_states"]["WEST"] == "BLUE"
    assert data["detection_result"]["signal_states"]["NORTH"] == "RED"
    assert data["detection_result"]["confidence"] > 0.90

