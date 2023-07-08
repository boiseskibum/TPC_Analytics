import pandas as pd

import jt_util as util

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

class JT_protocol:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        print(self.df)

    def get_names_by_type(self, type):
        return self.df.loc[self.df['type'] == type, 'name'].tolist()

    def get_protocol_by_name(self, name):
        return self.df.loc[self.df['name'] == name, 'protocol'].values[0]

    def get_leg_by_name(self, name):
        return self.df.loc[self.df['name'] == name, 'leg'].values[0]

    def get_unique_types(self):
        return self.df['type'].unique().tolist()

    def validate_type_name_combination(self, type, name):
        names = self.get_names_by_type(type)
        if name in names:
            return True
        else:
            return False

    def validate_data(self):
        unique_names = self.df['name'].unique()
        unique_protocols = self.df['protocol'].unique()

        error_str1 = ""
        error_str2 = ""

        duplicates = self.df[self.df.duplicated('name')]['name'].unique()
        if len(duplicates) > 0:
            error_str1 = f"Protocol file Validation Error: Duplicate values found in the 'name' column {duplicates}"
            log.f()
            log.error(error_str1)

        duplicates = self.df[self.df.duplicated('protocol')]['protocol'].unique()
        if len(duplicates) > 0:
            error_str2 = f"Protocol file Validation Error: Duplicate values found in the 'protocol' column {duplicates}"
            log.f()
            log.error(error_str2)

        return error_str1 + error_str2

#### Main ##########################################################

if __name__ == "__main__":

    # Test code
    file_path = 'jt_protocol_config.csv'  # Replace with the actual path to your CSV file

    # Create an instance of the DataProcessor
    protocol_obj = JT_protocol(file_path)

    # Get all unique types
    unique_types = protocol_obj.get_unique_types()
    print("Unique Types:", unique_types)

    # Loop through each type and get the associated protocol
    for type in unique_types:
        names = protocol_obj.get_names_by_type(type)
        print(f"Type: {type}")
        for name in names:
            protocol = protocol_obj.get_protocol_by_name(name)
            print(f"   Type: {type}, Name: {name}, Protocol: {protocol}")

    #lastly check the validate function to make sure all fields are correct and if not return an error messagge

    protocol_obj.validate_data()

    bs_list = protocol_obj.get_names_by_type("bs type")
    print(f"bs list of type results: {bs_list}")