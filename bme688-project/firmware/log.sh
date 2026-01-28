#!/bin/bash
# Read ESP32-C6 BME688 output and save it to a CSV file

mkdir -p ../logs

echo "Suggested labels:"
echo "  baseline           - clean air in chamber"
echo "  sens_1pct          - ~1% EtOH (1 drop EtOH + 39 drops water)"
echo "  sens_2pct          - ~2% EtOH (1 drop EtOH + 19 drops water)"
echo "  sens_4pct          - ~4% EtOH (1 drop EtOH + 9 drops water))"
echo "  repeat_1pct        - repeatability at ~1% EtOH"
echo "  reprod_9C          - reproducibility at ~9°C"
echo "  reprod_25C         - reproducibility at ~25°C"
echo "  reprod_45C         - reproducibility at ~45°C"
echo

# Ask user for label
read -p "Enter label for this measurement [baseline/sens_1pct/...]: " label
if [ -z "$label" ]; then
    label="nolabel"
fi

# Base filename (without extension)
timestamp=$(date +%Y%m%d_%H%M)
base="../logs/${timestamp}_${label}"
outfile="${base}.csv"

# Avoid overwriting existing files
idx=1
while [ -e "$outfile" ]; do
    outfile="${base}_${idx}.csv"
    idx=$((idx + 1))
done

header="timestamp_ms;temperature_C;humidity_pct;pressure_hPa;gas_ohm"

echo "----------------------------------------"
echo "Logging to file: $outfile"
echo "CSV header:      $header"
echo "Press Ctrl+C to stop logging."
echo "----------------------------------------"

# Header
echo "$header" | tee "$outfile"

# Run ESP-IDF monitor, clean color codes, keep valid CSV rows, and save to file

idf.py monitor 2>/dev/null | \
sed -u $'s/\x1b\\[[0-9;]*m//g' | \
awk -v hdr="$header" '
  BEGIN { FS=OFS=";" }
  $0 == hdr { next }
  /^[0-9]+;[^;]+;[^;]+;[^;]+;[^;]+$/ {
    gsub("\r", "")
    print; fflush()
  }
' | tee -a "$outfile"