import pandas as pd
import jt_util as util

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

class JT_athletes:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_csv(file_path)

    def get_athletes(self):
        unique_athletes = self.df["athletes_name"].unique()
        return unique_athletes.tolist()

    # this is typically "left" or right
    def get_injured_side(self, athlete_name):
        injured = self.df.loc[self.df["athletes_name"] == athlete_name, "injured"].values
        return injured_status[0]


