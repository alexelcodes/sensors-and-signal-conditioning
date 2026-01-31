# Sensors and Signal Conditioning

<p align="center">
  <img src="https://img.shields.io/badge/Environment-Conda-44A833" />
  <img src="https://img.shields.io/badge/Jupyter-Notebooks-orange" />
  <img src="https://img.shields.io/badge/Signal%20Processing-Filters%20%26%20ADC-informational" />
  <img src="https://img.shields.io/badge/ESP32--C6-ESP--IDF-success" />
  <img src="https://img.shields.io/badge/Sensor-BME688-lightgrey" />
</p>

This repository contains coursework and an applied project focused on sensor signal chains, analog-to-digital conversion, noise reduction, and data analysis, combining theoretical concepts with hands-on experimentation.

---

## Contents

### Applied project: BME688 sensor evaluation

Course project using a **Bosch BME688** environmental sensor and an **ESP32-C6** platform.

Includes:

- ESP-IDF firmware (C)
- automated data logging
- Python-based analysis and plotting
- sensitivity, linearity, repeatability, and reproducibility evaluation
- custom 3D-printed measurement chamber

→ Full report: [`bme688-project/README.md`](bme688-project/README.md)

---

### Course notebooks

- sensor fundamentals and signal chains
- measurements and basic metrology
- resistive sensors
- sampling and ADCs
- digital filters
- Kalman filters

→ See [`course-notebooks`](course-notebooks)

---

## Tools and technologies

- Python (NumPy, Pandas, SciPy, Matplotlib)
- Jupyter Notebooks
- Embedded C (ESP-IDF)
- Signal processing and sensor data analysis

---

## Setup

### Conda

This project uses a **conda environment** for reproducible Python dependencies.

#### 1. Install conda

Install **Miniforge** (recommended) or another conda distribution:

- https://github.com/conda-forge/miniforge

> Conda is used to avoid compatibility issues with scientific Python libraries.

#### 2. Create the environment

From the repository root, create the environment using the provided `environment.yml`:

```bash
conda env create -f environment.yml
```

This will create a conda environment named ssc.

#### 3. Activate the environment

```bash
conda activate ssc
```

#### 4. Select the kernel

In **VS Code** or **Jupyter**, select:

`ssc (Python 3.12)`

as the notebook kernel.

## Notes

- Recommended Python version: 3.12
- Conda is recommended for maximum reproducibility.
