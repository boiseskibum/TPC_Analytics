# jt_trial_manager.py
# this objects manages all trials and groups them together

import pandas as pd
import json
import os

class JT_JsonTrialManager:
    def __init__(self, path, filename):
        self.path = path
        self.filename = filename    #filename to hold the json strings
        self.file_path = path + filename
        print(f"JsonTrialManager results stored in: {self.file_path}")

    def write_trial_dict(self, trial_dict):
        with open(self.file_path, 'a') as file:
            json.dump(trial_dict, file)
            file.write('\n')

        self.backup_trial(trial_dict)

    def read_to_dataframe(self):
        data = []
        with open(self.file_path, 'r') as file:
            for line in file:
                data.append(self._extract_keys(line.strip()))

        df = pd.DataFrame(data)
        # Drop duplicates based on the 'original_filename' key and keep the last occurrence
        df.drop_duplicates(subset=['original_filename'], keep='last', inplace=True)
        return df

    def backup_trial(self, trial_dict):
        backup_directory = os.path.join(os.path.dirname(self.file_path), 'backup')
        # if not os.path.exists(backup_directory):
        #     os.makedirs(backup_directory)
        backup_file_path = os.path.join(backup_directory, trial_dict['original_filename'] + '.json')

        print(f'backup_file_path: {backup_file_path}')
        if os.path.exists(backup_file_path):
            print(f'{backup_file_path} already exists. Overwriting...')

        with open(backup_file_path, 'w') as file:
            json.dump(trial_dict, file)

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
