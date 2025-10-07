import csv
from collections import defaultdict

# Path to CSV results file
CSV_FILE = "results_jdk.csv"  

# Store file-level metrics
ploc_per_file = {}
lloc_per_file = {}

# Store function-level metrics
cyclomatic_values = []
fan_in_values = []
fan_out_values = []

with open(CSV_FILE, newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        file = row["file"]

        # Convert safely to int 
        ploc = int(row["ploc_file"]) if row["ploc_file"] else 0
        lloc = int(row["lloc_file"]) if row["lloc_file"] else 0
        cc   = int(row["cyclomatic"]) if row["cyclomatic"] else 0
        fi   = int(row["fan_in"]) if row["fan_in"] else 0
        fo   = int(row["fan_out"]) if row["fan_out"] else 0

        # Collect PLOC/LLOC per file
        if file not in ploc_per_file:
            ploc_per_file[file] = ploc
        if file not in lloc_per_file:
            lloc_per_file[file] = lloc

        # Function-level metrics
        cyclomatic_values.append(cc)
        fan_in_values.append(fi)
        fan_out_values.append(fo)

# ---------- Aggregate ----------
total_ploc = sum(ploc_per_file.values())
total_lloc = sum(lloc_per_file.values())

total_cc = sum(cyclomatic_values)
avg_cc = total_cc / len(cyclomatic_values) if cyclomatic_values else 0

total_fan_in = sum(fan_in_values)
total_fan_out = sum(fan_out_values)

avg_fan_in = total_fan_in / len(fan_in_values) if fan_in_values else 0
avg_fan_out = total_fan_out / len(fan_out_values) if fan_out_values else 0

max_fan_in = max(fan_in_values) if fan_in_values else 0
max_fan_out = max(fan_out_values) if fan_out_values else 0

# ---------- Display ----------
print("Aggregate Metrics Summary")
print("────────────────────────────")
print(f"Total PLOC: {total_ploc:,}")
print(f"Total LLOC: {total_lloc:,}")
print()
print(f"Total Cyclomatic Complexity: {total_cc:,}")
print(f"Average Cyclomatic Complexity per function: {avg_cc:.2f}")
print()
print(f"Total Fan-out: {total_fan_out:,}")
print(f"Average Fan-out per function: {avg_fan_out:.2f}")
print(f"Max Fan-out (most dependent function): {max_fan_out}")
print()
print(f"Total Fan-in: {total_fan_in:,}")
print(f"Average Fan-in per function: {avg_fan_in:.2f}")
print(f"Max Fan-in (most reused function): {max_fan_in}")
