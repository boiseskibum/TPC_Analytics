import os
import pandas as pd

try:
    from . import jt_util as util
except ImportError:
    import jt_util as util

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

class JT_athletes:
    def __init__(self, config_obj, testing_file_path=""):

        if config_obj is not None:
            self.config_obj = config_obj

            self.athletes_file_path = self.config_obj.athletes_file_path
        elif len(testing_file_path) > 0:
            self.athletes_file_path = testing_file_path
        else:
            log.critical(f'JT_Athletes creation')

        self.df = pd.DataFrame()

    #always reopen list and get it whenever called
    def get_athletes(self, new_file_name = None ):
        if new_file_name != None:
            self.athletes_file_path = new_file_name

        if not os.path.exists(self.athletes_file_path):
            #create a small sample file if the athletes file doesn't exist
            # Column names
            columns = ["athletes_name", "injured", "shank_length"]
            data = []
            # Data in row format - no longer utilized
            # data = [
            #     ["zHuey", "right", .25],
            #     ["zDewey", "left", .3]
            # ]

            self.df = pd.DataFrame(data, columns=columns)

            # Write the prototype DataFrame to a CSV file
            self.df.to_csv(self.athletes_file_path, index=False)

        try:
            self.df = pd.read_csv(self.athletes_file_path)
            unique_athletes = self.df["athletes_name"].unique()
            unique_athletes_sorted = sorted(unique_athletes)
            return unique_athletes_sorted
        except:
            raise ValueError(f"Could not open athletes file: {self.athletes_file_path}")


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

    # Add an athlete to the csv.   All fields are required
    def add_athlete(self, athlete, injured, shank_length):

        # validate athlete doesn't already exist
        if athlete.lower() in self.df['athletes_name'].str.lower().values:
            log.info(f'add_athlete failed to add user: |{athlete}| already exists')
            return

        self.get_athletes()
        new_data = {'athletes_name': athlete, 'injured': injured, 'shank_length': shank_length}
        new_row = pd.DataFrame([new_data])
        #print (f'#####  self.df type: {type(self.df)}, new_row type: {type(new_row)}')
        self.df = pd.concat([self.df, new_row], ignore_index=True)

        self.df.to_csv(self.athletes_file_path, index=False)  # Save the DataFrame back to CSV

#### Main ##########################################################

if __name__ == "__main__":

    # Test code
    file_path = 'athletes_testing.csv'  # Replace with the actual path to your CSV file

    # Create an instance of the DataProcessor
    athletes_obj = JT_athletes(None, file_path)

    # Get all unique types
    athletes = athletes_obj.get_athletes()
    log.debug(f'Athletes: {athletes}' )

    for athlete in athletes:
        injured = athletes_obj.get_injured_side(athlete)
        log.debug(f"athlete: {athlete}, Injured: {injured}")

