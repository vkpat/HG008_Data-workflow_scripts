## This python script creates a QC table in markdown format. This markdown table can be used for the GIAB FTP README.

import json
import math
from collections import defaultdict

# Define allowed metrics and their display names for each tool.
samtools_metrics = {
    "raw total sequences": "Total raw Sequences",
    "reads mapped": "Reads mapped",
    "reads mapped and paired": "Reads mapped and paired",
    "error rate": "Percent mismatch rate",
    "average length": "Average length",
    "insert size average": "Insert size average",
    "insert size standard deviation": "Insert size standard deviation",
    "percentage of properly paired reads (%)": "Percentage of properly paired",
}

mosdepth_metrics = {
  "mean_autosome_coverage": "Mean_autosome_coverage",
}

# Additional mosdepth metrics from text file
chr4_mosdepth_coverage = {
    "diploid_mean_coverage": "diploid_mean_coverage",
    "haploid_mean_coverage": "haploid_mean_coverage"
}

# Define the fixed order for ref_id columns.
FIXED_REF_ORDER = ["GRCh37","GRCh38-GIABv3", "CHM13v2.0"]

def load_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = list(data.values())
    return data

def load_mosdepth_txt(filename):
    mosdepth_values = {}
    with open(filename, "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            mosdepth_values[key.strip()] = value.strip()
    return mosdepth_values

def reorder_entries_by_ref(entries):
    mapping = {}
    for entry in entries:
        ref = entry.get('ref_id', 'Unknown')
        if ref not in mapping:
            mapping[ref] = entry

    ordered_entries = []
    for ref in FIXED_REF_ORDER:
        if ref in mapping:
            ordered_entries.append(mapping[ref])
    for entry in entries:
        ref = entry.get('ref_id', 'Unknown')
        if ref not in FIXED_REF_ORDER:
            ordered_entries.append(entry)
    return ordered_entries


def format_value(metric_key, display_name, raw_value):
    if raw_value == '-' or raw_value is None:
        return 'NA'
    s = str(raw_value)
    try:
        if display_name in ["Total raw Sequences", "Reads mapped", "Reads mapped and paired"]:
            int_val = int(s.replace(",", ""))
            return format(int_val, ",")
        elif display_name in ["Mean_autosome_coverage", "diploid_mean_coverage", "haploid_mean_coverage"]:
            return f"{int(round(float(s)))}x"
        elif display_name == "Percent mismatch rate":
            float_val = float(s) * 100
            truncated_val = math.floor(float_val * 1000) / 1000
            result = f"{truncated_val:.2f}"
            return result + "%"
        else:
            return s
    except Exception:
        return 'NA'

def create_markdown_table(hg_id, entries, mosdepth_values):
    ordered_entries = reorder_entries_by_ref(entries)
    ref_columns = [entry.get('ref_id', 'Unknown') for entry in ordered_entries]
    header_row = ["Metric"] + ref_columns
    data_rows = []

    row = ["Mean_autosome_coverage"]
    for entry in ordered_entries:
        value = format_value("mean_autosome_coverage", "Mean_autosome_coverage", entry.get("mosdepth", {}).get("mean_autosome_coverage", '-'))
        row.append(value)
    data_rows.append(row)
    
    for metric_key, display_name in samtools_metrics.items():
        row = [display_name]
        for entry in ordered_entries:
            value = format_value(metric_key, display_name, entry.get("samtools", {}).get(metric_key, '-'))
            row.append(value)
        data_rows.append(row)
    
    row = ["Percent_mapped_reads"]
    for entry in ordered_entries:
        samtools_data = entry.get("samtools", {})
        try:
            reads = float(str(samtools_data.get("reads mapped", "0")).replace(",", ""))
            total_raw = float(str(samtools_data.get("raw total sequences", "0")).replace(",", ""))
            value = f"{(reads / total_raw) * 100:.2f}%" if total_raw > 0 else "NA"
        except Exception:
            value = "NA"
        row.append(value)
    data_rows.append(row)

    if hg_id == "HG008-T":
        for key, label in chr4_mosdepth_coverage.items():
            row = [label]
            for entry in ordered_entries:
                if entry.get("ref_id") == "GRCh38-GIABv3":
                    row.append(format_value(key, label, mosdepth_values.get(key, '-')))
                else:
                    row.append("NA")
            data_rows.append(row)
    
    
    all_rows = [header_row] + data_rows
    num_cols = len(header_row)
    col_widths = [max(len(str(row[i])) for row in all_rows) for i in range(num_cols)]
    lines = []
    lines.append("| " + " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(header_row)) + " |")
    lines.append("| " + " | ".join("-" * col_widths[i] for i in range(num_cols)) + " |")
    for row in data_rows:
        lines.append("| " + " | ".join(row[i].ljust(col_widths[i]) for i in range(num_cols)) + " |")
    return f"### HG_ID: {hg_id}\n\n" + "\n".join(lines) + "\n"

def main():
    json_file = "metrics.json"
    txt_file = "HG008-T_Element_GRCh38-GIABv3.txt"
    data = load_json(json_file)
    mosdepth_values = load_mosdepth_txt(txt_file)
    groups = defaultdict(list)
    for entry in data:
        hg_id = entry.get("HG_ID", "Unknown")
        groups[hg_id].append(entry)
    markdown_content = "# Combined Metrics Tables\n\n"
    for hg_id, entries in groups.items():
        markdown_content += create_markdown_table(hg_id, entries, mosdepth_values) + "\n---\n\n"
    with open("output.md", "w") as f:
        f.write(markdown_content)

if __name__ == "__main__":
    main()
