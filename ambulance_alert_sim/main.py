import os
import matplotlib.pyplot as plt
from simulator import (
    get_base_density,
    simulate_no_alert,
    simulate_with_alert,
)
from config import H_default, alpha_default

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.join(BASE_DIR, "plots")

def main():
    os.makedirs(PLOTS_DIR, exist_ok=True)
    base_density = get_base_density()
    positions_no, time_no = simulate_no_alert(base_density)
    positions_alert, time_alert = simulate_with_alert(
        base_density,
        H=H_default,
        alpha=alpha_default,
    )
    time_saved = time_no - time_alert
    print("=== Ambulance Alert Simulation ===")
    print(f"Travel time (no alert): {time_no} time steps")
    print(f"Travel time (with alert): {time_alert} time steps")
    print(f"Time saved: {time_saved} time steps")
    if time_no:
        print(f"Improvement: {100*time_saved/time_no:.2f}%")
    plt.figure(figsize=(8, 5))
    plt.plot(range(len(positions_no)), positions_no, label="No alert")
    plt.plot(
        range(len(positions_alert)),
        positions_alert,
        label="With advance alert",
    )
    plt.xlabel("Time step")
    plt.ylabel("Ambulance position (segment)")
    plt.title("Ambulance movement: No alert vs Advance alert")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    save_path = os.path.join(PLOTS_DIR, "ambulance_comparison.png")
    plt.savefig(save_path, dpi=150)
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
    main()
