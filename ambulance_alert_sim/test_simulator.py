import numpy as np
import pytest
from config import N, T_max, H_default, alpha_default
from simulator import (
    get_base_density,
    effective_density_with_alert,
    ambulance_speed,
    simulate_no_alert,
    simulate_with_alert,
    validate_parameters,
)

def test_density():
    d = get_base_density()
    assert len(d) == N
    assert np.all((d >= 0) & (d <= 1))

def test_alert_reduces_future_density():
    d = get_base_density()
    e = effective_density_with_alert(d, 0, 3, 0.5)
    assert np.all(e[1:4] <= d[1:4])
    assert np.allclose(e[4:], d[4:])

def test_speed():
    assert ambulance_speed(0.0) == 1.0
    assert ambulance_speed(1.0) == 0.0

def test_simulation_finishes():
    d = get_base_density()
    _, t1 = simulate_no_alert(d)
    _, t2 = simulate_with_alert(d, H=H_default, alpha=alpha_default)
    assert t1 <= T_max
    assert t2 <= T_max

def test_alert_is_not_worse_in_this_model():
    d = get_base_density()
    _, t1 = simulate_no_alert(d)
    _, t2 = simulate_with_alert(d, H=3, alpha=0.5)
    assert t2 <= t1

def test_parameter_validation_errors():
    with pytest.raises(ValueError):
        validate_parameters(-1, 0.5)
    with pytest.raises(ValueError):
        validate_parameters(3, -0.1)
    with pytest.raises(ValueError):
        validate_parameters(3, 1.2)
    with pytest.raises(ValueError):
        get_base_density(1)

def test_float_horizon_safe():
    d = get_base_density()
    e = effective_density_with_alert(d, 0, 3.0, 0.5)
    assert len(e) == len(d)
    assert e[1] < d[1]

def test_zero_horizon_equals_no_alert():
    d = get_base_density()
    _, t1 = simulate_no_alert(d)
    _, t2 = simulate_with_alert(d, H=0, alpha=0.5)
    assert t1 == t2

def test_zero_alpha_equals_no_alert():
    d = get_base_density()
    _, t1 = simulate_no_alert(d)
    _, t2 = simulate_with_alert(d, H=3, alpha=0.0)
    assert t1 == t2

def test_speed_clipping():
    # Negative density clipped to 0
    assert ambulance_speed(-0.5) == 1.0
    # Density greater than 1 clipped to 1
    assert ambulance_speed(1.5) == 0.0

def test_short_density_array_raises():
    with pytest.raises(ValueError):
        simulate_no_alert([0.5])
    with pytest.raises(ValueError):
        simulate_with_alert([0.5], H=3, alpha=0.5)
