# test_acoustic_detector.py
"""
Unit tests for the Automatic Acoustic Emergency Approach Detector.
Verifies:
1. Correct directional classification for ambulances approaching from West, South, East, North.
2. Ambient noise suppression when no siren is sounding.
3. Decibel decay with distance.
4. Correct 4-aspect signal assignment (approaching side BLUE, other 3 RED).
5. Confidence score scaling.
"""

import pytest
import numpy as np
try:
    from acoustic_detector import AcousticDetector, SENSOR_POSITIONS
except ImportError:
    try:
        from src.acoustic_detector import AcousticDetector, SENSOR_POSITIONS
    except ImportError:
        from backend.src.acoustic_detector import AcousticDetector, SENSOR_POSITIONS

def test_west_approach_automatic_detection():
    detector = AcousticDetector(threshold_db=75.0)
    # Ambulance approaching on West corridor: x = -100m, y = 0
    ambulance_pos = np.array([-100.0, 0.0])
    velocity = np.array([20.0, 0.0]) # 20 m/s moving East toward intersection

    readings = detector.calculate_acoustic_field(ambulance_pos, siren_active=True, ambulance_velocity=velocity)
    result = detector.detect_approaching_side(readings)

    assert result["detected"] is True
    assert result["approaching_side"] == "WEST"
    assert result["peak_spl_db"] >= 75.0
    assert result["signal_states"]["WEST"] == "BLUE"
    assert result["signal_states"]["NORTH"] == "RED"
    assert result["signal_states"]["SOUTH"] == "RED"
    assert result["signal_states"]["EAST"] == "RED"
    assert result["confidence"] > 0.70

def test_south_approach_automatic_detection():
    detector = AcousticDetector(threshold_db=75.0)
    # Ambulance approaching from South: x = 0, y = -120m
    ambulance_pos = np.array([0.0, -120.0])
    velocity = np.array([0.0, 22.0])

    readings = detector.calculate_acoustic_field(ambulance_pos, siren_active=True, ambulance_velocity=velocity)
    result = detector.detect_approaching_side(readings)

    assert result["detected"] is True
    assert result["approaching_side"] == "SOUTH"
    assert result["signal_states"]["SOUTH"] == "BLUE"
    assert result["signal_states"]["NORTH"] == "RED"
    assert result["signal_states"]["EAST"] == "RED"
    assert result["signal_states"]["WEST"] == "RED"

def test_north_approach_automatic_detection():
    detector = AcousticDetector(threshold_db=75.0)
    # Ambulance approaching from North: x = 0, y = 140m
    ambulance_pos = np.array([0.0, 140.0])
    velocity = np.array([0.0, -20.0])

    readings = detector.calculate_acoustic_field(ambulance_pos, siren_active=True, ambulance_velocity=velocity)
    result = detector.detect_approaching_side(readings)

    assert result["detected"] is True
    assert result["approaching_side"] == "NORTH"
    assert result["signal_states"]["NORTH"] == "BLUE"
    assert result["signal_states"]["SOUTH"] == "RED"

def test_east_approach_automatic_detection():
    detector = AcousticDetector(threshold_db=75.0)
    # Ambulance approaching from East: x = 110m, y = 0
    ambulance_pos = np.array([110.0, 0.0])
    velocity = np.array([-25.0, 0.0])

    readings = detector.calculate_acoustic_field(ambulance_pos, siren_active=True, ambulance_velocity=velocity)
    result = detector.detect_approaching_side(readings)

    assert result["detected"] is True
    assert result["approaching_side"] == "EAST"
    assert result["signal_states"]["EAST"] == "BLUE"
    assert result["signal_states"]["WEST"] == "RED"

def test_ambient_noise_no_detection():
    detector = AcousticDetector(threshold_db=75.0)
    ambulance_pos = np.array([0.0, 0.0])
    # Siren turned off: background city ambient only
    readings = detector.calculate_acoustic_field(ambulance_pos, siren_active=False)
    result = detector.detect_approaching_side(readings)

    assert result["detected"] is False
    assert result["approaching_side"] is None
    assert result["action"] == "NORMAL_CYCLE"
    assert result["signal_states"]["NORTH"] == "NORMAL"

def test_distant_siren_below_threshold():
    detector = AcousticDetector(threshold_db=85.0) # High threshold
    # Very far away: 800m
    ambulance_pos = np.array([-800.0, 0.0])
    readings = detector.calculate_acoustic_field(ambulance_pos, siren_active=True)
    result = detector.detect_approaching_side(readings)

    # At 800m, SPL is below 85 dB
    assert result["detected"] is False
