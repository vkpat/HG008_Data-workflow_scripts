import json

# Function to create a Markdown table with a title
def create_markdown_table(title, data):
    markdown_table = f"## {title}\n\n"
    headers = list(data[0].keys())
    markdown_table += "| " + " | ".join(headers) + " |\n"
    markdown_table += "| " + " | ".join(['---'] * len(headers)) + " |\n"
    
    for row in data:
        markdown_table += "| " + " | ".join([str(row[header]) for header in headers]) + " |\n"
    
    return markdown_table

# Load the JSON data from a file
def load_json(json_file):
    with open(json_file, 'r') as file:
        return json.load(file)

# Function to format numerical values with commas and without decimal places for specific metrics
def format_value(metric, value):
    if metric in ["Total raw sequences", "Reads mapped", "Reads mapped and paired"]:
        try:
            formatted_value = f"{int(float(value)):,}"  # Format as integer with commas and "x"
        except ValueError:
            formatted_value = value
    elif metric == "Mean autosome coverage":
        try:
            formatted_value = f"{round(float(value)):,}x"  # Format as integer with commas and "x"
        except ValueError:
            formatted_value = value
    else:
        formatted_value = value  # No formatting for other metrics
    
    return formatted_value

# Function to handle the error rate conversion to percentage
def format_error_rate(value):
    try:
        error_rate_percent = float(value) * 100
        return f"{error_rate_percent:.2f}%"  # Format error rate to two decimal places with %
    except ValueError:
        return value

# Function to calculate percentage of reads mapped
def calculate_percent_read_mapped(total_raw_sequences, reads_mapped):
    try:
        total_raw = float(total_raw_sequences)
        mapped = float(reads_mapped)
        percent_mapped = (mapped / total_raw) * 100 if total_raw > 0 else 0
        return f"{percent_mapped:.1f}"  # Format percentage to two decimal places with %
    except ValueError:
        return "N/A"

# Function to extract specific metrics from the samtools stats in JSON data
def extract_samtools_metrics(json_data):
    samtools_data = json_data.get("samtools", {})
    
    # Extract relevant metrics for calculation
    total_raw_sequences = samtools_data.get("raw total sequences", "N/A")
    reads_mapped = samtools_data.get("reads mapped", "N/A")
    reads_mapped_and_paired = samtools_data.get("reads mapped and paired", "N/A")

    # Calculate percent read mapped
    percent_read_mapped = calculate_percent_read_mapped(total_raw_sequences, reads_mapped)

    # Keep the desired metrics format
    metrics = [
        {
            "Metrics": "Total raw sequences",
            "Value": format_value("Total raw sequences", total_raw_sequences)
        },
        {
            "Metrics": "Reads mapped",
            "Value": format_value("Reads mapped", reads_mapped)
        },
        {
            "Metrics": "Reads mapped and paired",
            "Value": format_value("Reads mapped and paired", reads_mapped_and_paired)
        },
        {
            "Metrics": "Percent Read Mapped",
            "Value": percent_read_mapped
        },
        {
            "Metrics": "Error rate",
            "Value": format_error_rate(samtools_data.get("error rate", "N/A"))
        },
        {
            "Metrics": "Average length",
            "Value": samtools_data.get("average length", "N/A")  # No formatting needed for average length
        },
        {
            "Metrics": "Insert size average",
            "Value": samtools_data.get("insert size average", "N/A")  # No formatting needed for insert size average
        },
        {
            "Metrics": "Insert size standard deviation",
            "Value": samtools_data.get("insert size standard deviation", "N/A")  # No formatting needed for insert size standard deviation
        },
        {
            "Metrics": "Percentage of properly paired reads",
            "Value": samtools_data.get("percentage of properly paired reads (%)", "N/A")  # No formatting needed for percentage of properly paired reads
        }
    ]
    
    return metrics

# Function to extract specific metrics from the mosdepth section in JSON data
def extract_mosdepth_metrics(json_data):
    mosdepth_data = json_data.get("mosdepth", {})
    
    # Extract Mean autosome coverage
    mean_autosome_coverage = mosdepth_data.get("mean_autosome_coverage", "N/A")

    # Keep the desired metrics format
    metrics = [
        {
            "Metrics": "Mean autosome coverage",
            "Value": format_value("Mean autosome coverage", mean_autosome_coverage)
        }
    ]

    return metrics

# Function to extract HG_IDs from the JSON
def extract_hg_ids(json_data):
    hg_ids = [{"HG_ID": sample_data.get("HG_ID", "Unknown")} for sample_data in json_data.values()]
    return hg_ids

# Main function to read the JSON, extract metrics from both JSON and mosdepth, and write to a Markdown file
def main(json_file, markdown_file):
    # Load the JSON file
    json_data = load_json(json_file)

    # Extract HG_IDs for the separate HG_ID table
    hg_ids = extract_hg_ids(json_data)

    # Create HG_ID table
    hg_id_title = "HG_ID Table"
    hg_id_table = create_markdown_table(hg_id_title, hg_ids)

    # Start writing to the Markdown file
    with open(markdown_file, 'w') as md_file:
        # Write the HG_ID table at the top
        md_file.write(hg_id_table)
        md_file.write("\n\n")  # Add some spacing
        
        # Loop through each sample in the JSON data and create separate tables by HG_ID
        for sample_name, sample_data in json_data.items():
            hg_id = sample_data.get("HG_ID", "Unknown")
            
            # Extract the specific metrics from samtools
            samtools_metrics = extract_samtools_metrics(sample_data)

            # Extract the specific metrics from mosdepth
            mosdepth_metrics = extract_mosdepth_metrics(sample_data)

            # Combine both sets of metrics
            combined_metrics =  mosdepth_metrics + samtools_metrics
            
            # Define the title of the table for the current HG_ID
            metrics_title = f"Summary Table for {hg_id}"
            
            # Create the Markdown table for the current HG_ID
            metrics_table = create_markdown_table(metrics_title, combined_metrics)
            
            # Write the table for the current HG_ID
            md_file.write(metrics_table)
            md_file.write("\n\n")  # Add some spacing between tables
    
    print(f"Markdown tables saved to {markdown_file}")

# Example usage
if __name__ == "__main__":
    json_file = 'HG001-5_combined_metrics_LngInsert.json'  # Replace with your JSON file path
    markdown_file = 'HG001-5_combined_metrics_LngInsert.md'  # Output Markdown file name 
    main(json_file, markdown_file)

