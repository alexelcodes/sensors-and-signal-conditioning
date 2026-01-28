import pandas as pd
import matplotlib.pyplot as plt
import sys
from pathlib import Path


# ---------------------------
# Helper: detect measurement type from filename
# ---------------------------
def detect_type(filename: str) -> str:
    name = filename.lower()

    if "baseline" in name:
        return "Baseline (air)"
    if "sens_" in name:
        return "Sensitivity & Linearity"
    if "repeat_" in name:
        return "Repeatability"
    if "reprod_" in name:
        return "Reproducibility"
    
    return "Unknown"


# ---------------------------
# Process a single CSV file
# ---------------------------
def analyze_file(path: Path, plots_dir: Path, summary_path: Path):
    print(f"\nProcessing: {path.name}")

    df = pd.read_csv(path, sep=";")

    # Convert milliseconds to seconds
    df["time_s"] = df["timestamp_ms"] / 1000.0

    # Convert gas resistance from ohms to kilo-ohms
    df["gas_kohm"] = df["gas_ohm"] / 1000.0

    measurement_type = detect_type(path.name)
    print(f"Measurement type: {measurement_type}")

    # ---------------------------
    # Choose tail data
    # ---------------------------
    TAIL_NUM = 200

    stats_df = df.tail(TAIL_NUM).copy()
    print(f"Using last {len(stats_df)} samples for stats (tail).")

    # ---- numeric summary to terminal (based on stats_df) ----
    summary_cols = ["temperature_C", "humidity_pct", "pressure_hPa", "gas_kohm"]
    summary = stats_df[summary_cols].agg(["count", "mean", "std", "min", "max"]).round(2)
    print(summary)

    # ---------------------------
    # Save compact summary to CSV file
    # ---------------------------
    row = {
        "file": path.name,
        "type": measurement_type,
        "T_mean": round(stats_df["temperature_C"].mean(), 2),
        "T_std": round(stats_df["temperature_C"].std(ddof=1), 2),
        "RH_mean": round(stats_df["humidity_pct"].mean(), 2),
        "RH_std": round(stats_df["humidity_pct"].std(ddof=1), 2),
        "P_mean": round(stats_df["pressure_hPa"].mean(), 2),
        "P_std": round(stats_df["pressure_hPa"].std(ddof=1), 2),
        "Rgas_kohm_mean": round(stats_df["gas_kohm"].mean(), 2),
        "Rgas_kohm_std": round(stats_df["gas_kohm"].std(ddof=1), 2),
    }

    row_df = pd.DataFrame([row])

    header = not summary_path.exists()
    row_df.to_csv(summary_path, sep=";", index=False, mode="a", header=header)

    print(f"Appended stats to: {summary_path}")

    # ---------------------------
    # Plots
    # ---------------------------
    
    # Always plot gas resistance
    plt.figure(figsize=(10, 5))
    plt.plot(df["time_s"], df["gas_kohm"])
    plt.xlabel("Time (s)")
    plt.ylabel("Gas resistance (kΩ)")
    plt.title(f"Gas resistance — {path.name}")
    plt.grid(True)

    out = plots_dir / f"{path.stem}_gas.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Saved plot: {out}")

    # Sensitivity & linearity → humidity only
    if "Sensitivity" in measurement_type:
        plt.figure(figsize=(10, 5))
        plt.plot(df["time_s"], df["humidity_pct"])
        plt.xlabel("Time (s)")
        plt.ylabel("Relative humidity (%)")
        plt.title(f"Humidity — {path.name}")
        plt.grid(True)

        out = plots_dir / f"{path.stem}_hum.png"
        plt.savefig(out, dpi=150)
        plt.close()
        print(f"Saved plot: {out}")

    # Baseline, repeatability, reproducibility → temperature + humidity
    else:
        # Temperature
        plt.figure(figsize=(10, 5))
        plt.plot(df["time_s"], df["temperature_C"])
        plt.xlabel("Time (s)")
        plt.ylabel("Temperature (°C)")
        plt.title(f"Temperature — {path.name}")
        plt.grid(True)

        out = plots_dir / f"{path.stem}_temp.png"
        plt.savefig(out, dpi=150)
        plt.close()
        print(f"Saved plot: {out}")

        # Humidity
        plt.figure(figsize=(10, 5))
        plt.plot(df["time_s"], df["humidity_pct"])
        plt.xlabel("Time (s)")
        plt.ylabel("Relative humidity (%)")
        plt.title(f"Humidity — {path.name}")
        plt.grid(True)

        out = plots_dir / f"{path.stem}_hum.png"
        plt.savefig(out, dpi=150)
        plt.close()
        print(f"Saved plot: {out}")


# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze.py file1.csv file2.csv ...")
        sys.exit(1)

    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)

    summary_path = Path("stats_summary.csv")

    for f in sys.argv[1:]:
        path = Path(f)
        if not path.exists():
            print(f"File not found: {path}")
            continue

        analyze_file(path, plots_dir, summary_path)