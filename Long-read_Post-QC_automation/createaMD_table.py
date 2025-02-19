## This script creates a QC table( Long-read) in markdown file that can be used for GIAB ftp site README files

import json
import os
import math
from collections import defaultdict

# Define allowed metrics and their display names for each tool.
samtools_metrics = {
    "bases mapped (cigar)": "Bases Mapped (Cigar)",
    "total length": "Total Length",
    "% mapped": "% Mapped"
}

cramino_metrics = {
    "Number of alignments": "Number of Alignments",
    "% from total reads": "Percent from Total Reads",
    "Yield [Gb]": "Yield (Gb)",
    "Mean coverage": "Mean Coverage",
    "N50": "N50",
    "Median identity": "Median Identity",

}

# Define Mosdepth metrics and their display names.
chr4_mosdepth_coverage = {
    "diploid_mean_coverage": "diploid_mean_coverage",
    "haploid_mean_coverage": "haploid_mean_coverage"
}

# Define the fixed order for ref_id columns.
FIXED_REF_ORDER = ["GRCh37", "GRCh38-GIABv3", "CHM13v2.0"]

def format_value(raw_value, suffix="", force_int=False, add_commas=True):
    if raw_value in ["-", None, ""]:
        return "NA"
    try:
        num = float(str(raw_value).split()[0].replace(",", ""))
        if force_int:
            return f"{int(num)}{suffix}"
        formatted_value = f"{num:,.2f}" if add_commas else f"{num}"
        return formatted_value.rstrip("0").rstrip(".")  # Remove trailing .00
    except ValueError:
        return "NA"

def load_mosdepth_txt(mosdepth_file):
    """Loads Mosdepth output from a given file path."""
    if not os.path.exists(mosdepth_file):
        print(f"Warning: Mosdepth file '{mosdepth_file}' not found.")
        return {}

    mosdepth_values = {}
    with open(mosdepth_file, "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            mosdepth_values[key.strip()] = value.strip()
    return mosdepth_values

def get_samtools_value(entry, metric_key):
    samtools_data = entry.get("samtools_stats", {}).get("data", {})

    # Normalize keys by stripping spaces, colons, and converting to lowercase
    normalized_keys = {key.strip(": ").lower(): key for key in samtools_data.keys()}
    lookup_key = metric_key.strip(": ").lower()

    return samtools_data.get(normalized_keys.get(lookup_key, "-"), "-").split("#")[0].strip()  # Remove inline comments

def reorder_entries_by_ref(entries):
    mapping = {entry.get('ref_id', 'Missing_ref_id'): entry for entry in entries if 'ref_id' in entry}
    ordered_entries = [mapping[ref] for ref in FIXED_REF_ORDER if ref in mapping]
    ordered_entries += [entry for entry in entries if entry.get('ref_id', 'Missing_ref_id') not in FIXED_REF_ORDER]
    return ordered_entries

def create_markdown_table(hg_id, entries, mosdepth_file):
    ordered_entries = reorder_entries_by_ref(entries)
    ref_columns = [entry.get('ref_id', 'Missing_ref_id') for entry in ordered_entries]
    header_row = ["Metric"] + ref_columns
    data_rows = []

    for metric_key, display_name in cramino_metrics.items():
        row = [display_name]
        for entry in ordered_entries:
            value = format_value(entry.get("cramino", {}).get(metric_key, '-'), 'x', force_int=True, add_commas=True) if metric_key == "Mean coverage" else format_value(entry.get("cramino", {}).get(metric_key, '-'), '')
            row.append(value)
        data_rows.append(row)

    # Add Samtools metrics at the end of the table
    for metric_key, display_name in samtools_metrics.items():
        row = [display_name]
        for entry in ordered_entries:
            if metric_key == "% mapped":
                bases_mapped = get_samtools_value(entry, "bases mapped (cigar)")
                total_length = get_samtools_value(entry, "total length")
                try:
                    percent_mapped = (float(bases_mapped.replace(",", "")) / float(total_length.replace(",", ""))) * 100 if total_length not in ["-", "NA", "0"] else "NA"
                    value = f"{percent_mapped:.2f}" if percent_mapped != "NA" else "NA"
                except ValueError:
                    value = "NA"
            else:
                value = format_value(get_samtools_value(entry, metric_key))
            row.append(value)
        data_rows.append(row)

    # Add Mosdepth Coverage Metrics only for HG008-T
    if hg_id == "HG008-T":
        mosdepth_values = load_mosdepth_txt(mosdepth_file)
        for key, label in chr4_mosdepth_coverage.items():
            row = [label]
            for entry in ordered_entries:
                if entry.get("ref_id") == "GRCh38-GIABv3":
                    row.append(format_value(mosdepth_values.get(key, '-')))
                else:
                    row.append("NA")
            data_rows.append(row)

    all_rows = [header_row] + data_rows
    col_widths = [max(len(str(row[i])) if i < len(row) else 0 for row in all_rows) for i in range(len(header_row))]
    table = ["| " + " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(header_row)) + " |",
             "| " + " | ".join("-" * col_widths[i] for i in range(len(header_row))) + " |"]
    table += ["| " + " | ".join(
        (row[i] if i < len(row) else "").ljust(col_widths[i])
        for i in range(len(header_row))
    ) + " |" for row in data_rows]
    return f"### hg_id: {hg_id}\n\n" + "\n".join(table) + "\n"

def load_json(filename):
    if not os.path.exists(filename):
        print(f"Error: JSON file '{filename}' not found.")
        return []
    
    with open(filename, 'r') as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                print("Keys found in JSON:", data.keys())  # Debugging
                samples = []
                for key, value in data.items():  # Iterate over top-level keys
                    if isinstance(value, dict) and "samples" in value:
                        samples.extend(value["samples"])  # Extract and merge samples
                return samples  # Return a combined list of all samples
            return data if isinstance(data, list) else []
        except json.JSONDecodeError as e:
            print(f"Error loading JSON: {e}")
            return []

def main():
    json_file = "output.json"
    mosdepth_file = "HG008-T_Element_GRCh38-GIABv3.txt"  # Change this to the correct path

    data = load_json(json_file)
    if not data:
        print(f"No data loaded from {json_file}. Check if the file exists and has valid data.")
        return

    groups = defaultdict(list)
    for entry in data:
        groups[entry.get("hg_id", "Unknown")].append(entry)

    markdown_content = "# Combined Metrics Tables\n\n"
    for hg_id, entries in groups.items():
        markdown_content += create_markdown_table(hg_id, entries, mosdepth_file) + "\n---\n\n"

    with open("output.md", "w") as f:
        f.write(markdown_content)
    
    print(markdown_content)

if __name__ == "__main__":
    main()
