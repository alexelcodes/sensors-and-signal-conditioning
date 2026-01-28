import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 2:
        print("Usage: python repeatability.py logs/repeatability_1pct.csv")
        return

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path, sep=";")

    time_s = df["timestamp_ms"].values / 1000.0
    R = df["gas_ohm"].values / 1000.0  # kΩ

    # --- Take last 200 points ---
    N_TAIL = 200
    R_tail = R[-N_TAIL:]
    time_tail = time_s[-N_TAIL:]

    # --- Repeatability statistics ---
    mean_R = R_tail.mean()
    std_R = R_tail.std(ddof=1)
    U_k2 = 2 * std_R

    print("\n=== Repeatability (tail-based) ===")
    print(f"File                : {csv_path.name}")
    print(f"Tail samples        : {len(R_tail)}")
    print(f"Mean R (tail)       : {mean_R:.3f} kΩ")
    print(f"Std  (s)            : {std_R:.3f} kΩ")
    print(f"Expanded uncertainty U (k=2): {U_k2:.3f} kΩ")

    print("R_tail min:", R_tail.min())
    print("R_tail max:", R_tail.max())
    print("Mean R:", mean_R)

    # --- Plot tail only ---
    Path("plots").mkdir(exist_ok=True)

    plt.figure(figsize=(9, 4))
    plt.plot(time_tail, R_tail, label="Tail gas resistance")
    plt.axhline(mean_R, linestyle="--", label=f"Mean = {mean_R:.2f} kΩ")

    plt.xlabel("Time (s)")
    plt.ylabel("Gas resistance (kΩ)")
    plt.title("Repeatability – steady-state tail (1% ethanol)")
    plt.grid(True)
    plt.legend()

    out_path = Path("plots") / f"{csv_path.stem}_repeatability.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    print(f"Saved plot: {out_path}")

if __name__ == "__main__":
    main()
