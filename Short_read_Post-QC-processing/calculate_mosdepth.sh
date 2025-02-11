#!/bin/bash
# calc_mosdepth.sh
# This script calculates two values from a BED file named <ref_id>.bed:
#   - diploid_mean_coverage: sum of column 4
#   - haploid_mean_coverage: sum of column 2
#
# It then appends the results as key-value pairs to a text file.

# Check if a reference id was provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <ref_id>"
    exit 1
fi

# Define variables
ref_id="$1"
bed_file="${ref_id}"
output_file="HG008-T_Element_GRCh38-GIABv3.txt"

# Check if the BED file exists
if [ ! -f "$bed_file" ]; then
    echo "Error: File '$bed_file' not found!"
    exit 1
fi

# Calculate diploid_mean_coverage (sum of column 4)
diploid_mean_coverage=$(awk -F'\t' 'BEGIN { SUM=0 } { SUM += $4 } END { print (SUM/NR)*2 }' "$bed_file")

# Calculate haploid_mean_coverage (sum of column 2)
haploid_mean_coverage=$(awk -F'\t' 'BEGIN { SUM=0 } { SUM += $4 } END { print (SUM/NR) }' "$bed_file")

# Print the results to the console
echo "diploid_mean_coverage (sum of column 4): $diploid_mean_coverage"
echo "haploid_mean_coverage (sum of column 2): $haploid_mean_coverage"

# Append the results to the output file as key-value pairs
# If the file does not exist, it will be created.
{
    echo "diploid_mean_coverage=$diploid_mean_coverage"
    echo "haploid_mean_coverage=$haploid_mean_coverage"
} >> "$output_file"

echo "Results appended to $output_file"

