import os

def rename_files(directory):
    # List all files in the given directory
    for filename in os.listdir(directory):
        # Construct full file path
        filepath = os.path.join(directory, filename)

        # Check if it's a file
        if os.path.isfile(filepath):
            # Split the filename by underscore
            tokens = filename.split('_')

            # Check if there are enough parts in the filename
            if len(tokens) > 1:
                first_name = ''
                last_name = ''
                try:
                    print(f'  tokens {tokens}')
                    # Extract the first and second tokens (assuming the second token contains the full name)
                    first_name, last_name = tokens[1].split()[:2]
                    print(f'  first_name: {first_name}, last_name: {last_name}')

                    # hack to change the first name of Isaiah to Max
                    new_first_name = first_name
                    if first_name == 'Isaiah':
                        new_first_name = 'Max'

                    # Construct the new filename
                    new_filename = filename.replace(f"{first_name} {last_name}", f"z{new_first_name}")
                    new_filepath = os.path.join(directory, new_filename)

                    # Rename the file
                    os.rename(filepath, new_filepath)
                    print(f"Renamed '{filename}' to '{new_filename}'")
                except:
                    print(f'could not unpack: {filename}')

# Example usage
directory_path = 'resources/demo'
rename_files(directory_path)
