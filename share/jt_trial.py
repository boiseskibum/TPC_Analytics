# jt_trial.py
# purpose - store and retrieve trial runs.  A trial conclude a dataframe with data along with one or more videos associated
#
# Notes:
#  - upon creation of the object this grabs the date and timestamp for future saving operations
#  - for saving or retrieving there is no reset of this class, use once and discard

import datetime
from datetime import datetime
import io, os
import pandas as pd
import jt_util as util
import jt_video as jtv

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

class JT_Trial:
    def __init__(self, athlete, protocol):
        self.athlete = athlete
        self.protocol = protocol
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.date = datetime.now().strftime("%Y%m%d")
        self.long_date = datetime.now().strftime("%Y-%m-%d")
        self.orginal_filename = ""

        self.results_df = pd.DataFrame()
        self.jt_videos = {}
        self.graph_images = {}

        self.trial_dict = {}

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

    # needs some thinking here, does it get a list of trials that it can then get a single trial for it.  Should a list of results be its own class?
    def get_athlete(self):
        pass

    # this is called when all results are to be saved
    # path app is the base of where the app lives.  It will create any necessary directories required to save
    # .csv's, graphs, videos. Directories such as data/athlete, results/athlete/date, etc.
    def save_trial(self, path_app):

        ###### data CSV saving
        #create path
        path_athlete = path_app + "/data/" + self.athlete + "/"

        #create filename
        self.orginal_filename = f"{self.protocol}_{self.athlete}_{self.timestamp}.csv"

        log.debug(f'path_athlete: {path_athlete}')

        # Check if the data/athlete directory already exists
        if not os.path.exists(path_athlete):
            # Create the directory if it doesn't exist
            os.makedirs(path_athlete)
            log.debug(f'Directory created: {path_athlete}')

        self.trial_dict['original_filename'] = self.orginal_filename
        self.trial_dict['athlete'] = self.athlete
        self.trial_dict['protocol'] = self.protocol
        self.trial_dict['date'] = self.date
        self.trial_dict['timestamp'] = self.timestamp

        path_filename = path_athlete + self.orginal_filename

        try:
            self.results_df.to_csv(path_filename, index=True)
            log.debug(f"saved file: {path_filename}")
            self.trial_dict['results_csv'] = path_filename
        except:
            log.error(f"failed to save results_df: {path_filename}")

        ##### Graphs/Images and Videos Saving
        # check if the results/athlete/date path exists and if not makes it
        path_results = path_app + "/results/" + self.athlete + "/" + self.long_date + "/"
        if not os.path.exists(path_results):
            # Create the directory if it doesn't exist
            os.makedirs(path_results)
            log.debug(f'Directory created: {path_results}')

        ###### Videos and images/graphs or stored in the results directory ######

        # save videos in results directory
        for key, value in self.videos.items():
            filename = f"{self.protocol}_{self.athlete}_{self.timestamp}_{key}.mp4"
            path_filename = path_results + filename
            try:
                value.save_video(path_filename)
                log.msg(f"Saved Video: {path_filename}")
                self.trial_dict[key] = path_filename

            except:
                log.error(f"FAILED to saved Video key: {key}: file: {path_filename}")

        # save images in results directory
        for key, value in self.graph_images.items():
            filename = f"{self.protocol}_{self.athlete}_{self.timestamp}_{key}."
            path_filename = path_results + filename
            try:
                with open(path_filename, 'wb') as f:
                    f.write(value.getvalue())
                    log.msg(f"Saved graph/image: {path_filename}")
                    self.trial_dict[key] = path_filename

            except:
                log.error(f"FAILED to saved graph/image key: {key}: file: {path_filename}")

        return(self.trial_dict)
