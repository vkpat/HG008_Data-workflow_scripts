import os

# Function to rename files
def rename_files(directory, old_pattern, new_pattern):
    # List all files in the specified directory
    for filename in os.listdir(directory):
        # Check if the old pattern exists in the filename
        if old_pattern in filename:
            # Create the new filename by replacing the old pattern with the new one
            new_filename = filename.replace(old_pattern, new_pattern)
            
            # Get the full paths of the files
            old_file = os.path.join(directory, filename)
            new_file = os.path.join(directory, new_filename)
            
            # Rename the file
            os.rename(old_file, new_file)
            print(f'Renamed: {filename} -> {new_filename}')
            
# Example usage:
# Specify the directory containing your files
directory = 'PATH'

# Specify the pattern you want to replace and the new pattern
old_pattern = 'GRCh38-GIABv3_HG005_GAT-APP-C144'
new_pattern = 'HG005_Element-StdInsert_78x_GRCh38-GIABv3'

# Call the rename function
rename_files(directory, old_pattern, new_pattern)
