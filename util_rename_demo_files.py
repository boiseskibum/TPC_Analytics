import os, datetime
from datetime import datetime, timedelta
import pandas as pd

def rename_files(directory):
    # List all files in the given directory
    i = 0
    for filename in os.listdir(directory):
        i+=1

        # Construct full file path
        filepath = os.path.join(directory, filename)

        # Check if it's a file
        if os.path.isfile(filepath):
            # Split the filename by underscore
            root, ext = os.path.splitext(filename)

            tokens = root.split('_')

            # Check if there are enough parts in the filename
            if len(tokens) > 1:
                first_name = ''
                last_name = ''
                try:
#                    print(f'  tokens {tokens}')
                    # Extract the first and second tokens (assuming the second token contains the full name)
                    try:
                        first_name, last_name = tokens[1].split()[:2]
                    except:
                        first_name = tokens[1]
                        last_name = 'n/a'
#                    print(f'  first_name: {first_name}, last_name: {last_name}')

                    # hack to change the first name of Isaiah to Max
                    new_first_name = first_name
                    if first_name == 'Isaiah':
                        new_first_name = 'Max'

                    # get remaining tokens
                    protocol = tokens[0]
                    date_str = tokens[2]
                    time_str = tokens[3]

                    # this is hack to pick up the 'Video_1" at the end for mpegs
                    try:
                        file_type = tokens[4]
                        file_bonus = tokens[5]
                        more_crap = f'_{file_type}_{file_bonus}'
                    except:
                        more_crap = ''

                    # if old school format with no hyphens then reformat the string
                    if '-' not in date_str:
                        date_object = datetime.strptime(date_str, "%Y%m%d")
                        date_str = date_object.strftime("%Y-%m-%d")

                    if '-' not in time_str:
                        time_obj = datetime.strptime(time_str, "%H%M%S")
                        time_str = time_obj.strftime("%H-%M-%S")

                    # add one second to the time string
                    time_obj = datetime.strptime(time_str, "%H-%M-%S")
                    new_time_obj = time_obj + timedelta(seconds=1)
                    new_time_str = new_time_obj.strftime("%H-%M-%S")

                    # Construct the new filename
                    new_filename = f"{protocol}_{new_first_name}_{date_str}_{new_time_str}{more_crap}{ext}"
                    new_filepath = os.path.join(directory, new_filename)
                    print(f' old filename: {filename}    new filename: {new_filename}')

                    # Rename the file
                    os.rename(filepath, new_filepath)
#                    print(f"Renamed '{filename}' to '{new_filename}\n'")

                    if '.csv' in new_filename:
                        # lastly open the .csv and change the athletes name
                        # Load the CSV file
                        df = pd.read_csv(new_filepath)

                        # Replace all values in the 'athletes name' column
                        df['athletes_name'] = new_first_name

                        # Save the modified DataFrame back to a CSV file
                        df.to_csv(new_filepath, index=False)

                except:
                    print(f'could not unpack: {filename}')
    print(f'processed {i} files')
# Example usage
directory_path = 'resources/demo'
rename_files(directory_path)
