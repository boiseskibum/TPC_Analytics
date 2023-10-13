# jt_trial_manager.py
# this objects manages all trials and appends them to the master list of trials.

import pandas as pd
import os, glob, json

try:
    import jt_util as util
    import jt_config as jtc
    import jt_trial as jtt
except:
    from . import jt_util as util
    from . import jt_config as jtc
    from . import jt_trial as jtt

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

class JT_JsonTrialManager:
    def __init__(self, config_obj):

        self.config_obj = config_obj
        self.path_db = config_obj.path_db
        self.error = False
        self.error_msg = ""
        #if path doesn't exist create it
        if len(self.path_db) > 0 and not os.path.exists(self.path_db):
            os.makedirs(self.path_db)

        self.protocol_list = self.config_obj.protocol_obj.summary_file_protocol_list


        self.trial_mgr_index_file_path = config_obj.trial_mgr_filename
        self.df = None      # if populated contains all trials that have been run
        print(f"JsonTrialManager results stored in: {self.trial_mgr_index_file_path}")

    ###############################################
    # Returns a list of all Trials tha have been stored
    def load_all_trials(self, force_reload=False):

        if self.df is None or force_reload == True:
            data = []
            try:
                with open(self.trial_mgr_index_file_path, 'r') as file:
                    for line in file:
                        data.append(self._extract_keys(line.strip()))
            except:
                self.error_msg = f'Failed in load_all_trials from: {self.trial_mgr_index_file_path}, file not there or no rows/values in it'
                log.error(self.error_msg)


            self.df = pd.DataFrame(data)

            # Drop duplicates based on the 'original_filename' key while only keeping the last occurrence.  This covers reprocessinng
            # that might occur.   Hopefully not often, if it does
            total_rows = len(self.df)
            self.df.drop_duplicates(subset=['original_filename'], keep='last', inplace=True)
            unique_rows = len(self.df)
            log.info(f"Trial manager total rows: {total_rows}, unique rows: {unique_rows},   wasted rows: {total_rows-unique_rows}")

        return self.df

    ###############################################
    # given just a filename it finds the full file_path which is needed.
    # returns a JT_Trial object containing the full path
    def get_trial_file_path(self, original_filename, trial_text=""):
        if self.df is None:
            self.load_all_trials()

        self._debug_print("whole deal",  self.df)

        columns = self.df.columns

        # Filter the DataFrame based on original_filename
        filtered_df = self.df[self.df["original_filename"] == original_filename]

        self._debug_print("Filtered df:", filtered_df)

        trial = jtt.JT_Trial(self.config_obj)

        # Retrieve the corresponding original_json value
        if not filtered_df.empty:
            original_json = filtered_df.iloc[0]["original_json"]
            log.debug(f"Original JSON value for {original_filename}: {original_filename}")
        else:
            self.error = True
            self.error_msg = f"No matching entry found for {original_filename}"
            log.debug(f"No matching entry found for {original_filename}")
            return trial

        data = json.loads(original_json)

        file_path = data['results_csv']
        log.debug(f"***Trial_manager.get_file_path: {file_path}***")

        # account for different OS
        converted_file_path = self.config_obj.convert_file_path(file_path)
        log.debug(f"***Trial_manager.get_file_path: {file_path}***")

        trial.validate_trial_path(converted_file_path)

        graphs_num = 0
        videos_num = 0
        #loop through keys looking for graphs and videos
        for key, value in data.items():
            # get videos associated with this trial
            if key.startswith("VIDEO"):

                #convert the path if needed to handle OS changes
                converted_file_path = self.config_obj.convert_file_path(value)
                log.debug(f"Key: {key}, Value: {converted_file_path}")
                trial.attach_video_file(key, converted_file_path)

        return trial

    ###############################################
    # this creates back up individual files for each Trial and puts them in the backup directory.  Hopefully never utilized
    def backup_trial_index(self, trial_dict):
        backup_directory = self.path_db + 'json_backup/'
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
    def _debug_print(self, title_str,  df):
        print(title_str)
        for index, row in df.iterrows():
            print(row['original_filename'], row['athlete'], row['protocol'])

    ###############################################
    ##### Saving Trial Functions  #####
    ###############################################

    #### save trial indexes
    # Appends the information from one Trial to the master file containing all trials
    # for convenience this returns a jt_trial_display for future usage
    def save_trial_indexing(self, trial_dict):

        with open(self.trial_mgr_index_file_path, 'a') as file:
            json.dump(trial_dict, file)
            file.write('\n')

        log.debug(f"Trial Manager - writing trial to {self.trial_mgr_index_file_path}")
        self.backup_trial_index(trial_dict)

        # if self.df is initialized then add the new row to it
        if self.df != None:
            # append data to existing df
            # this gets is the exact same as the process above where it creates a json, then extracts it back out
            # so that we can append it to the dataframe we already have.
            json_str = json.dump(trial_dict)
            data = []
            data.append(self._extract_keys(json_str))
            self.df = self.df.append(pd.Series(data, index=self.df.columns), ignore_index=True)

        return


    ###########################################################
    ##### UTILITY Functions  #####
    # return all athletes based upon existing folders list
    def get_list_of_all_athletes(self):

        # get list of athletes (folders in data directory)
        folders = []
        for entry in os.scandir(self.config_obj.path_data):
            if entry.is_dir():
                folders.append(entry.name)

        log.debug(f'folders: {folders}')

        return folders

    # return all files for a given athlete from their directory, the file names must start with JT (this excludes
    def get_all_files_for_athlete(self, athlete):

        # get list of files for athlete
        path = self.config_obj.path_data + athlete + '/JT*.csv'
        file_list = glob.glob(path)
        file_list = [os.path.normpath(file_path) for file_path in
                     file_list]  # line added so windows doesn't put a backslash in.
        log.debug(f'PROCESSING all files for: {athlete}')
        file_list.sort(key=os.path.getmtime)
        # log.debug(f'filelist: {file_list}')

        return file_list

    # old stuff from jakes master's program

    # delete all summary data for a given athlete from the respective summary
    def delete_athlete_summary_records(self, athlete):

        #iterate over protocols to open summary files and delete the athlete
        for protocol in self.protocol_list:
            my_csv_filename = self.path_db + protocol + '_data.csv'
            if os.path.exists(my_csv_filename):

                # Read the DataFrame from CSV
                df = pd.read_csv(my_csv_filename)
                before = len(df)

                # Filter out rows with athlete_name="Steve Taylor"
                df_filtered = df[df['athlete_name'] != athlete]
                after = len(df_filtered)
                # Reset the index
                df_filtered = df_filtered.reset_index(drop=True)

                # Save the filtered DataFrame to a new CSV file
                df_filtered.to_csv(my_csv_filename, index=False)
                print(f"Removed athlete {athlete} from protocol summary: {protocol}, before: {before}, after: {after}")
            else:
                pass

        return True

    # delete summary data files so they can be rebuilt
    def delete_all_summary_files(self):
        for protocol in self.protocol_list:
            csv_filename_to_delete = self.path_db + protocol + '_data.csv'

            # Check if the file exists before attempting to delete it
            if os.path.exists(csv_filename_to_delete):
                # Attempt to remove the file
                try:
                    os.remove(csv_filename_to_delete)
                    log.debug(f"Summary File {csv_filename_to_delete} deleted successfully.")
                except OSError as e:
                    self.error = True
                    self.error_msg = f"Error deleting Summary File {csv_filename_to_delete}: {e}"
                    log.debug(self.error_msg)
            else:
                log.debug(f"Summary File {csv_filename_to_delete} does not exist.")


