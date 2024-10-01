## This python script is to convert the JSON to CSV format that compiles all the metrics similar to manifest column names so we only need to copy the metrics from CSV to the HG008 data manifest 

import json
import csv

# Load your JSON file
try:
    with open('combined_HG001-HG005_metrics.json', 'r') as file:
        qc_data = json.load(file)
except FileNotFoundError:
    print("Error: The file 'sample.metrics.json' was not found.")
    qc_data = {}
except json.JSONDecodeError:
    print("Error: Failed to decode JSON from 'sample.metrics.json'.")
    qc_data = {}

# Define the mapping between the desired metric names and the corresponding fields in the JSON
metric_mapping = {
    'ST_total_raw_sequences': 'raw total sequences',
    'ST_reads_mapped': 'reads mapped',
    'ST_reads_mapped_paired': 'reads mapped and paired',
    'ST_error_rate': 'error rate',
    'ST_average_length': 'average length',
    'ST_insert_size_avg': 'insert size average',
    'ST_insert_size_SD': 'insert size standard deviation',
    'ST_percent_properly_paired': 'percentage of properly paired reads (%)',
    'percent_mapped_reads': 'bases mapped',
    'G_mean_autosome_coverage': 'mean_autosome_coverage',  # Extracted from 'mosdepth'
    'FQC_total_sequences': 'FASTQC sequences',  # Placeholder, update if needed
    'FQC_total_Gbp': 'FASTQC Gbp',  # Placeholder, update if needed
}

# Prepare the data for CSV. First, the header
header = ['File'] + list(metric_mapping.keys())

# Prepare the rows with metrics for each file
summary_data = [header]  # Start with the header

# Loop through each file in the JSON and extract the desired metrics
for filename, stats in qc_data.items():
    samtools_data = stats.get('samtools', {})  # Get the 'samtools' section of each file
    mosdepth_data = stats.get('mosdepth', {})  # Get the 'mosdepth' section of each file

    # Prepare a row for the current file
    row = [filename]  # Start the row with the filename

    # Loop through the metric mapping and extract corresponding values
    for metric, json_key in metric_mapping.items():
        if metric == 'G_mean_autosome_coverage':  # Check if it's the autosome coverage metric
            value = mosdepth_data.get(json_key, 'N/A')  # Get value directly from mosdepth data
        else:
            value = samtools_data.get(json_key, 'N/A')  # Use 'N/A' if the key is not found
        row.append(value)  # Add the value to the row

    # Add the completed row to the summary_data
    summary_data.append(row)

# Write the extracted data to a CSV file
csv_filename = 'qc_metrics_output_columns.csv'
with open(csv_filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)

    # Write header and data rows
    csvwriter.writerows(summary_data)

print(f"Data has been written to {csv_filename}")
