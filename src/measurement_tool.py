import argparse
import csv
from file_scanner import get_source_files
from loc_counter import analyze_file, compute_fan_in_out

def main():
    parser = argparse.ArgumentParser(description="Measure LOC, McCabe complexity, Fan-in, Fan-out metrics.")
    parser.add_argument("--repo", type=str, required=True, help="Path to repo or single source file")
    parser.add_argument("--out", type=str, default="results.csv", help="Output CSV file name")
    args = parser.parse_args()

    # Scan all source files
    source_files = get_source_files(args.repo)
    if not source_files:
        print("No supported source files found.")
        return

    all_rows = []  

    # Analyze each file individually 
    for file_path in source_files:
        rows, _ = analyze_file(file_path)
        all_rows.extend(rows)

    # Compute fan-in / fan-out across the whole repo
    fan_in_map, fan_out_map = compute_fan_in_out(source_files)

    # Merge fan-in/out data into results
    for row in all_rows:
        func_name = row["function"].split("(")[0].split()[-1].strip()
        row["fan_in"] = fan_in_map.get(func_name, 0)
        row["fan_out"] = fan_out_map.get(func_name, 0)

    # Save final results to CSV
    save_results_to_csv(all_rows, args.out)

    print(f"Analysis complete! {len(source_files)} files processed, "
          f"{sum(1 for r in all_rows if r.get('function'))} functions analyzed.")
    print(f"Results saved to: {args.out}")


def save_results_to_csv(results, output_file):
    if not results:
        print("No results to save.")
        return

    # Merge all keys to get a complete header
    fieldnames = set()
    for r in results:
        fieldnames.update(r.keys())
    fieldnames = list(fieldnames)

    # Preferred column order
    preferred_order = [
        "file", "language", "function", "signature",
        "ploc_file", "lloc_file", "cyclomatic",
        "fan_in", "fan_out"
    ]
    fieldnames = [f for f in preferred_order if f in fieldnames] + \
                 [f for f in fieldnames if f not in preferred_order]

    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


if __name__ == "__main__":
    main()
