import pandas as pd
import jt_util as util

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

class JT_athletes:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.DataFrame()

    #always reopen list and get it whenever called
    def get_athletes(self, new_file_name = None ):
        if new_file_name != None:
            self.file_path = new_file_name

        try:
            self.df = pd.read_csv(self.file_path)
            unique_athletes = self.df["athletes_name"].unique()
            return unique_athletes.tolist()
        except:
            raise ValueError(f"Could not open athletes file: {self.file_path}")


    # this is typically "left" or right
    def get_injured_side(self, athlete_name):
        if len(self.df) < 1:
            self.get_athletes()

        try:
            filtered_df = self.df[self.df["athletes_name"] == athlete_name]
            injured = filtered_df["injured"].values[0]
        except:
            log.error(f'could not find: {athlete_name} in get_injured_side call')
            injured =""
        return injured

    # this is used for the length of leg in the ISO test
    def get_shank_length(self, athlete_name):
        if len(self.df) < 1:
            self.get_athletes()

        try:
            filtered_df = self.df[self.df["athletes_name"] == athlete_name]
            value = filtered_df["shank_length"].values[0]
        except:
            log.error(f'could not find: {athlete_name} in get_shank_length call')
            value = ""
        return value


#### Main ##########################################################

if __name__ == "__main__":

    # Test code
    file_path = 'athletes_testing.csv'  # Replace with the actual path to your CSV file

    # Create an instance of the DataProcessor
    athletes_obj = JT_athletes(file_path)

    # Get all unique types
    athletes = athletes_obj.get_athletes()
    print("Athletes:", athletes)

    for athlete in athletes:
        injured = athletes_obj.get_injured_side(athlete)
        print(f"athlete: {athlete}, Injured: {injured}")

