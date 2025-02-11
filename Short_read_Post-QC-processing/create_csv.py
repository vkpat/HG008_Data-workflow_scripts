## This script creates a csv file with all the metrics from samtools and mosdepth for Tumor/Normal manifest document. This can be also used to send collaborator a QC table with all the metrics

import json
import math
import csv
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
chr4_mosdepth_calculation = {
   "diploid_mean_coverage": "diploid_mean_coverage",
    "haploid_mean_coverage": "haploid_mean_coverage"
}

# Define the fixed order for ref_id columns.
FIXED_REF_ORDER = ["GRCh38-GIABv3", "GRCh37", "CHM13v2.0"]

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

def reorder_entries(entries):
    sorted_entries = sorted(entries, key=lambda x: (x.get("HG_ID", "Unknown"), FIXED_REF_ORDER.index(x.get("ref_id", "Unknown")) if x.get("ref_id", "Unknown") in FIXED_REF_ORDER else len(FIXED_REF_ORDER)))
    return sorted_entries

def format_value(metric_key, display_name, raw_value):
    if raw_value == '-' or raw_value is None:
        return 'NA'
    s = str(raw_value)
    try:
        if display_name in ["Total raw Sequences", "Reads mapped", "Reads mapped and paired"]:
            return s.replace(",", "")  # Keep original value
        elif display_name in ["Mean_autosome_coverage", "diploid_mean_coverage", "haploid_mean_coverage"]:
            return s  # Keep original float value
        elif display_name == "Percent mismatch rate":
            return f"{float(s) * 100:.2f}"  # Extract exact float value
        elif display_name == "percent_mapped_reads":
            return f"{float(s):.2f}"  # Keep percent format
        else:
            return s
    except Exception:
        return 'NA'

def create_csv_table(entries, mosdepth_values):
    ordered_entries = reorder_entries(entries)
    header_row = ["HG_ID", "Ref_ID"] + list(samtools_metrics.values()) + ["mean_autosome_coverage","percent_mapped_reads" ,"diploid_mean_coverage", "haploid_mean_coverage","tumor_ploidy_short","NRPCC"]
    data_rows = []
    
    for entry in ordered_entries:
        row = [entry.get("HG_ID", "Unknown"), entry.get("ref_id", "Unknown")]
        for metric_key, display_name in samtools_metrics.items():
            row.append(format_value(metric_key, display_name, entry.get("samtools", {}).get(metric_key, '-')))
        row.append(format_value("mean_autosome_coverage", "Mean_autosome_coverage", entry.get("mosdepth", {}).get("mean_autosome_coverage", '-')))
        
         # Compute Percent Mapped
        samtools_data = entry.get("samtools", {})
        reads = samtools_data.get("reads mapped", "0").replace(",", "")
        total_raw = samtools_data.get("raw total sequences", "0").replace(",", "")
        try:
            percent_mapped = (float(reads) / float(total_raw) * 100) if float(total_raw) > 0 else "NA"
        except Exception:
            percent_mapped = "NA"
        row.append(format_value("percent_mapped", "percent_mapped_reads", percent_mapped))
        

        if entry.get("HG_ID") == "HG008-T" and entry.get("ref_id") == "GRCh38-GIABv3":
            mosdepth_1_value = mosdepth_values.get("diploid_mean_coverage", "-")
            mosdepth_2_value = mosdepth_values.get("haploid_mean_coverage", "-")
            row.append(format_value("diploid_mean_coverage", "diploid_mean_coverage", mosdepth_1_value))
            row.append(format_value("haploid_mean_coverage", "haploid_mean_coverage", mosdepth_2_value))
            

             # Compute tumor_ploidy_short = (mean_autosome_coverage / Mosdepth_1) / 2
            autosome_coverage_value = entry.get("mosdepth", {}).get("mean_autosome_coverage", "-")
            try:
                autosome_coverage_value = float(autosome_coverage_value) if autosome_coverage_value not in ["NA", "-"] else "NA"
                mosdepth_2_value = float(mosdepth_2_value) if mosdepth_2_value not in ["NA", "-"] else "NA"
                po_value = (autosome_coverage_value / mosdepth_2_value) * 2 if mosdepth_2_value != "NA" else "NA"
            except Exception:
                po_value = "NA"
            row.append(format_value("po", "tumor_ploidy_short", po_value))

            # Compute NRPCC = haploid_mean_coverage / 2
            try:
                additional_ma = float(mosdepth_2_value) / 2 if mosdepth_2_value not in ["NA", "-"] else "NA"
            except Exception:
                additional_ma = "NA"
            row.append(format_value("additional_ma", "NRPCC", additional_ma))
        else:
            row.append("NA")
            row.append("NA")
            row.append("NA")
            row.append("NA")
        data_rows.append(row)
    
    return [header_row] + data_rows

    return [header_row] + data_rows

def main():
    json_file = "metrics.json"
    txt_file = "HG008-T_Element_GRCh38-GIABv3.txt"
    output_csv = "output.csv"
    data = load_json(json_file)
    mosdepth_values = load_mosdepth_txt(txt_file)
    
    with open(output_csv, "w", newline='') as f:
        writer = csv.writer(f)
        table_data = create_csv_table(data, mosdepth_values)
        writer.writerows(table_data)

if __name__ == "__main__":
    main()
