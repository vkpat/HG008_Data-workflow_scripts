import json
import csv

# Load your JSON file
json_filename = 'sample.json'  # Specify your JSON file name here
try:
    with open(json_filename, 'r') as file:
        qc_data = json.load(file)
except FileNotFoundError:
    print(f"Error: The file '{json_filename}' was not found.")
    qc_data = {}
except json.JSONDecodeError:
    print(f"Error: Failed to decode JSON from '{json_filename}'.")
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
    'G_mean_autosome_coverage': 'mean_autosome_coverage',  # Extracted from 'mosdepth'
}

# Add the new metric for percentage of mapped reads
metric_mapping['Percent_mapped_reads'] = 'Percent mapped reads'  # Add to mapping

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

    # Extract metrics for samtools data and convert to integers
    try:
        total_raw_sequences = int(samtools_data.get('raw total sequences', 0))
        reads_mapped = int(samtools_data.get('reads mapped', 0))
    except ValueError:
        total_raw_sequences = 0
        reads_mapped = 0

    # Loop through the metric mapping and extract corresponding values
    for metric, json_key in metric_mapping.items():
        if metric == 'G_mean_autosome_coverage':  # Check if it's the autosome coverage metric
            value = mosdepth_data.get(json_key, 'N/A')  # Get value directly from mosdepth data
        elif metric == 'Percent_mapped_reads':
            # Calculate percent mapped reads
            if total_raw_sequences > 0:
                value = (reads_mapped / total_raw_sequences) * 100
            else:
                value = 'N/A'  # Avoid division by zero
        else:
            value = samtools_data.get(json_key, 'N/A')  # Use 'N/A' if the key is not found
        row.append(value)  # Add the value to the row

    # Add the completed row to the summary_data
    summary_data.append(row)

# Write the extracted data to a CSV file
csv_filename = 'sample.csv'  # Specify your CSV output file name here
with open(csv_filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)

    # Write header and data rows
    csvwriter.writerows(summary_data)

print(f"Data has been written to {csv_filename}")

