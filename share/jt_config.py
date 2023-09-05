# jt_config.py
# purpose: ability to store configuration data (keys and values) into a file

import json

class JT_Config:
    def __init__(self, path_app):

        # if filename with .csv sent in then we know this is just testing and don't set up everthing
        if ".csv" in path_app:
            self.config_file_path = path_app
        else:
            # setup path variable
            self.path_data = path_app + 'data/'
            self.path_results = path_app + 'results/'
            self.path_log = path_app + 'log/'
            self.path_db = path_app + 'db/'
            self.path_config = path_app + 'config/'

            # default db/tables names - can be changed but probably shouldn't be
            # These will go into a real database someday
            self.config_file_path = self.path_config + "jt_cmj_main_config.json"
            self.protocol_file_path = self.path_config + "jt_protocol_config.csv"
            self.athletes_file_path = self.path_config + "athletes.csv"
            self.trial_mgr_filename = self.path_db + 'all_athletes.json'

    # get key value
    def get_config(self, my_key):
        try:
            with open(self.config_file_path, "r") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {}

        # if the key is not found then "None" is returned
        last_key_value = config.get(my_key, None)

        return last_key_value

    # set a key/value in the config file
    def set_config(self, my_key, new_key_value):
        my_return = False
        try:
            with open(self.config_file_path, "r") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {}

        config[my_key] = new_key_value
        with open(self.config_file_path, "w") as f:
            json.dump(config, f)
            my_return = True

        return my_return

########################################################

if __name__ == "__main__":
    # Test code
    file_path = 'config_testing.csv'  # Replace with the actual path to your CSV file

    # Create an instance of the DataProcessor
    config_obj = JT_Config(file_path)

    print( f"test1: should be nothing/fail: {config_obj.get_config('abc')}")
    print( f"test2: stores a value: {config_obj.set_config('abc', 'abc_value1')}")
    print( f"test3: stores a value: {config_obj.set_config('abc2', 'abc_value2')}")

    print( f"test3: get abc2 value: {config_obj.get_config('abc2')}")
    print( f"test3: get def2 value, should fail: {config_obj.get_config('def2')}")


