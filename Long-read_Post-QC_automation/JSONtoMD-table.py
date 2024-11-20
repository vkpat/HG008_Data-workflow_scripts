## This python script helps to extract the QC metrics value from JSON file to a Markdown table for FTP README or sharing the table to collaborator and internal team memebers

import json
import os

def extract_sample_name(filename):
    """
    Extract the sample name from the filename by splitting on the first underscore.
    """
    return filename.split('_')[0]

def format_with_commas(value):
    """
    Add commas to numbers in a string if applicable.
    """
    try:
        # Remove any non-numeric parts (e.g., descriptions) for formatting
        numeric_part = int(value.split()[0])
        return f"{numeric_part:,}" + " " + " ".join(value.split()[1:])
    except (ValueError, IndexError):
        # If the value isn't numeric or can't be formatted, return as is
        return value

def generate_markdown_table(json_file, output_md, include_fields):
    """
    Generate a Markdown table from a JSON file, including only specified fields.
    Dynamically extract sample names from filenames.
    """
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Create a Markdown table header
    headers = ["Sample Name"] + include_fields
    md_table = [" | ".join(headers), " | ".join(["---"] * len(headers))]

    # Populate the table rows
    for sample, content in data.items():
        # Dynamically extract the sample name from filename
        sample_name = extract_sample_name(content["samtools_stats"]["filename"])

        row = [sample_name]  # Use extracted sample name for the table
        for field in include_fields:
            # Pull values from cramino or samtools_stats as needed
            value = (
                content["cramino"].get(field) or
                content["samtools_stats"].get(field) or
                "N/A"
            )
# Format numbers with commas if applicable
            row.append(format_with_commas(value))
        md_table.append(" | ".join(row))

    # Write to an output .md file
    with open(output_md, 'w') as md_file:
        md_file.write("\n".join(md_table))

    print(f"Markdown table written to {output_md}")

def main():
    # Input JSON file
    input_json = "combined_data.json"

    # Output Markdown file
    output_md = "summary_table.md"

    # Fields to include in the table
    include_fields = [
        "Number of alignments",
        "% from total reads",
        "Yield [Gb]" ,
        "Mean coverage",
        "N50",
        "Median identity",

    ]

    # Generate the Markdown table
    generate_markdown_table(input_json, output_md, include_fields)

if __name__ == "__main__":
    main()

