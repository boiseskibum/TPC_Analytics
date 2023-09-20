# jt_config.py
# purpose: ability to store configuration data (keys and values) into a file

import json, os

try:
    from . import jt_util as util
    from . import jt_protocol as jtp
    from . import jt_athletes as jta
except:
    import jt_util as util
    import jt_protocol as jtp
    import jt_athletes as jta

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

class JT_Config:
    def __init__(self, path_app):

        self.error_msg = ""
        self.error = False

        # if filename with .csv sent in then we know this is just testing and don't set up everthing
        if ".csv" in path_app:
            self.config_file_path = path_app
        else:
            # setup path variable
            self.path_app = path_app
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
            self.protocol_obj = None
            self.athletes_obj = None

            #get protocol object
            try:
                self.protocol_obj = jtp.JT_protocol(self)
                ret = self.protocol_obj.validate_data()
                if len(ret) > 0:
                    self.error_msg = "ERROR: Protocol Config Validation"
                    self.error = True
                    self.protocol_obj = None
            except:
                self.error_msg = f"Protocol Config File ERROR: {self.protocol_file_path} could not be opened or found"
                log.error(self.error_msg)

            # get athletes object
            try:
                # create the athletes Object
                self.athletes_obj = jta.JT_athletes(self) # get list of valid athletes from CSV file
                self.athletes_obj.get_athletes()
            except:
                self.error_msg = "Error: Athletes List Unable to be opened"
                log.error(self.error_msg)
                self.athletes_obj = None

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

    def convert_file_path(self, file_path):

        #only convert if file path does NOT exist
        if os.path.exists(file_path):
            return file_path

        self.app_dir = 'Force Plate Testing/'

        # Find the index where "/Force Plate Testing/" ends
        index = file_path.find(self.app_dir)

        if index != -1:
            result = file_path[index + len(self.app_dir):]  # Extract everything after that part
            result = self.path_app + result
        else:
            print("ERROR '/Force Plate Testing/' not found in the file path")
            result = file_path

        if file_path != result:
            print(f"Converted: {file_path}\n    to:  {result}")

        return result


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

    # set base and application path
    path_base = util.jt_path_base()  # this figures out right base path for Colab, MacOS, and Windows
    path_app = path_base + 'Force Plate Testing/'

    # Create an instance of the DataProcessor
    config_obj = JT_Config(path_app)

    #macOS path converted to windows test
    fp = "/Users/stephentaylor/Library/CloudStorage/GoogleDrive-boiseskibum@gmail.com/My Drive/Force Plate Testing//results/huey/2023-08-17/JTDcmj_huey_2023-08-17_00-40-26_VIDEO_1.mp4"
    new_path = config_obj.convert_file_path(fp)
    print( f"test file conversion: {new_path}")

