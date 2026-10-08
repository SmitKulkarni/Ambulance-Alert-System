import numpy as np
from config import N, v_max, H_default, alpha_default, T_max

def get_base_density(n=N):
    if n < 2:
        raise ValueError("n must be at least 2")
    return np.linspace(0.2, 0.8, n)

def validate_parameters(H, alpha):
    if H < 0:
        raise ValueError("H must be >= 0")
    if not 0 <= alpha <= 1:
        raise ValueError("alpha must be between 0 and 1")

def effective_density_with_alert(base_density, ambulance_pos, H, alpha):
    validate_parameters(H, alpha)
    rho_eff = np.asarray(base_density, dtype=float).copy()
    start = max(0, int(ambulance_pos) + 1)
    end = min(int(ambulance_pos) + int(H) + 1, len(rho_eff))
    if start < end:
        rho_eff[start:end] *= (1 - alpha)
    return rho_eff

def ambulance_speed(rho_eff, maximum_speed=v_max):
    rho = float(np.clip(rho_eff, 0.0, 1.0))
    return maximum_speed * (1 - rho)

def simulate_no_alert(base_density, maximum_speed=v_max, max_time=T_max):
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
        rho_eff = effective_density_with_alert(
            base_density, idx, H, alpha
        )
        # Alert changes traffic ahead, so use the next segment.
        speed = ambulance_speed(rho_eff[next_idx], maximum_speed)
        pos += speed
        positions.append(pos)
        time += 1
    return np.array(positions), time
