# test_edge_cases.py
import pytest
import numpy as np

try:
    from simulator import (
        get_base_density,
        effective_density_with_alert,
        ambulance_speed,
        simulate_step_history,
    )
    from micro_simulator import (
        simulate_microscopic_corridor,
        run_microscopic_comparison,
        idm_acceleration,
    )
    from v2x_simulator import (
        simulate_v2x_green_corridor,
        run_v2x_comparison,
        calculate_packet_success_rate,
    )
except ImportError:
    from src.simulator import (
        get_base_density,
        effective_density_with_alert,
        ambulance_speed,
        simulate_step_history,
    )
    from src.micro_simulator import (
        simulate_microscopic_corridor,
        run_microscopic_comparison,
        idm_acceleration,
    )
    from src.v2x_simulator import (
        simulate_v2x_green_corridor,
        run_v2x_comparison,
        calculate_packet_success_rate,
    )

def test_extreme_cooperation_alpha_zero():
    """Alpha = 0.0 must yield identical travel time to baseline."""
    base_frames, base_time = simulate_step_history(enable_alert=False, n=20)
    alert_frames, alert_time = simulate_step_history(enable_alert=True, H=3, alpha=0.0, n=20)
    assert base_time == alert_time, "When alpha=0.0, no clearing occurs, time should equal baseline"

def test_extreme_cooperation_alpha_one():
    """Alpha = 1.0 must yield maximum clearance and lower transit time."""
    _, base_time = simulate_step_history(enable_alert=False, n=20)
    _, alert_time = simulate_step_history(enable_alert=True, H=3, alpha=1.0, n=20)
    assert alert_time < base_time

def test_horizon_zero_equals_no_alert():
    """Horizon H = 0 must produce identical travel time to no alert."""
    _, base_time = simulate_step_history(enable_alert=False, n=20)
    _, alert_time = simulate_step_history(enable_alert=True, H=0, alpha=0.5, n=20)
    assert base_time == alert_time

def test_microscopic_adaptive_civilian_count():
    """Microscopic simulation should adapt civilian vehicle count to corridor length."""
    res_short = simulate_microscopic_corridor(N=10, H=2, alpha=0.5)
    res_long = simulate_microscopic_corridor(N=40, H=4, alpha=0.5)
    
    count_short = res_short["summary"]["civilian_vehicles_count"]
    count_long = res_long["summary"]["civilian_vehicles_count"]
    assert count_long > count_short, "Longer corridors should scale civilian vehicle counts"

def test_v2x_unknown_protocol_fallback():
    """Passing an unknown protocol string should fall back gracefully to default without error."""
    rate = calculate_packet_success_rate(distance_segments=3.0, protocol="non_existent_proto")
    assert 0.0 <= rate <= 1.0

def test_v2x_simulation_short_corridor():
    """Corridors with small N should execute safely without crashing even if fewer TSCs exist."""
    res = simulate_v2x_green_corridor(N=10, H=2, alpha=0.5)
    assert res["summary"]["arrival_time_steps"] > 0
    assert len(res["frames"]) > 0

def test_micro_comparison_repeatability():
    """Dual runs with same seeds must yield deterministic results."""
    run1 = run_microscopic_comparison(N=20, H=3, alpha=0.5)
    run2 = run_microscopic_comparison(N=20, H=3, alpha=0.5)
    assert run1["metrics"]["baseline_steps"] == run2["metrics"]["baseline_steps"]
    assert run1["metrics"]["alert_steps"] == run2["metrics"]["alert_steps"]
