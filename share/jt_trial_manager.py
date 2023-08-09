# jt_trial_manager.py
# this objects manages all trials and groups them together

import pandas as pd
import json
import os
import jt_util as util

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

class JT_JsonTrialManager:
    def __init__(self, path, filename):
        self.path = path
        #if path doesn't exist create it
        if len(path) > 0 and not os.path.exists(path):
            os.makedirs(path)
        self.filename = filename    #filename to hold the json strings
        self.file_path = path + filename
        print(f"JsonTrialManager results stored in: {self.file_path}")

    def write_trial_dict(self, trial_dict):
        with open(self.file_path, 'a') as file:
            json.dump(trial_dict, file)
            file.write('\n')

        log.debug(f"Trial Manager - writing trial to {self.file_path}")
        self.backup_trial(trial_dict)

    def read_to_dataframe(self):
        data = []
        try:
            with open(self.file_path, 'r') as file:
                for line in file:
                    data.append(self._extract_keys(line.strip()))
        except:
            log.error(f"Failed to write the backup json file: {backup_file_path}")

        df = pd.DataFrame(data)
        # Drop duplicates based on the 'original_filename' key and keep the last occurrence
        df.drop_duplicates(subset=['original_filename'], keep='last', inplace=True)
        return df

    def backup_trial(self, trial_dict):
        backup_directory = self.path + 'json_backup/'
        if not os.path.exists(backup_directory):
            os.makedirs(backup_directory)
        json_filename = os.path.splitext( trial_dict['original_filename'] )[0]
        backup_file_path = backup_directory + json_filename + '.json'

        print(f'backup_file_path: {backup_file_path}')
        if os.path.exists(backup_file_path):
            log.debug(f'{backup_file_path} already exists. Overwriting...')

        try:
            with open(backup_file_path, 'w') as file:
                json.dump(trial_dict, file)
        except:
            log.error(f"Failed to write the backup json file: {backup_file_path}")

    def _extract_keys(self, json_str):
        data = json.loads(json_str)
        return {
            'original_filename': data.get('original_filename', ''),
            'athlete': data.get('athlete', ''),
            'protocol': data.get('protocol', ''),
            'date': data.get('date', ''),
            'timestamp': data.get('timestamp', ''),
            'original_json': json_str
        }
# Example usage:
if __name__ == "__main__":
    file_path = 'trials.json'

    json_manager = JT_JsonTrialManager("", "test_trial_manager.json")

    # Write some trial dictionaries to the file
    json_manager.write_trial_dict({
        'original_filename': 'trial1',
        'athlete': 'John Doe',
        'protocol': 'Protocol A',
        'date': '2023-07-22',
        'timestamp': '2023-07-22 15:30:00',
        'other_data': 'some_data'
    })

    json_manager.write_trial_dict({
        'original_filename': 'trial2',
        'athlete': 'Jane Smith',
        'protocol': 'Protocol B',
        'date': '2023-07-23',
        'timestamp': '2023-07-23 10:45:00',
        'other_data': 'some_other_data'
    })

    # Read the JSON strings into a DataFrame
    df = json_manager.read_to_dataframe()
    print(df)
