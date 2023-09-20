# jt_trial.py
# purpose - 1) store a trial run.  A trial conclude a dataframe with data along with one or more videos associated
#           2) holds components that uniquely identify a given trial and process those rules
# Notes:
#  - upon creation of the object this grabs the date and timestamp for future saving operations
#  - for saving or retrieving there is no reset of this class, use once and discard

import io, os, datetime
from datetime import datetime
import pandas as pd

try:
    from . import jt_util as util
    from . import jt_video as jtv
    from . import jt_config as jtc
    from . import jt_trial_manager as jttm
    from . import process_JTSext as p_JTSext
    from . import process_JTDcmj as p_JTDcmj
except:
    import jt_util as util
    import jt_config as jtc
    import jt_video as jtv
    import jt_trial_manager as jttm
    import process_JTSext as p_JTSext
    import process_JTDcmj as p_JTDcmj

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

##########################################################
class JT_Trial:
    def __init__(self, config_obj):
        self.config_obj = config_obj
        self.original_filename = None   #this is the filename with no path included
        self.file_path = None           #full path and filename
        self.timestamp_str = None
        self.date_now = None            #used for saving files
        self.trial_name = None
        self.results_df = pd.DataFrame()
        self.protocol_obj = None
        self.summary_results_dict = None
        self.protocol_summary_name = None        # holds the protocol filename to save the raw data with.
        self.debug = False      # used to write data to debug locations
        self.error = False
        self.error_msg = ""

        #for retrieving information
        self.graphs = {}    #graphs that can be saved for later use.  They are made up of title, xlabel, ylobel, and lines
                            # set process_JTDcmj.p for example.   There can be one or more of these that are made available
                            # and can be rendered by the UI
        self.video_files = {}

        #for saving trial information
        self.trial_dict = {}
        self.jt_videos = {}
        self.graph_images = {}      # IBSOLETE - Not used any more

        self.short_start_index = None
        self.short_end_index = None
        self.athletes_obj = config_obj.athletes_obj
        self.protocol_obj = config_obj.protocol_obj

    def parse_filename(self, file_path):
        self.short_filename = os.path.splitext(os.path.basename(file_path))[0]
        self.extension = os.path.splitext(os.path.basename(file_path))[1]
        filename = self.short_filename + self.extension
        directory_path = os.path.dirname(file_path)

        tokens = self.short_filename.split('_')
        try:

            self.protocol = tokens[0]
            self.athlete = tokens[1]
            self.date_str = tokens[2]
            self.time_str = tokens[3]

            self.trial_name = f'{self.protocol} - not set'

            #if old school format with no hyphens then reformat the string
            if '-' not in self.date_str:
                date_object = datetime.strptime(self.date_str, "%Y%m%d")
                self.date_str = date_object.strftime("%Y-%m-%d")

            if '-' not in self.time_str:
                time_obj = datetime.strptime(self.time_str, "%H%M%S")
                self.time_str = time_obj.strftime("%H-%M-%S")

            self.timestamp_str = self.date_str + "_" + self.time_str
            self._create_orginal_filename()
            self.file_path = file_path

        except:
            self.error = True
            self.error_msg = f"File name didn't meet specification (protocol_username_date_time) OR couldn't look up athlete: {self.short_filename}"
            log.info(self.error_msg)
            return None

    ##########################################
    # Retrieve Trial
    ##########################################

    # basedup upon a filepath get components used for a given trial
    # the file_path should be completely provided.  HOWEVER if not then path_data
    # can be added for it to attempt to find the file.   this is done for debugging purposes
    # so as the path changes from one OS to another OS.  It isn't used elsewhere

    def validate_trial_path(self, file_path, path_data = ""):

        self.file_path = file_path
        self.parse_filename(file_path)

        # check if path-data is in file_path.   if blanks is provided it will not execute
        if len(path_data) > 0 and path_data not in file_path:
            self.file_path = path_data + self.athlete + '/' + self.file_path
            self.error_msg = f'Debug on: and making sure file_path is complete:   {self.file_path} '
            log.debug(self.error_msg)
            return False

        # check if file_path exists
        if not os.path.exists(self.file_path):
            self.error_msg = f"validate_trial_path, file does not exist: {self.file_path}"
            log.critical(self.error_msg)
            self.error = True
            return False

        return True

    def attach_video_file(self, key, video):
        self.video_files[key] = video

    #########################
    # processes a given trial
    def process_summary(self):

        # sets up preliminary data
        self.injured = self.athletes_obj.get_injured_side(self.athlete)
        self.tested_leg = self.protocol_obj.get_leg_by_protocol(self.protocol)
        self.shank_length = self.athletes_obj.get_shank_length(self.athlete)

        #### different types of protocols
        if self.protocol.startswith("JTSext"):
            try:
                self.protocol_summary_name = 'JTSext'   # this make it not include the L or R for the different protocols
                protocol_specific_obj = p_JTSext.JTSext(self)
                self.summary_results_dict = protocol_specific_obj.process()
            except:
                self.error_msg = f'failed to proceess protocol: {self.protocol_summary_name} file: {self.original_filename}'
                log.error(self.error_msg)
                return False

        elif self.protocol == "JTDcmj":
            self.protocol_summary_name = self.protocol

            try:
                protocol_specific_obj = p_JTDcmj.JTDcmj(self)
                self.summary_results_dict = protocol_specific_obj.process()

                self.short_start_index = self.summary_results_dict['jump_onset_moment_index']
                self.short_end_index = self.summary_results_dict['takeoff_moment_index']
            except:
                self.error_msg = f'failed to proceess protocol: {self.protocol_summary_name} file: {self.original_filename}'

                log.error(self.error_msg)
                return False

        return True

    def _create_orginal_filename(self):
        self.original_filename = f"{self.protocol}_{self.athlete}_{self.timestamp_str}.csv"

    def save_summary(self):

        if not self.protocol_summary_name :
            log.error(f"Trial has not successfully had process_summary called:  {self.original_filename}")

        log_dict = {}
        log_dict['status'] = 'success'
        log_dict['athlete'] = self.athlete
        log_dict['protocol'] = self.protocol
        log_dict['protocol_summary_name'] = self.protocol_summary_name
        log_dict['short_filename'] = self.short_filename
        log_dict["timestamp_str"] = self.timestamp_str
        log_dict["date_str"] = self.date_str
        log_dict['filename'] = self.file_path

        standard_dict = {}
        standard_dict['original_filename'] = self.short_filename + '.csv'
        standard_dict['athlete_name'] = self.athlete
        standard_dict["col_timestamp_str"] = self.timestamp_str
        standard_dict["date_str"] = self.date_str
        my_dict = {}
        return_dict = {}

        # append the standard stuff to the results and
        try:
            self.summary_results_dict.update(standard_dict)
            self._save_results(my_dict, self.protocol)

            #grab the graphs to be returned if there are any
            return_dict = {key: value for key, value in self.summary_results_dict.items() if "GRAPH_" in key}

        except:

            log.error(f'FILE: {self.file_path} no such protocol: {self.protocol_summary_name}')

            #debug_log - write what information we can to even though there was an error processing the file
            log_dict['status'] = 'error'       #change status to error
            log_dict['error_msg'] = self.error_msg

            if self.debug == False:
                self._save_results(log_dict, 'debug_log')
            else:
                #debug code to create debug_log_data.csv
                self._save_debug_results(log_dict)

            self.error_msg = f"Failed to save summary data for {self.original_filename}"
            log.error(self.error_msg)

            return False

        return return_dict

    ###############################################
    #### log results to csv file ####
    def _save_results(self, my_dict, protocol):

        my_list = [my_dict]
        if len(my_list) < 1:
            log.msg(f'NO rows to store for {protocol}: Nothing written to file')
            return

        # create dataframe from my_list
        df = pd.DataFrame(my_list)

        # set up where file is written and sort the dataframe if it is the debug_log
        if protocol == 'debug_log':
            my_csv_filename = self.config_obj.path_log + protocol + '_data.csv'
        else:
            my_csv_filename = self.config_obj.path_db + protocol + '_data.csv'

        # log.msg(f'Results for {protocol}: number of rows {len(my_list)} written to file: {my_csv_filename}')

        # append if file exists,  if not then create it
        log.debug(f'SAVING RESULTS to file: {my_csv_filename}')
        if os.path.exists(my_csv_filename):
            # append results
            df.to_csv(my_csv_filename, mode='a', header=not os.path.isfile(my_csv_filename), index=True)
        else:
            # create new file
            df.to_csv(my_csv_filename)

    def _save_debug_results(self, my_dict):
        results_df = pd.DataFrame([my_dict])
        my_csv = self.config_obj.path_temp2 + 'debug_data.csv'
        results_df.to_csv(my_csv)

        my_flatfile = self.config_obj.path_temp2 + 'debug_data_flat.txt'
        # create flat file with value
        with open(my_flatfile, "w") as file:
            # Write each key/value pair to a new line
            for key, value in my_dict.items():
                file.write(f"{key} {value}\n")

    ##########################################
    # Saving Trial
    ##########################################

    #Set =object up to save data for an athlete and Protocol
    def setup_for_save(self, athlete, protocol):
        self.athlete = athlete
        self.protocol = protocol

    # add information in for saving
    def attach_results_df(self, results_df):
        self.results_df = results_df

    # video keys should be:   front, side, etc
    # video value - should be Object of JT_Video
    def attach_video(self, key, video):
        if not isinstance(video, jtv.JT_Video):
            raise TypeError("Video must be JT_Video")

        self.jt_videos[key] = video

    # images keys should be: main, ????
    # images value shoiuld be: BytesIO imported from io
    def attach_graph_images(self, key, image):
        if not isinstance(image, io.BytesIO):
            raise TypeError("Video must be JT_Video")

        self.graph_images[key] = image


    # this is called when all results are to be saved
    # path app is the base of where the app lives.  It will create any necessary directories required to save
    # .csv's, graphs, videos. Directories such as data/athlete, results/athlete/date, etc.
    def save_raw_trial(self, path_app):

        #save timestamp_str to right now
        self.timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.date_now = datetime.now().strftime("%Y-%m-%d")

        ###### data CSV saving
        #create path
        path_athlete = path_app + "data/" + self.athlete + "/"

        #create filename
        self._create_orginal_filename()

        log.debug(f'path_athlete: {path_athlete}')

        # Check if the data/athlete directory already exists
        if not os.path.exists(path_athlete):
            # Create the directory if it doesn't exist
            os.makedirs(path_athlete)
            log.debug(f'Directory created: {path_athlete}')

        self.trial_dict['original_filename'] = self.original_filename
        self.trial_dict['athlete'] = self.athlete
        self.trial_dict['protocol'] = self.protocol
        self.trial_dict['date'] = self.date_now
        self.trial_dict['timestamp'] = self.timestamp_str

        path_filename = path_athlete + self.original_filename

        try:
            self.results_df.to_csv(path_filename, index=True)
            log.debug(f"Trial: appending to file: {path_filename}")
            self.trial_dict['results_csv'] = path_filename
        except:
            self.error_msg = f"failed to save results_df: {path_filename}"
            log.error(self.error_msg)

        ##### Graphs/Images and Videos Saving
        # check if the results/athlete/date path exists and if not makes it
        path_results = path_app + "/results/" + self.athlete + "/" + self.date_now + "/"
        if not os.path.exists(path_results):
            # Create the directory if it doesn't exist
            os.makedirs(path_results)
            log.debug(f'Directory created: {path_results}')

        ###### Videos and images/graphs or stored in the results directory ######

        # save videos in results directory
        for key, value in self.jt_videos.items():
            filename = f"{self.protocol}_{self.athlete}_{self.timestamp_str}_{key}.mp4"
            path_filename = path_results + filename
            try:
                value.save_video(path_filename)
                log.msg(f"Saved Video: {path_filename}")
                self.trial_dict[key] = path_filename

            except:
                self.error_msg = f"FAILED to saved Video key: {key}: file: {path_filename}"
                log.error(self.error_msg)
        # save images in results directory
        for key, value in self.graph_images.items():
            filename = f"{self.protocol}_{self.athlete}_{self.timestamp_str}_{key}."
            path_filename = path_results + filename
            try:
                with open(path_filename, 'wb') as f:
                    f.write(value.getvalue())
                    log.msg(f"Saved graph/image: {path_filename}")
                    self.trial_dict[key] = path_filename

            except:
                self.error_msg = f"FAILED to saved graph/image key: {key}: file: {path_filename}"
                log.error(self.error_msg)
        return(self.trial_dict)


#####################################################################################
if __name__ == "__main__":

    # set base and application path
    path_base = util.jt_path_base()  # this figures out right base path for Colab, MacOS, and Windows
    path_app = path_base + 'Force Plate Testing/'
    config_obj = jtc.JT_Config(path_app)

    trial_mgr_obj = jttm.JT_JsonTrialManager(config_obj)

    trial = JT_Trial(config_obj)


    file1 = 'JTDcmj_huey_2023-08-17_00-27-47.csv'   # file that fails
    file3 = 'JTDcmj_huey_2023-08-17_00-38-07.csv'
    file4 = 'JTDcmj_huey_2023-08-17_00-16-09.csv'

    fp = file4
    trial = trial_mgr_obj.get_trial_file_path(fp, 'srt')
    if trial_mgr_obj.error:
        print(f'trial manager error: {trial_mgr_obj.error_msg}')
    else:
        trial.process_summary()
        print(f'TESTING RESULTS:  Processed file {fp}')
        print(f'processing status: {trial.error} (false is error)  Error_msg:{trial.error_msg}')
        print(f'Summary dict:\n{trial.summary_results_dict}')

