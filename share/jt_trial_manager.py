# jt_trial_manager.py
# this objects manages all trials and appends them to the master list of trials.

import pandas as pd
import json
import os
if __name__ == "__main__":
    import jt_util as util
    import jt_trial as jtt
    import jt_trial_display as jttd
else:
    from . import jt_util as util
    from . import jt_trial as jtt
    from . import jt_trial_display as jttd

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

class JT_JsonTrialManager:
    def __init__(self, config_obj):

        self.config_obj = config_obj

        self.path = config_obj.path_db
        #if path doesn't exist create it
        if len(self.path) > 0 and not os.path.exists(self.path):
            os.makedirs(self.path)

        self.file_path = config_obj.trial_mgr_filename
        self.df = None      # if populated contains all trials that have been run
        print(f"JsonTrialManager results stored in: {self.file_path}")

    ###############################################
    # Appends the information from one Trial to the master file containing all trials
    # for convenience this returns a jt_trial_display for future usage
    def write_trial_dict(self, trial_dict):

        with open(self.file_path, 'a') as file:
            json.dump(trial_dict, file)
            file.write('\n')

        log.debug(f"Trial Manager - writing trial to {self.file_path}")
        self.backup_trial(trial_dict)

        # if self.df is initialized then add the new row to it
        if self.df != None:
            # append data to existing df
            # this gets is the exact same as the process above where it creates a json, then extracts it back out
            # so that we can append it to the dataframe we already have.
            json_str = json.dump(trial_dict)
            data = []
            data.append(self._extract_keys(json_str))
            self.df = self.df.append(pd.Series(data, index=self.df.columns), ignore_index=True)

        original_filename = trial_dict['original_filename']
        trial_display = jttd.JT_TrialDisplay(original_filename)

        return trial_display

    ###############################################
    # Returns a list of all Trials tha have been stored
    def load_all_trials(self, force_reload=False):

        if self.df is None or force_reload == True:
            data = []
            try:
                with open(self.file_path, 'r') as file:
                    for line in file:
                        data.append(self._extract_keys(line.strip()))
            except:
                log.error(f"Failed to load_all_trials from: {self.file_path}")

            self.df = pd.DataFrame(data)

            # Drop duplicates based on the 'original_filename' key while only keeping the last occurrence.  This covers reprocessinng
            # that might occur.   Hopefully not often, if it does
            total_rows = len(self.df)
            self.df.drop_duplicates(subset=['original_filename'], keep='last', inplace=True)
            unique_rows = len(self.df)
            log.info(f"Trial manager total rows: {total_rows}, unique rows: {unique_rows},   wasted rows: {total_rows-unique_rows}")

        return self.df

    ###############################################
    # given just a filename it finds the full file_path which is needed.   returns a trial
    def get_trial_file_path(self, original_filename, trial_text=""):
        if self.df is None:
            self.load_all_trials()

        columns = self.df.columns

        # Filter the DataFrame based on original_filename
        filtered_df = self.df[self.df["original_filename"] == original_filename]

        # Retrieve the corresponding original_json value
        if not filtered_df.empty:
            original_json = filtered_df.iloc[0]["original_json"]
            log.debug(f"Original JSON value for {original_filename}: {original_filename}")
        else:
            log.debug(f"No matching entry found for {original_filename}")
            return None

        data = json.loads(original_json)

        file_path = data['results_csv']
        log.debug(f"***Trial_manager.get_file_path: {file_path}***")

        trial = jtt.JT_Trial()
        trial.retrieve_trial(file_path)

        graphs_num = 0
        videos_num = 0
        #loop through keys looking for graphs and videos
        for key, value in data.items():
            # get videos associated with this trial
            if key.startswith("VIDEO"):
                print(f"Key: {key}, Value: {value}")
                trial.attach_video_file(key, value)

        return trial

    ###############################################
    # this creates back up individual files for each Trial and puts them in the backup directory.  Hopefully never utilized
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
###############################################
###############################################
###############################################
# Example usage:
if __name__ == "__main__":
    file_path = 'trials.json'

    json_manager = JT_JsonTrialManager("", "test_trial_manager.json")



    # Write some trial dictionaries to the file
    json_manager.write_trial_dict({
        'original_filename': 'JTSextL_Mickey_2023-08-08_16-40-29.csv',
        'athlete': 'John Doe',
        'protocol': 'Protocol A',
        'date': '2023-07-22',
        'timestamp': '2023-07-22 15:30:00',
        'other_data': 'some_data'
    })

    json_manager.write_trial_dict({
        'original_filename': 'JTSextL_Mickey_2023-08-08_16-40-29.csv',
        'athlete': 'Jane Smith',
        'protocol': 'Protocol B',
        'date': '2023-07-23',
        'timestamp': '2023-07-23 10:45:00',
        'other_data': 'some_other_data'
    })

    # Read the JSON strings into a DataFrame
    df = json_manager.load_all_trials()
    print(df)
    oj = last_original_json_value = df["original_json"].iloc[-1]
    print(f'last value of original json is: {oj}')

    temp = 'JTSextL_Mickey_2023-08-08_16-40-29.csv'
    td = json_manager.get_trial_display(temp)
