import os
import json
import re

def extract_hg_id(filename):
    """Extract the HG ID from the filename."""
    match = re.search(r'HG008-(T|N-D|N-P)', filename)
    return match.group(0) if match else "Unknown"

def extract_ref_id(filename):
    """Extract the reference ID from the filename (e.g., GRCh38, GRCh37, CHM13)."""
    match = re.search(r'(GRCh38-GIABv3|GRCh37|CHM13v2.0)', filename)
    return match.group(0) if match else "Unknown"

def extract_id_from_filename(file_name):
    """
    Extract the sample ID, ref_id, and hg_id from the filename.
    """
    sample_id = os.path.splitext(os.path.basename(file_name))[0]
    ref_id = extract_ref_id(file_name)
    hg_id = extract_hg_id(file_name)
    return sample_id, ref_id, hg_id

def cramino(file_path):
    """
    Parse the first 13 lines of cramino.txt output with tab-separated key-value pairs,
    including ref_id and hg_id if present.
    """
    cramino_data = {}
    extracted_sample_id, extracted_ref_id, extracted_hg_id = extract_id_from_filename(file_path)
    ref_id = extracted_ref_id
    hg_id = extracted_hg_id
    
    with open(file_path, 'r') as file:
        for idx, line in enumerate(file):
            if idx >= 13:  # Stop reading after 13 lines
                break
            parts = line.strip().split('\t')
            if len(parts) == 2:  # Ensure it's a valid key-value pair
                key, value = parts
                key = key.strip()
                value = value.strip()
                cramino_data[key] = value
                
                # Capture ref_id and hg_id if they appear in the data
                if key.lower() == "ref_id" and value != "Unknown":
                    ref_id = value
                if key.lower() == "hg_id" and value != "Unknown":
                    hg_id = value
    
    return extracted_sample_id, cramino_data, ref_id, hg_id

def samtools_stats(file_path):
    """
    Parse the samtools stats.txt output, where each "SN" line contains a key-value pair.
    Each value may also contain a comment (after a '#').
    """
    samtools_data = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith("SN"):
                    parts = line[2:].strip().split('\t', 1)
                    if len(parts) == 2:  # Expecting key-value pair
                        key = parts[0].strip()
                        value = parts[1].strip()
                        value_parts = value.split('#', 1)
                        data_value = value_parts[0].strip()
                        comment = value_parts[1].strip() if len(value_parts) > 1 else ""
                        if comment:
                            samtools_data[key] = f"{data_value}  # {comment}"
                        else:
                            samtools_data[key] = data_value
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")
    return samtools_data

def combine_multiple_files(cramino_files, samtools_files, output_json):
    """
    Combine multiple cramino.txt and samtools_stats.txt files into a single JSON file.
    """
    combined_data = {}

    for cramino_file, samtools_file in zip(cramino_files, samtools_files):
        sample_id, extracted_ref_id, extracted_hg_id = extract_id_from_filename(cramino_file)
        samtools_file_name = os.path.basename(samtools_file)
        
        extracted_sample_id, cramino_data, file_ref_id, file_hg_id = cramino(cramino_file)
        
        # Use file-based IDs if they exist, otherwise fall back to extracted IDs
        ref_id = file_ref_id if file_ref_id != "Unknown" else extracted_ref_id
        hg_id = file_hg_id if file_hg_id != "Unknown" else extracted_hg_id

        if extracted_sample_id not in combined_data:
            combined_data[extracted_sample_id] = {
                "samples": []
            }
        
        combined_data[extracted_sample_id]["samples"].append({
            "ref_id": ref_id if ref_id != "Unknown" else "GRCh38,GRCh37,Chm13",
            "hg_id": hg_id,
            "cramino": cramino_data,
            "samtools_stats": {
                "file_name": samtools_file_name,
                "data": samtools_stats(samtools_file)
            }
        })

    with open(output_json, 'w') as json_file:
        json.dump(combined_data, json_file, indent=4)
    print(f"Data from {len(cramino_files)} file pairs combined and written to {output_json}")

def main():
    # Specify file paths for cramino.txt and samtools_stats.txt
    cramino_files = [
        "HG008-T_GRCh38-GIABv3_ONT-UL-R10.4.1-dorado_0.8.1_sup.5mC_5hmC_54x_20241216.cramino.txt",
        "HG008-T_CHM13v2.0_ONT-UL-R10.4.1-dorado_0.8.1_sup.5mC_5hmC_54x_20241216.cramino.txt",
        ]
    samtools_files = [ 
        "HG008-T_GRCh38-GIABv3_ONT-UL-R10.4.1-dorado_0.8.1_sup.5mC_5hmC_54x_20241216.samtools_stats.txt",
        "HG008-T_CHM13v2.0_ONT-UL-R10.4.1-dorado_0.8.1_sup.5mC_5hmC_54x_20241216.samtools_stats.txt",
    ]

    if len(cramino_files) != len(samtools_files):
        raise ValueError("Mismatched number of cramino and samtools files.")

    output_json_path = 'output.json'
    combine_multiple_files(cramino_files, samtools_files, output_json_path)

if __name__ == "__main__":
    main()
