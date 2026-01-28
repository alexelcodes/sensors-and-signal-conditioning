import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------------------
# File locations for dynamic raw CSV plots
# -----------------------------------------
FILES = {
    "9°C":  "logs/20251205_1450_reprod_9C.csv",
    "25°C": "logs/20251205_1547_reprod_25C.csv",
    "45°C": "logs/20251205_1639_reprod_45C.csv",
}

STATS_PATH = Path("stats_summary.csv")


# -----------------------------------------
# Load raw CSV (full dynamic time series)
# -----------------------------------------
def load_raw_file(path):
    """Load a raw CSV log from the sensor and convert fields to numeric."""
    df = pd.read_csv(path, sep=";", names=[
        "timestamp_ms", "temperature_C", "humidity_pct",
        "pressure_hPa", "gas_ohm"
    ], header=None)

    df = df.apply(pd.to_numeric, errors="coerce")
    df["time_s"] = df["timestamp_ms"] / 1000.0
    df["gas_kohm"] = df["gas_ohm"] / 1000.0
    return df


# -----------------------------------------
# Plot the dynamic responses for 9/25/45°C
# -----------------------------------------
def plot_dynamic_responses():
    plt.figure(figsize=(10, 6))

    for label, path in FILES.items():
        df = load_raw_file(path)
        plt.plot(df["time_s"], df["gas_kohm"], linewidth=1.4, label=label)

    plt.xlabel("Time (s)")
    plt.ylabel("Gas resistance (kΩ)")
    plt.title("Dynamic sensor response at 9°C, 25°C, and 45°C")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    out = Path("plots/reprod_dynamic_response.png")
    out.parent.mkdir(exist_ok=True)
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Saved: {out}")


# -----------------------------------------
# Plot reproducibility summary (steady-state)
# -----------------------------------------
def plot_reproducibility_summary():
    df = pd.read_csv(STATS_PATH, sep=";")
    df = df[df["type"] == "Reproducibility"].copy()

    T = df["T_mean"].values
    R = df["Rgas_kohm_mean"].values

    # Linear fit R(T)
    a, b = np.polyfit(T, R, 1)
    T_line = np.linspace(T.min() - 2, T.max() + 2, 200)
    R_line = a * T_line + b

    # Reproducibility (k=2)
    std = R.std(ddof=1)
    U = 2 * std  # expanded uncertainty (k=2)

    plt.figure(figsize=(8, 6))
    plt.scatter(T, R, s=80, color="black", label="Steady-state means")
    plt.plot(T_line, R_line, "--", label=f"Fit: R = {a:.3f}·T + {b:.2f}")

    # Error bars ±U/2 centered around each point
    plt.errorbar(T, R, yerr=U / 2, fmt='none', ecolor="red",
                 label=f"Reproducibility (k=2): U = {U:.3f} kΩ")

    plt.xlabel("Ambient temperature (°C)")
    plt.ylabel("Gas resistance (kΩ)")
    plt.title("Reproducibility summary (9–45°C)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    out = Path("plots/reprod_summary.png")
    out.parent.mkdir(exist_ok=True)
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Saved: {out}")


# -----------------------------------------
# MAIN
# -----------------------------------------
def main():
    print("\n=== GENERATING REPRODUCIBILITY FIGURES ===\n")

    # 1) Full dynamic time-series plot
    plot_dynamic_responses()

    # 2) Steady-state reproducibility summary
    plot_reproducibility_summary()

    print("\nAll figures saved to /plots\n")


if __name__ == "__main__":
    main()
