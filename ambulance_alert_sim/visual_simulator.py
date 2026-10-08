import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from simulator import (
    get_base_density,
    effective_density_with_alert,
    ambulance_speed,
)
from config import N, v_max, H_default, alpha_default, T_max

def run_step_by_step_simulation(enable_alert=True):
    base_density = get_base_density(N)
    pos = 0.0
    history = []
    time_step = 0
    while pos < len(base_density) - 1 and time_step < T_max:
        idx = min(int(np.floor(pos)), len(base_density) - 1)
        next_idx = min(idx + 1, len(base_density) - 1)
        
        if enable_alert:
            current_density = effective_density_with_alert(base_density, idx, H_default, alpha_default)
        else:
            current_density = base_density.copy()
            
        speed = ambulance_speed(current_density[next_idx], v_max)
        history.append({
            'time': time_step,
            'pos': pos,
            'idx': idx,
            'density': current_density.copy(),
            'alert_active': enable_alert
        })
        pos += speed
        time_step += 1
        
    return history, time_step

def run_live_corridor_animation():
    hist_no_alert, time_no = run_step_by_step_simulation(enable_alert=False)
    hist_alert, time_alert = run_step_by_step_simulation(enable_alert=True)
    max_frames = max(len(hist_no_alert), len(hist_alert))

    # Setup the visual window: Corridor Road on top, Progress Graph on bottom
    fig, (ax_road, ax_graph) = plt.subplots(2, 1, figsize=(12, 7), gridspec_kw={'height_ratios': [1, 1.2]})
    try:
        fig.canvas.manager.set_window_title("Ambulance Corridor Live Simulation Visualizer")
    except Exception:
        pass

    # --- Top Plot: Road Visualizer ---
    ax_road.set_xlim(-0.5, N - 0.5)
    ax_road.set_ylim(-0.8, 1.8)
    ax_road.set_yticks([0, 1])
    ax_road.set_yticklabels(['Baseline (No Alert)', 'Smart Alert Active'], fontsize=10)
    ax_road.set_xlabel("Corridor Segment Index (0 to 19)", fontsize=10)
    ax_road.set_title("Real-Time Corridor Traffic Density & Ambulance Positions", fontsize=11, fontweight='bold')
    ax_road.grid(True, axis='x', linestyle='--', alpha=0.5)

    # Segment background bars
    bars_no = ax_road.bar(range(N), [0.35]*N, bottom=-0.175, color='gray', alpha=0.6, edgecolor='black')
    bars_alert = ax_road.bar(range(N), [0.35]*N, bottom=0.825, color='gray', alpha=0.6, edgecolor='black')

    # Ambulance markers
    amb_no, = ax_road.plot([], [], marker='s', markersize=14, color='darkred', label='Ambulance (Baseline)')
    amb_alert, = ax_road.plot([], [], marker='s', markersize=14, color='crimson', label='Ambulance (Alert)')

    status_text = ax_road.text(0.02, 0.90, '', transform=ax_road.transAxes,
                               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # --- Bottom Plot: Real-time Trajectory Graph ---
    ax_graph.set_xlim(0, max_frames + 2)
    ax_graph.set_ylim(0, N)
    ax_graph.set_xlabel("Time Step", fontsize=10)
    ax_graph.set_ylabel("Corridor Position (Segments)", fontsize=10)
    ax_graph.grid(True, linestyle=':', alpha=0.7)

    line_no, = ax_graph.plot([], [], color='#1f77b4', linewidth=2, label=f'No Alert (Total: {time_no} steps)')
    line_alert, = ax_graph.plot([], [], color='#2ca02c', linewidth=2, label=f'With Alert (Total: {time_alert} steps)')
    ax_graph.legend(loc='lower right')

    x_data_no, y_data_no = [], []
    x_data_alert, y_data_alert = [], []

    def update(frame):
        # Update Baseline
        f_no = min(frame, len(hist_no_alert) - 1)
        state_no = hist_no_alert[f_no]
        amb_no.set_data([state_no['pos']], [0])
        for i, bar in enumerate(bars_no):
            density = state_no['density'][i]
            bar.set_color(plt.cm.Reds(density * 0.8 + 0.1))

        # Update Alert Active
        f_al = min(frame, len(hist_alert) - 1)
        state_al = hist_alert[f_al]
        amb_alert.set_data([state_al['pos']], [1])
        for i, bar in enumerate(bars_alert):
            density = state_al['density'][i]
            # Green tint if alerted segments are cleared
            bar.set_color(plt.cm.Greens(1.0 - density))

        # Update Bottom Graph Lines
        if frame < len(hist_no_alert):
            x_data_no.append(state_no['time'])
            y_data_no.append(state_no['pos'])
            line_no.set_data(x_data_no, y_data_no)

        if frame < len(hist_alert):
            x_data_alert.append(state_al['time'])
            y_data_alert.append(state_al['pos'])
            line_alert.set_data(x_data_alert, y_data_alert)

        # Update summary text
        status_text.set_text(
            f"Step: {frame} | "
            f"Alert Pos: {state_al['pos']:.1f}/{N-1} | "
            f"No-Alert Pos: {state_no['pos']:.1f}/{N-1}"
        )

        return [amb_no, amb_alert, line_no, line_alert, status_text] + list(bars_no) + list(bars_alert)

    ani = animation.FuncAnimation(
        fig, update, frames=max_frames, interval=120, repeat=False, blit=False
    )
    plt.tight_layout()
    try:
        import matplotlib
        if matplotlib.get_backend().lower() not in ["agg", "template"]:
            plt.show(block=False)
            plt.pause(1)
            plt.close("all")
        else:
            plt.show()
    except Exception:
        plt.close("all")

if __name__ == "__main__":
    run_live_corridor_animation()
