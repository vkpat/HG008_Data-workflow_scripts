## Python script helps to create a table with QC metrics in the Markdown file format for the FTP README or sharing purposes

import json
import csv

# Function to create a Markdown table with a title
def create_markdown_table(title, data):
    # Add the title to the Markdown file
    markdown_table = f"# {title}\n\n"
    
    # Extract table headers from the keys of the first dictionary
    headers = list(data[0].keys())
    
    # Create the header row
    markdown_table += "| " + " | ".join(headers) + " |\n"
    
    # Create the separator row
    markdown_table += "| " + " | ".join(['---'] * len(headers)) + " |\n"
    
    # Create each row of the table
    for row in data:
        markdown_table += "| " + " | ".join([str(row[header]) for header in headers]) + " |\n"
    
    return markdown_table

# Load the JSON data from a file
def load_json(json_file):
    with open(json_file, 'r') as file:
        return json.load(file)

# Function to extract specific metrics from the mosdepth CSV (assuming a specific structure)
def extract_mosdepth_metrics(json_data):
    # Navigate to the "sample.mosdepth.csv" -> "mosdepth" section
    mosdepth_data = json_data.get("sample.mosdepth.csv", {}).get("mosdepth", {})

    # Extract specific metrics like mean_autosome_coverage
    metrics = [
        {
            "Metrics": "Mean autosome coverage",
            "Value": mosdepth_data.get("mean_autosome_coverage", "N/A")
        }
    ]
    
    return metrics

# Function to extract specific metrics from the JSON data
def extract_json_metrics(json_data):
    # Navigate to the "sample.samtools_stats.txt" -> "samtools" section
    samtools_data = json_data.get("sample.samtools_stats.txt", {}).get("samtools", {})
    
    # Extract specific metrics
    metrics = [
        {
            "Metrics": "Total raw sequences",
            "Value": samtools_data.get("raw total sequences", "N/A")
        },
        {
            "Metrics": "Reads mapped and paired",
            "Value": samtools_data.get("reads mapped and paired", "N/A")
        },
        {
            "Metrics": "Error rate",
            "Value": samtools_data.get("error rate", "N/A")
        },
        {
            "Metrics": "Average length",
            "Value": samtools_data.get("average length", "N/A")
        },
        {
            "Metrics": "Insert size average",
            "Value": samtools_data.get("insert size average", "N/A")
        },
        {
            "Metrics": "Insert size standard deviation",
            "Value": samtools_data.get("insert size standard deviation", "N/A")
        },
        {
            "Metrics": "Percentage of properly paired reads",
            "Value": samtools_data.get("percentage of properly paired reads (%)", "N/A")
        }
    ]
    
    return metrics

# Main function to read the JSON, extract metrics from both JSON and mosdepth, and write to a Markdown file
def main(json_file, markdown_file):
    # Load the JSON file
    json_data = load_json(json_file)

    # Extract the specific metrics from the mosdepth CSV
    mosdepth_metrics = extract_mosdepth_metrics(json_data)

    # Extract the specific metrics from the JSON (samtools)
    json_metrics = extract_json_metrics(json_data)
    
    # Combine both sets of metrics
    combined_metrics = mosdepth_metrics + json_metrics
    
    # Define the title of the table
    title = "HG005_Element-StdInsert Summary table"
    
    # Create the Markdown table with a title
    markdown_table = create_markdown_table(title, combined_metrics)
    
    # Write the Markdown table to a file
    with open(markdown_file, 'w') as md_file:
        md_file.write(markdown_table)
    
    print(f"Markdown table saved to {markdown_file}")

# Example usage
if __name__ == "__main__":
    json_file = 'sample.json'  # Replace with your JSON file path where your JSON is located.
    markdown_file = 'output.md'  # Output Markdown file name 
    main(json_file, markdown_file)
