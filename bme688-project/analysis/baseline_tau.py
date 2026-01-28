import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def compute_tau(time_s, R):
    """
    Compute time constant tau for a first-order-like response.

    time_s : 1D array of time in seconds
    R      : 1D array of gas resistance (Ohm or kOhm, units do not matter)

    Returns:
        tau_s        : time constant in seconds
        R0           : initial level (mean of first samples)
        R_inf        : final level (mean of tail)
        t_tau        : time at which curve reaches 63.2% of total change
        R_tau_target : ideal R(tau) from formula
        R_tau_actual : R value at the picked index
    """
    # Number of points for initial part and tail (steady state)
    N_START = min(10, len(R))     # first 10 samples (or less if file is short)
    N_TAIL = min(200, len(R))     # last 200 samples (or less if file is short)

    R0 = R[:N_START].mean()
    R_inf = R[-N_TAIL:].mean()

    # Ideal 63.2% level for first-order system
    R_tau_target = R0 + 0.632 * (R_inf - R0)

    # Decide direction: rising or falling
    if R_inf >= R0:
        # Rising response: look for first time R >= R_tau_target
        mask = R >= R_tau_target
    else:
        # Falling response: look for first time R <= R_tau_target
        mask = R <= R_tau_target

    if mask.any():
        idx_tau = np.argmax(mask)  # index of first True
    else:
        # Fallback: choose sample closest to R_tau_target
        idx_tau = np.argmin(np.abs(R - R_tau_target))

    t_tau = time_s[idx_tau]
    R_tau_actual = R[idx_tau]

    tau_s = t_tau  # time constant in seconds (starting from t=0)

    return tau_s, R0, R_inf, t_tau, R_tau_target, R_tau_actual


def main():
    if len(sys.argv) < 2:
        print("Usage: python baseline_tau.py logs/2025xxxxx_baseline.csv")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"File not found: {csv_path}")
        sys.exit(1)

    # Read baseline CSV
    df = pd.read_csv(csv_path, sep=";")

    # Time in seconds
    time_s = df["timestamp_ms"].values / 1000.0

    # Use gas resistance (convert to kOhm for nicer numbers)
    R_kohm = df["gas_ohm"].values / 1000.0

    # Compute tau and related values
    tau_s, R0, R_inf, t_tau, R_tau_target, R_tau_actual = compute_tau(time_s, R_kohm)

    # --- 3 * tau point ---
    t_3tau = 3 * tau_s
    idx_3tau = np.argmin(np.abs(time_s - t_3tau))
    t_3tau_actual = time_s[idx_3tau]
    R_3tau_actual = R_kohm[idx_3tau]
    R_3tau_theory = R0 + 0.95 * (R_inf - R0)

    frac_change = (R_3tau_actual - R0) / (R_inf - R0) * 100.0

    print("\n=== Baseline time constant (tau) ===")
    print(f"File            : {csv_path.name}")
    print(f"R0 (start)      : {R0:.2f} kΩ")
    print(f"R_inf (plateau) : {R_inf:.2f} kΩ")
    print(f"R_tau (target)  : {R_tau_target:.2f} kΩ")
    print(f"R_tau (actual)  : {R_tau_actual:.2f} kΩ")
    print(f"tau             : {tau_s:.1f} s (time when curve reaches 63.2% of total change)")

    print("\n=== Check at 3 * tau ===")
    print(f"3τ time (target)        : {t_3tau:.1f} s")
    print(f"3τ time (nearest sample): {t_3tau_actual:.1f} s")
    print(f"R(3τ) theory (95%)      : {R_3tau_theory:.2f} kΩ")
    print(f"R(3τ) actual            : {R_3tau_actual:.2f} kΩ")
    print(f"Actual change vs span   : {frac_change:.1f} % of (R_inf - R0)")

    # ---------- Plot ----------
    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)

    plt.figure(figsize=(10, 5))
    plt.plot(time_s, R_kohm, label="Gas resistance (baseline)")
    plt.axhline(R0, linestyle="--", label=f"R0 = {R0:.2f} kΩ")
    plt.axhline(R_inf, linestyle="--", label=f"R_inf = {R_inf:.2f} kΩ")
    plt.axhline(R_tau_target, linestyle=":", label=f"R_tau target = {R_tau_target:.2f} kΩ")

    # tau marker
    plt.axvline(t_tau, linestyle=":", label=f"tau ≈ {tau_s:.1f} s")
    plt.plot(t_tau, R_tau_actual, "o", label="Chosen tau point")

    # 3 * tau marker
    plt.axvline(t_3tau_actual, linestyle=":", label=f"3τ ≈ {t_3tau_actual:.1f} s")
    plt.plot(t_3tau_actual, R_3tau_actual, "s", label="Point at 3τ")

    plt.xlabel("Time (s)")
    plt.ylabel("Gas resistance (kΩ)")
    plt.title("Baseline response, time constant τ and 3τ")
    plt.grid(True)
    plt.legend()

    out_path = plots_dir / f"{csv_path.stem}_tau.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    print(f"\nSaved plot with tau and 3τ markers to: {out_path}")


if __name__ == "__main__":
    main()
