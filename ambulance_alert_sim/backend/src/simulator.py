# backend/simulator.py
import numpy as np
from config import N, v_max, H_default, alpha_default, T_max

def get_base_density(n: int = N) -> np.ndarray:
    """Generates synthetic baseline traffic density ramping linearly from 0.2 to 0.8."""
    if n < 2:
        raise ValueError("n must be at least 2")
    return np.linspace(0.2, 0.8, n)

def validate_parameters(H: int, alpha: float):
    if H < 0:
        raise ValueError("H must be non-negative")
    if not (0.0 <= alpha <= 1.0):
        raise ValueError("alpha must be between 0.0 and 1.0")

def effective_density_with_alert(base_density: np.ndarray, ambulance_pos: float, H: int, alpha: float) -> np.ndarray:
    """Applies driver clearance (1 - alpha) to road segments ahead within horizon H."""
    validate_parameters(H, alpha)
    rho_eff = np.asarray(base_density, dtype=float).copy()
    start = int(ambulance_pos) + 1
    end = min(int(ambulance_pos) + int(H) + 1, len(rho_eff))
    if start < end:
        rho_eff[start:end] = rho_eff[start:end] * (1.0 - alpha)
    return rho_eff

def ambulance_speed(rho_eff_value: float, maximum_speed: float = v_max) -> float:
    """Linear speed degradation model: speed decreases monotonically with density."""
    rho = float(np.clip(rho_eff_value, 0.0, 1.0))
    return maximum_speed * (1.0 - rho)

def simulate_step_history(enable_alert: bool = True, H: int = H_default, alpha: float = alpha_default, n: int = N):
    """
    Simulates the corridor run and records frame-by-frame state
    for live visual streaming.
    """
    base_density = get_base_density(n)
    pos = 0.0
    time_step = 0
    history = []

    while pos < len(base_density) - 1 and time_step < T_max:
        idx = min(int(np.floor(pos)), len(base_density) - 1)
        next_idx = min(idx + 1, len(base_density) - 1)

        if enable_alert:
            current_density = effective_density_with_alert(base_density, idx, H, alpha)
        else:
            current_density = base_density.copy()

        # Alert lookahead correction: upcoming entry segment dictates speed
        speed = ambulance_speed(current_density[next_idx], v_max)

        history.append({
            "step": time_step,
            "position": round(float(pos), 2),
            "ambulance_pos": round(float(pos), 2),
            "density": [round(float(d), 3) for d in current_density],
            "speed": round(float(speed), 3),
            "ambulance_speed": round(float(speed), 3)
        })

        pos += speed
        time_step += 1

    # Record final arrival state
    history.append({
        "step": time_step,
        "position": round(float(min(pos, n - 1)), 2),
        "ambulance_pos": round(float(min(pos, n - 1)), 2),
        "density": [round(float(d), 3) for d in (effective_density_with_alert(base_density, n-1, H, alpha) if enable_alert else base_density)],
        "speed": 0.0,
        "ambulance_speed": 0.0
    })

    return history, time_step

def simulate_no_alert(base_density, maximum_speed=v_max, max_time=T_max):
    """Simulates ambulance transit through base density without digital advance alert."""
    base_density = np.asarray(base_density, dtype=float)
    if len(base_density) < 2:
        raise ValueError("base_density must contain at least 2 segments")
    pos = 0.0
    time = 0
    positions = [pos]
    while pos < len(base_density) - 1 and time < max_time:
        idx = min(int(np.floor(pos)), len(base_density) - 1)
        next_idx = min(idx + 1, len(base_density) - 1)
        speed = ambulance_speed(base_density[next_idx], maximum_speed)
        pos += speed
        positions.append(pos)
        time += 1
    return np.array(positions), time

def simulate_with_alert(
    base_density,
    H=H_default,
    alpha=alpha_default,
    maximum_speed=v_max,
    max_time=T_max,
):
    """Simulates ambulance transit through modified effective density with digital advance alert."""
    base_density = np.asarray(base_density, dtype=float)
    if len(base_density) < 2:
        raise ValueError("base_density must contain at least 2 segments")
    validate_parameters(H, alpha)
    pos = 0.0
    time = 0
    positions = [pos]
    while pos < len(base_density) - 1 and time < max_time:
        idx = min(int(np.floor(pos)), len(base_density) - 1)
        next_idx = min(idx + 1, len(base_density) - 1)
        rho_eff = effective_density_with_alert(base_density, idx, H, alpha)
        speed = ambulance_speed(rho_eff[next_idx], maximum_speed)
        pos += speed
        positions.append(pos)
        time += 1
    return np.array(positions), time

