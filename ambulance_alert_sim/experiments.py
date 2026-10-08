import csv
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
RESULTS_DIR = os.path.join(BASE_DIR, "results")

def save_csv(filename, header, rows):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

def run_experiments():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)
    density = get_base_density()
    _, time_no = simulate_no_alert(density)
    
    # Experiment 1: alert horizon
    H_values = [0, 1, 2, 3, 4, 5]
    alpha_fixed = alpha_default
    rows_H = []
    for H in H_values:
        _, t = simulate_with_alert(
            density, H=H, alpha=alpha_fixed
        )
        rows_H.append([H, t, time_no - t])
        
    # Experiment 2: cooperation
    alpha_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    H_fixed = H_default
    rows_alpha = []
    for alpha in alpha_values:
        _, t = simulate_with_alert(
            density, H=H_fixed, alpha=alpha
        )
        rows_alpha.append([alpha, t, time_no - t])
        
    save_csv(
        os.path.join(RESULTS_DIR, "results_H.csv"),
        ["H", "time_with_alert", "time_saved"],
        rows_H,
    )
    save_csv(
        os.path.join(RESULTS_DIR, "results_alpha.csv"),
        ["alpha", "time_with_alert", "time_saved"],
        rows_alpha,
    )
    
    summary_path = os.path.join(RESULTS_DIR, "summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"Baseline: {time_no}\n\n")
        f.write("H experiment\n")
        f.write("H\tTime_with_alert\tTime_saved\n")
        for row in rows_H:
            f.write(f"{row[0]}\t{row[1]}\t{row[2]}\n")
        f.write("\nAlpha experiment\n")
        f.write("alpha\tTime_with_alert\tTime_saved\n")
        for row in rows_alpha:
            f.write(f"{row[0]}\t{row[1]}\t{row[2]}\n")
            
    H_saved = [r[2] for r in rows_H]
    A_saved = [r[2] for r in rows_alpha]
    
    plt.figure(figsize=(7, 4.5))
    plt.plot(H_values, H_saved, marker="o")
    plt.xlabel("Alert horizon H (segments)")
    plt.ylabel("Time saved (time steps)")
    plt.title(f"Effect of Alert Horizon (alpha={alpha_fixed})")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "time_saved_vs_H.png"), dpi=150)
    plt.close()
    
    plt.figure(figsize=(7, 4.5))
    plt.plot(alpha_values, A_saved, marker="s")
    plt.xlabel("Cooperation factor alpha")
    plt.ylabel("Time saved (time steps)")
    plt.title(f"Effect of Driver Cooperation (H={H_fixed})")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "time_saved_vs_alpha.png"), dpi=150)
    plt.close()
        
    print("Experiments completed. Check results/ and plots/.")

if __name__ == "__main__":
    run_experiments()
