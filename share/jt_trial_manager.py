# jt_trial_manager.py
# this objects manages all trials and appends them to the master list of trials.

import pandas as pd
import os, glob, json, time, sys

#used for progress bar
from PyQt6.QtWidgets import QProgressDialog, QApplication, QLabel, QVBoxLayout, QPushButton, QWidget
from PyQt6 import QtCore, QtWidgets


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
        self.path_db = self.config_obj.path_db
        self.error = False
        self.error_msg = ""
        #if path doesn't exist create it
        if len(self.path_db) > 0 and not os.path.exists(self.path_db):
            os.makedirs(self.path_db)

        self.protocol_list = self.config_obj.protocol_obj.summary_file_protocol_list


        self.trial_mgr_index_file_path = self.config_obj.trial_mgr_filename
        self.df = None      # if populated contains all trials that have been run
        log.debug(f"JsonTrialManager results stored in: {self.trial_mgr_index_file_path}")

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
            log.debug(f"Trial manager total rows: {total_rows}, unique rows: {unique_rows},   wasted rows: {total_rows-unique_rows}")

        return self.df

    #function to return a dataframe with the unique combinations of athletes and the protocols that they have completed
    def get_athletes_and_protocols_combinations(self):

        self.load_all_trials(True)

        # Create a copy of the DataFrame
        df_copy = self.df.copy()

        # Step 1: Create 'short_protocol' column
        df_copy['short_protocol'] = df_copy['protocol'].apply(lambda x: 'JTSext' if x.startswith('JTSext') else x)
        #print(df_copy)

        # Get unique combinations of athlete and short_protocol
        unique_combinations_df = df_copy[['athlete', 'short_protocol']].drop_duplicates()
        #print(unique_combinations_df)

        return(unique_combinations_df)

    ###############################################
    # given just a filename it finds the full file_path which is needed.
    # returns a JT_Trial object containing the full path
    def get_trial_file_path(self, original_filename, trial_text=""):
        if self.df is None:
            self.load_all_trials()

#        self._debug_print("whole deal",  self.df)

        columns = self.df.columns

        # Filter the DataFrame based on original_filename
        filtered_df = self.df[self.df["original_filename"] == original_filename]

#        self._debug_print("Filtered df:", filtered_df)

        trial = jtt.JT_Trial(self.config_obj)

        # Retrieve the corresponding original_json value
        if not filtered_df.empty:
            original_json = filtered_df.iloc[0]["original_json"]
            log.debug(f"Original JSON value for {original_json}: {original_filename}")
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
                video_file_path = value
                trial.attach_video_file(key, video_file_path)

        return trial

    ###############################################
    # this creates back up individual files for each Trial and puts them in the backup directory.  Hopefully never utilized
    def backup_trial_index(self, trial_dict):
        backup_directory = self.path_db + 'json_backup/'
        if not os.path.exists(backup_directory):
            os.makedirs(backup_directory)
        json_filename = os.path.splitext( trial_dict['original_filename'] )[0]
        backup_file_path = backup_directory + json_filename + '.json'

        log.debug(f'backup_file_path: {backup_file_path}')
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
    def save_trial_indexing(self, trial_dict):

        with open(self.trial_mgr_index_file_path, 'a') as file:
            json.dump(trial_dict, file)
            file.write('\n')

        log.debug(f"Trial Manager - writing trial to {self.trial_mgr_index_file_path}")

