# jt_trial.py
# purpose -  holds components that uniquely identify a given trial and process those rules for displaying the pieces
# Notes:

import datetime
from datetime import datetime
import io, os
import pandas as pd
import jt_util as util
import jt_video as jtv

import sys

import jt_trial as jtt

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

#object that accepts full file path to the trial.csv file
class JT_TrialDisplay:
    def __init__(self, filepath=None, trial_name=""):

        if filepath is not None:
            self.attach_filepath(filepath, trial_name)

        self.jt_videos = {}
        self.graph_images = {}

        self.trial_dict = {}

    def attach_filepath(self, filepath, trial_name=""):

        if not os.path.exists(filepath):
            log.error(f"In JT_TrialDisplay init, the filepath: {filepath} does not exist")

        file_dict = jtt.parse_filename(filepath)
        self.athlete = file_dict["athlete"]
        self.protocol = file_dict["protocol"]
        self.date_str = file_dict["date_str"]
        self.timestamp_str = file_dict["timestamp_str"]
        self.filename = file_dict["filename"]
        self.filepath = filepath
        self.trial_name = trial_name

    def attach_video(self, key, filepath):

        if not os.path.exists(filepath):
            log.error(f"In JT_TrialDisplay attach_video, the filepath: {filepath} does not exist")

        self.jt_videos[key] = filepath

    # images keys should be: main, ????
    # images value shoiuld be: BytesIO imported from io
    def attach_graph(self, key, filepath):
        if not os.path.exists(filepath):
            log.error(f"In JT_TrialDisplay attach_video, the filepath: {filepath} does not exist")

        self.graph_images[key] = filepath


#####################################################################################
if __name__ == "__main__":

    trial_display = JT_TrialDisplay('Avery McBride/JTSextR_Avery McBride_20230717_164704.csv')




