import os
import csv
import json
import re

def parse_samtools_stats_file(stats_file):
    """Parse an existing samtools stats file to extract key metrics."""
    metrics = {}
    with open(stats_file, 'r') as f:
        for line in f:
            if line.startswith("SN"):  # SN: Summary Numbers in samtools stats
                parts = line.split("\t")
                key = parts[1].strip(":")
                value = parts[2].strip()
                metrics[key] = value
    return metrics

def parse_mosdepth_csv(csv_file):
    """Parse an existing mosdepth CSV file to extract key metrics."""
    metrics = {}
    with open(csv_file, mode='r') as f:
        reader = csv.reader(f)
        headers = next(reader)  # Capture the header row (row 1)
        values = next(reader)   # Capture the value row (row 2)

        if len(headers) == len(values):
            for i, key in enumerate(headers):
                metrics[key.strip()] = values[i].strip()
        else:
            print(f"Header and values row length mismatch in {csv_file}.")
    return metrics

def write_to_json(data, output_file):
    """Write the extracted metrics to a JSON file."""
    with open(output_file, "w") as json_file:
        json.dump(data, json_file, indent=4)

def extract_hg_id(filename):
    """Extract the HG ID from the filename (e.g., HG001, HG002)."""
    match = re.search(r'HG00[1-5]', filename)
    return match.group(0) if match else None

def process_files_in_directory(samtools_dir, mosdepth_dir):
    """Process multiple samtools stats and mosdepth CSV files from given directories."""
    all_metrics = {}

    # Process all samtools stats files
    for filename in os.listdir(samtools_dir):
        if filename.endswith("samtools_stats.txt"):  # Assuming samtools stats files are .txt
            filepath = os.path.join(samtools_dir, filename)
            samtools_metrics = parse_samtools_stats_file(filepath)
            base_filename = filename.replace(".samtools_stats.txt", "")  # Remove the suffix to get the base filename
            hg_id = extract_hg_id(base_filename)  # Extract HG ID for sorting
            if hg_id:
                all_metrics[base_filename] = {"HG_ID": hg_id, "samtools": samtools_metrics}

    # Process all mosdepth CSV files
    for filename in os.listdir(mosdepth_dir):
        if filename.endswith(".csv"):  # Assuming mosdepth output is .csv
            filepath = os.path.join(mosdepth_dir, filename)
            mosdepth_metrics = parse_mosdepth_csv(filepath)
            base_filename = filename.replace(".mosdepth.csv", "")  # Remove the suffix to get the base filename
            hg_id = extract_hg_id(base_filename)  # Extract HG ID for sorting
            if hg_id:
                # Append mosdepth metrics to the corresponding samtools entry (if exists)
                if base_filename in all_metrics:
                    all_metrics[base_filename]["mosdepth"] = mosdepth_metrics
                else:
                    all_metrics[base_filename] = {"HG_ID": hg_id, "mosdepth": mosdepth_metrics}

    # Sort all_metrics by HG_ID
    sorted_metrics = dict(sorted(all_metrics.items(), key=lambda item: item[1]["HG_ID"]))
    
    return sorted_metrics

def main():
    # Directories containing samtools and mosdepth files
    samtools_stats_dir = "/scratch2/HG008_Data_QC-stats_files/RM_data/Element_AVITI_20240920/HG001-5_Element_LngInsert/QC_stats"  # Replace with actual directory
    mosdepth_csv_dir = "/scratch2/HG008_Data_QC-stats_files/RM_data/Element_AVITI_20240920/HG001-5_Element_LngInsert/QC_stats"  # Replace with actual directory

    # Extract and merge metrics from samtools and mosdepth files
    sorted_metrics = process_files_in_directory(samtools_stats_dir, mosdepth_csv_dir)

    # Output JSON file
    json_output = "HG001-5_combined_metrics_LngInsert.json"
    
    # Write the combined metrics to JSON
    write_to_json(sorted_metrics, json_output)

    print(f"Metrics extracted and written to {json_output} in sorted order.")

if __name__ == "__main__":
    main()

