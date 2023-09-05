# jt_trial.py
# purpose - 1) store a trial run.  A trial conclude a dataframe with data along with one or more videos associated
#           2) holds components that uniquely identify a given trial and process those rules
# Notes:
#  - upon creation of the object this grabs the date and timestamp for future saving operations
#  - for saving or retrieving there is no reset of this class, use once and discard

import datetime
from datetime import datetime
import io, os, sys
import pandas as pd
import jt_util as util
import jt_video as jtv

sys.path.append('../JT_analytics')
import process_JTSext as p_JTSext
import process_JTDcmj as p_JTDcmj


# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

# purpose is to parse filenames in a consistent manner
# the filename can and should contain the complete path to the file
def parse_filename(file_path):

    short_filename = os.path.splitext(os.path.basename(file_path))[0]
    extension = os.path.splitext(os.path.basename(file_path))[1]
    filename = short_filename + extension
    directory_path = os.path.dirname(file_path)
    tokens = short_filename.split('_')

    try:
        protocol = tokens[0]
        athlete = tokens[1]
        date_str = tokens[2]
        time_str = tokens[3]

        #if old school format with no hyphens then reformat the string
        if '-' not in date_str:
            date_object = datetime.strptime(date_str, "%Y%m%d")
            date_str = date_object.strftime("%Y-%m-%d")

        if '-' not in time_str:
            time_obj = datetime.strptime(time_str, "%H%M%S")
            time_str = time_obj.strftime("%H-%M-%S")

        timestamp_str = date_str + "_" + time_str
    except:
        log.info(f"File name didn't meet specification (protocol_username_date_time) so ignoring: {short_filename}")
        return None

    my_dict = {
        "filename": filename,
        "short_filename": short_filename,
        "path": directory_path,
        "file_path": file_path,
        "athlete": athlete,
        "protocol": protocol,
        "date_str": date_str,
        "time_str": time_str,
        "timestamp_str": timestamp_str
    }

    return my_dict

##########################################################
class JT_Trial:
    def __init__(self):
        self.original_filename = None   #this is the filename with no path included
        self.file_path = None           #full path and filename
        self.timestamp_str = None
        self.date_now = None            #used for saving files

        self.results_df = pd.DataFrame()
        self.jt_videos = {}
        self.graph_images = {}
        self.trial_dict = {}
        self.graphs ={}     #graphs that can be saved for later use.  They are made up of title, xlabel, ylobel, and lines
                            # set process_JTDcmj.p for example.   There can be one or more of these that are made available
                            # and can be rendered by the UI

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

            #if old school format with no hyphens then reformat the string
            if '-' not in self.date_str:
                date_object = datetime.strptime(self.date_str, "%Y%m%d")
                self.date_str = date_object.strftime("%Y-%m-%d")

            if '-' not in self.time_str:
                time_obj = datetime.strptime(self.time_str, "%H%M%S")
                time_str = time_obj.strftime("%H-%M-%S")

            self.timestamp_str = self.date_str + "_" + self.time_str

        except:
            log.info(f"File name didn't meet specification (protocol_username_date_time) so ignoring: {self.short_filename}")
            return None

    #Set =object up to save data for an athlete and Protocol
    def setup_for_save(self, athlete, protocol):
        self.athlete = athlete
        self.protocol = protocol

    # basedup upon a filepath get components used for a given trial
    # the file_path should be completely provided.  HOWEVER if not then path_data
    # can be added for it to attempt to find the file.   this is done for debugging purposes
    # so as the path changes from one OS to another OS.  It isn't used elsewhere

    def retrieve_trial(self, file_path, path_data = ""):

        self.file_path = file_path
        self.parse_filename(file_path)

        # check if path-data is in file_path.   if blanks is provided it will not execute
        if len(path_data) > 0 and path_data not in file_path:
            self.file_path = path_data + self.athlete + '/' + self.file_path
            log.debug(f'Debug on: and making sure file_path is complete:   {self.file_path} ')

        # check if file_path exists
        if not os.path.exists(self.file_path):
            log.critical(f"process_single_file, file does not exist: {self.file_path}")
            return

    def get_trial_data(self):

        if self.protocol.startswith("JTSext"):
            log.debug("NEED TO IMPLEMENT SOMETHING HERE for JTSEXT")

        elif self.protocol == "JTDcmj":

            # Process the cmj file
            process_obj = p_JTDcmj.JTDcmj(self, injured, path_athlete_results)

            my_dict = process_obj.process()

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
    def save_trial(self, path_app):

        #save timestamp_str to right now
        self.timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.date_now = datetime.now().strftime("%Y-%m-%d")

        ###### data CSV saving
        #create path
        path_athlete = path_app + "data/" + self.athlete + "/"

        #create filename
        self.original_filename = f"{self.protocol}_{self.athlete}_{self.timestamp_str}.csv"

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
            log.error(f"failed to save results_df: {path_filename}")

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
                log.error(f"FAILED to saved Video key: {key}: file: {path_filename}")

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
                log.error(f"FAILED to saved graph/image key: {key}: file: {path_filename}")

        return(self.trial_dict)


#####################################################################################
if __name__ == "__main__":

    my_dict = parse_filename('Avery McBride/JTSextR_Avery McBride_20230717_164704.csv')
    print(f"Results from parsing filename: {my_dict}")