# commenting out backup trial index because it can be reproduced.  Maybe the future but not right now
#        self.backup_trial_index(trial_dict)

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

    #returns the total number of files.  Used for reprocessoing progress dialog
    def get_total_files(self):

        total = 0
        athletes = self.get_list_of_all_athletes()
        for athlete in athletes:

            files = self.get_all_files_for_athlete(athlete)
            # reprocessing files
            for file in files:
                total += 1

        return total

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


    # delete summary data files so they can be rebuilt - these files hold all of the data for a given protocol
    def delete_summary_files(self):

        self.error = False
        for protocol in self.protocol_list:
            csv_filename_to_delete = self.path_db + protocol + '_data.csv'
            log.debug(f'Deleting summary data file: {csv_filename_to_delete}')
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

    # code to delete the index_file
    def delete_index_file(self):

        self.error = False
        if os.path.exists(self.trial_mgr_index_file_path):
            # Attempt to remove the file
            try:
                os.remove(self.trial_mgr_index_file_path)
            except OSError as e:
                self.error = True
                self.error_msg = f"Error deleting Summary File {self.trial_mgr_index_file_path}: {e}"
                log.debug(self.error_msg)
        else:
            log.debug(f"Summary File {self.trial_mgr_index_file_path} does not exist, could not delete.")

    #reprocess all files, this will rebuild the summary files, rebuild the index file, and recreate any image files
    def reprocess_all_files(self, my_pyqt_app = None):
        total_files = self.get_total_files()

        # code to put up status - file n of total files
        if my_pyqt_app is not None:
            my_progressDialog = QProgressDialog("Processing Files...", "cancel", 0, total_files, my_pyqt_app)
            my_progressDialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
            QtWidgets.QApplication.processEvents()  # Process events to update the UI
            time.sleep(2)  # delay a moment

        log.info(f"***** Reprocessing {total_files} files *****")

        # first delete the summary files
        self.delete_summary_files()
        if self.error == False:
            log.info(f'Deleted all summary files')
        else:
            log.info(f'Failed to delete all Summary files.  Error msg: {self.error_msg}')

        # delete the index files
        self.delete_index_file()
        if self.error == False:
            log.info(f'Deleted Index file')
        else:
            log.info(f'Failed to delete Index_File.  Error msg: {self.error_msg}')

        #walk through athletes re-processing each one
        total = 0
        completed = 0
        athletes = self.get_list_of_all_athletes()
        for athlete in athletes:

            files = self.get_all_files_for_athlete(athlete)
            log.info(f"    Processing {athlete} num files: {len(files)}")
            # reprocessing files
            for file in files:
                total += 1
                trial = jtt.JT_Trial(self.config_obj)
                trial.parse_filename(file)
                if trial.error == True:
                    log.error(f'trial error: {trial.error_msg}')
                else:
#                        print(f"## about to process_summary file: {file}")
                    trial.process_summary()
                    if trial.error == True:
                        log.error(f'Trial Error:  {trial.error_msg}')
                    else:
#                            print(f"## about to save_summary file: {file}")
                        trial.save_summary()
                        if trial.error == True:
                            log.error(f'Reprocessing Error:  {trial.error_msg}')
                        else:
                            completed += 1
                            log.debug(f'## Successfully Reprocessed: {file}')
                            trial_dict = trial.recreate_trial_dict()
                            self.save_trial_indexing(trial_dict)

                # status on screen - file n of total files to process
                if my_pyqt_app is not None:
                    my_progressDialog.setValue(total)
                    my_progressDialog.setLabelText(f"Processing File {total}/{total_files}")
                    QtWidgets.QApplication.processEvents()  # Process events to update the UI
                    if total_files < 15:
                        time.sleep(.3)  # Simulate file processing time

        if my_pyqt_app is not None:
            my_progressDialog.setValue(total_files)  # Ensure the progress bar reaches 100%
            my_progressDialog.setLabelText(f"Processing File {total}/{total_files}")
            QtWidgets.QApplication.processEvents()  # Process events to update the UI
            time.sleep(3)  # Simulate file processing time

        msg_str = f'#### total processed: {total} success: {completed}: failed: {total - completed}'
        log.info(msg_str)

        return msg_str

###############################################
###############################################
###############################################
# Example usage:
class FileProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Testing of Re-Processor")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout(self)

        # Button to start processing files
        start_button = QPushButton("Re-Process Files", self)
        start_button.clicked.connect(self.process_files)
        layout.addWidget(start_button)

    def process_files(self):

        #WARNING THIS WILL REPROCESS ALL FILES
        config_obj = jtc.JT_Config('taylor performance', 'TPC', None)
        config_obj.validate_install()

        trial_mgr_obj = JT_JsonTrialManager(config_obj)

        trial_mgr_obj.reprocess_all_files(self)


if __name__ == "__main__":


    app = QApplication(sys.argv)
    window = FileProcessor()
    window.show()
    sys.exit(app.exec())


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

