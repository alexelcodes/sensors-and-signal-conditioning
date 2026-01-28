import numpy as np
import matplotlib.pyplot as plt

"""
Sensitivity and linearity analysis for BME688 ethanol measurements.

- Uses steady-state mean gas resistance values from stats_summary.csv
- Fits a linear model R = a*C + b
- Evaluates linearity using residuals (errors from the fitted line):
    e_i = R_meas - R_fit
- Computes:
    * sensitivity (slope |a|)
    * residuals for each point
    * standard deviation of residuals
"""

# ---- Experimental data from stats_summary.csv ----
# Ethanol concentration in vol-%
C = np.array([1, 2, 4])

# Mean gas resistance in kOhm (steady-state tail)
R = np.array([25.81, 20.56, 14.38])

# ---- Linear fit R = a*C + b ----
a, b = np.polyfit(C, R, 1)
R_fit = a * C + b

# ---- Residuals (errors from line) ----
# e_i = R_meas - R_fit
residuals = R - R_fit

# Sample standard deviation of residuals
std_res = np.std(residuals, ddof=1)

# ---- Print results ----
print("=== Sensitivity and linearity (residual-based) ===")
print(f"Sensitivity (slope |a|): {abs(a):.2f} kΩ / %\n")

print("Residuals (R_meas - R_fit) for each concentration:")
for c, r_meas, r_fit, e in zip(C, R, R_fit, residuals):
    print(
        f"  C = {c:.0f} %: "
        f"R_meas = {r_meas:.2f} kΩ, "
        f"R_fit = {r_fit:.2f} kΩ, "
        f"residual = {e:.2f} kΩ"
    )

print(f"\nStd of residuals  : {std_res:.3f} kΩ")

# ---- Plot: sensitivity (R vs C) ----
plt.figure(figsize=(7, 5))
plt.plot(C, R, marker="o", linestyle="-", label="Measured data")
plt.plot(C, R_fit, linestyle="--",
         label=f"Linear fit: R = {a:.2f}·C + {b:.2f}")

plt.xlabel("Ethanol concentration (%)")
plt.ylabel("Gas resistance R (kΩ)")
plt.title("BME688 Sensitivity to Ethanol")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig("plots/sensitivity_R_vs_C.png", dpi=150)
plt.show()

# ---- Residual plot (linearity visualization) ----
plt.figure(figsize=(7, 4))
plt.axhline(0, linestyle="--", linewidth=1)

plt.plot(C, residuals, marker="o", linestyle="-")

plt.xlabel("Ethanol concentration (%)")
plt.ylabel("Residual R_meas - R_fit (kΩ)")
plt.title("Linearity based on residuals")
plt.grid(True)

plt.tight_layout()
plt.savefig("plots/linearity_residuals.png", dpi=150)
plt.show()
