## This script helps to create a JSON file from the Cramino, samtools output for Long-read data stats

def parse_samtools_stats(file_path):
    """
    Parse samtools stats.txt output, where values may contain a number and description separated by \t.
    Remove the tab character and keep the number and description clean.
    """
    samtools_data = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                print(f"Processing line: {line}")  # Debugging: Print each line

                # Check if line starts with "SN" which indicates statistics line
                if line.startswith("SN"):
                    parts = line[2:].strip().split('\t')  # Remove "SN" and then split by tab
                    if len(parts) == 2:  # Expecting key-value pair
                        key = parts[0].strip()
                        value = parts[1].strip()

                        # Remove the tab character in value and replace it with a space
                        value = value.replace('\t', ' ')  # Replace \t with a space
                        samtools_data[key] = value
                    else:
                        print(f"Malformed line (expected two parts): {line}")

        if not samtools_data:
            print(f"Warning: No valid data in {file_path}")
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")

    # Include the filename in the samtools data
    samtools_data['filename'] = os.path.basename(file_path)

    return samtools_data

def combine_multiple_files(cramino_files, samtools_files, output_json):
    """
    Combine multiple cramino.txt and samtools_stats.txt files into a single JSON file.
    """
    combined_data = {}

    # Process each pair of cramino and samtools files
    for cramino_file, samtools_file in zip(cramino_files, samtools_files):
        sample_name = os.path.splitext(os.path.basename(cramino_file))[0]
        combined_data[sample_name] = {
            "cramino": parse_cramino(cramino_file),
            "samtools_stats": parse_samtools_stats(samtools_file)
        }

    # Write combined data to a JSON file
    with open(output_json, 'w') as json_file:
        json.dump(combined_data, json_file, indent=4)
    print(f"Data from {len(cramino_files)} file pairs combined and written to {output_json}")

def main():
    # Specify file paths for cramino.txt and samtools_stats.txt
    cramino_files = [
        "sample1_CraminoQC.txt",
        "sample2_craminoQC.txt",
        ]
    samtools_files = [
        "sample1_samtools_stats.txt",
        "sample2_samtools_stats.txt",
    ]

    # Ensure the file lists are of the same length
    if len(cramino_files) != len(samtools_files):
        raise ValueError("Mismatched number of cramino and samtools files.")

    # Output JSON file
    output_json_path = 'combined_data.json' 

    # Combine the data
    combine_multiple_files(cramino_files, samtools_files, output_json_path)

if __name__ == "__main__":
    main()