###############################################
###############################################
###############################################
# Example usage:
if __name__ == "__main__":

    config_obj = jtc.JT_Config('taylor performance', 'TPC')

    trial_mgr_obj = JT_JsonTrialManager(config_obj)

    log.set_logging_level("INFO")
    # file_path = 'trials.json'
    #
    #
    # # Write some trial dictionaries to the file
    # trial_mgr.save_trial_indexing({
    #     'original_filename': 'JTSextL_Mickey_2023-08-08_16-40-29.csv',
    #     'athlete': 'John Doe',
    #     'protocol': 'Protocol A',
    #     'date': '2023-07-22',
    #     'timestamp': '2023-07-22 15:30:00',
    #     'other_data': 'some_data'
    # })
    #
    # trial_mgr.save_trial_indexing({
    #     'original_filename': 'JTSextL_Mickey_2023-08-08_16-40-29.csv',
    #     'athlete': 'Jane Smith',
    #     'protocol': 'Protocol B',
    #     'date': '2023-07-23',
    #     'timestamp': '2023-07-23 10:45:00',
    #     'other_data': 'some_other_data'
    # })

    # Read the JSON strings into a DataFrame
#    df = trial_mgr_obj.load_all_trials()
#    print(df)
#    oj = last_original_json_value = df["original_json"].iloc[-1]
#    print(f'last value of original json is: {oj}')

    def testing_delete_athlete(tm, athlete):

        athletes = tm.get_list_of_all_athletes()
        if athlete in athletes:
            print(f"Deleting summary data for: {athlete}")
            tm.delete_athlete_summary_records(athlete)
            files = tm.get_all_files_for_athlete(athlete)
            print(f"    reprocessing: {len(files)} files for athlete: {athlete}")

            #reprocessing files
            for file in files:
                trial = trial_mgr_obj.get_trial_file_path(file, 'srt')
                if trial_mgr_obj.error:
                    print(f'trial manager error: {trial_mgr_obj.error_msg}')
                else:
                    trial.process_summary()
                    trial.save_summary()

        else:
            print("ERROR:  Athlete does not have directory")

        # add athlete data back in debug_log


    def testing_rebuild_all(tm):
        tm.delete_all_summary_files()
        if tm.error:
            print(f'Deleted all summary files')
        else:
            print(f'Failed to delete all files.  Error msg: {tm.error_msg}')

        max_files = 100000
        total = 0
        completed = 0
        athletes = tm.get_list_of_all_athletes()
        for athlete in athletes:

            files = tm.get_all_files_for_athlete(athlete)
            print(f"    Processing {athlete} num files: {len(files)}")
            # reprocessing files
            for file in files:
                # allow myself to do only so many
                if total < max_files:
                    total += 1
                    trial = jtt.JT_Trial(config_obj)
                    trial.parse_filename(file)
                    if trial.error == True:
                        print(f'trial error: {trial.error_msg}')
                    else:
#                        print(f"## about to process_summary file: {file}")
                        trial.process_summary()
                        if trial.error == True:
                            print(f'Trial Error:  {trial.error_msg}')
                        else:
 #                           print(f"## about to save_summary file: {file}")
                            trial.save_summary()
                            if trial.error == True:
                                print(f'Trial Error:  {trial.error_msg}')
                            else:
                                completed += 1
                                print(f'## Successfully completed: {file}')
        print(f'#### total processed: {total} success: {completed}: failed: {total - completed}')
        pass



#    testing_delete_athlete(trial_mgr_obj, 'Mickey')
    testing_rebuild_all(trial_mgr_obj)
