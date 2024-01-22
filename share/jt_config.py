# jt_config.py
# purpose: ability to store configuration data (keys and values) into a file

import json, os, platform, shutil
from PyQt6.QtGui import QImage, QPixmap

try:
    from . import jt_util as util
    from . import jt_protocol as jtp
    from . import jt_athletes as jta
    from . import jt_trial_manager as jttm
except:
    import jt_util as util
    import jt_protocol as jtp
    import jt_athletes as jta
    import jt_trial_manager as jttm

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

###########################
# app_name - holds the app name which will be used in directories and other places
# path_app - used only for debug if you want the config file to be in specific spot.
#
# Usage:
#   1) my_config = JT_config initialize to get started from your main app
#   2) my_config.validate directories to see if a directory structure has already been set up.  If no directory has been
#       set up it creates the directory in ~/documents/app_name with a default to self.path_app to utilize that
#       initial path, but will return False so that the application can then have the opportunity to set the path_app
#       for data/db/results/log/etc.
#   3) if .validate() returns False then call my_config.set_app_location(directory_path) to pass in the path where the
#       app should be installed.   The default will be in ~/documents/app_name.   Ideally they install in some
#       directory that is backed up in the cloud
#   4) my_config._set_paths()  this utilizes the directory set above and is already called with a successful call
#       of my_config.validate() or inside of my_config.set_app_location
#
class JT_Config:
    def __init__(self, app_name, base_path, debug_path="" ):

        self.error_msg = ""
        self.error = False
        self.app_name = app_name
        self.app_name_no_blanks = app_name.replace(" ", "_")
        self.debug_path = debug_path
        self.current_directory = os.getcwd()
        log.msg(f"Current Working Directory: {self.current_directory}")
        if base_path is not None:
            self.base_path = base_path  # this is the base path
        else:
            self.base_path = self.current_directory

        # get operations system (Windows or Darwin
        self.my_platform = platform.system()

    # this validates if the install has happened.  see descriptions above
    def validate_install(self):
        if ".csv" in self.debug_path:
            self.config_file_path = self.debug_path
            return True

        self._get_os_document_path()

        starting_path_app = self.documents_folder + self.app_name + '/'   # this will be overwritten later
        path_app_config = starting_path_app + 'config/'
        self.path_app_config_json = path_app_config + self.app_name_no_blanks + '_path_app_config.json' #this will not change

        # validate if config.json file exists and read json file to get path_app
        if os.path.exists(self.path_app_config_json):
            try:
                with open(self.path_app_config_json, "r") as json_file:
                    config_data = json.load(json_file)
                    self.path_app = config_data.get("AppDirectory")
                    path_data = self.path_app + 'data/'

                    # Validate if one of the directories is set up inside of the path_app directory.  If so assume the
                    # others are set up as well.
                    if os.path.exists(path_data):
                        self._set_paths()  # if all is good then set up the paths.  This will get called in setup_app_location if False is returned
                        return True
                    else:
                        return False

            except FileNotFoundError:
                self.error_msg = f"{self.path_app_config_json} file not found."
                self.error = True
                log.critical(self.error_msg)
                return None
            except json.JSONDecodeError:
                self.error_msg = f"Error decoding JSON from: {self.path_app_config_json}"
                self.error = True
                log.critical(self.error_msg)
                return None
            except Exception as e:
                self.error_msg = f"File not found: {self.path_app_config_json}"
                self.error = True
                log.critical(self.error_msg)
                return None

        else:
            #default scenario: make directory in documents folder with app name, and config if it doesn't exsist
            os.makedirs(path_app_config, exist_ok=True)

            # write out config.json with new default app value
            data = {"AppDirectory": starting_path_app}

            # Write the data to the JSON file
            with open(self.path_app_config_json, "w") as json_file:
                json.dump(data, json_file, indent=4)

            return False

        return False

    # see documentation above
    def setup_app_location(self, path_for_app_install):
        self.path_app = path_for_app_install + '/' + self.app_name + '/'

        # Create AppDirectory if it doesn't exist
        os.makedirs(self.path_app, exist_ok=True)
        log.msg(f"creating directory structure in: {self.path_app}")

        # Create subdirectories inside AppDirectory
        subdirectories = ["config", "data", "db", "results", "log", "temp", "temp/debug"]
        for subdirectory in subdirectories:
            subdirectory_path = os.path.join(self.path_app, subdirectory)
            os.makedirs(subdirectory_path, exist_ok=True)

        log.msg(f"Installation directory structure created successfully.{subdirectories}")

        #write out config.json with new path_app value
        data = { "AppDirectory": self.path_app }

        # Write the data to the JSON file
        with open(self.path_app_config_json, "w") as json_file:
            json.dump(data, json_file, indent=4)
        log.msg(f"JSON file with key 'AppDirectory' created at: {self.path_app_config_json}")

        self._set_paths()

    # copy any demo files to there default directory if requested
    def setup_demo_files(self):

        #copy files from resources/demo to path_data/username
        # 1) get list of demo files
        # 2) iterate over them getting the 2nd token from each which is the username
        # 3) create data directory with username if it doesn't exist
        # 4) copy file to said directory

        dp = self.get_demo_path()
        files = os.listdir(dp)
        athlete_list = []

        for file in files:
            athlete_full_path = os.path.join(dp, file)
            # validate it's a file
            athlete = ""
            if os.path.isfile(athlete_full_path):
                tokens = file.split('_')
                try:
                    athlete = tokens[1]
                    ap = self.path_data + athlete + '/'
                    if not os.path.isdir(ap):
                        os.makedirs(ap, exist_ok=True)
                        log.info(f"Creating athlete folder: {ap}.")
                    try:
                        shutil.copy(athlete_full_path, ap)
                        log.info(f"demo athlete: copied {file} to folder:{ap}.")
                    except IOError as e:
                        print(f"Unable to copy file: {file} to folder: {ap}  Error: {e}")

                except IndexError:
                    log.msg(f"Could not tokenize name to copy demo file: {file}")

                # check if user hasn't been added and if so add it.
                if athlete not in athlete_list:
                    # If not, add it to the list
                    athlete_list.append(athlete)
                    self.athletes_obj.add_athlete(athlete, 'right', .3)

        # add the athletes into the athletes file


        #create all_athletes.json file3 in side of path_db.  Technically, I am just running the
        # trial_manager.reprocess_all_files() command
        tm = jttm.JT_JsonTrialManager(self)
        tm.reprocess_all_files()   # pyqt is not sent in so there will not be a status bar on the screen

        pass

    def _set_paths(self):

        # setup path variables
        self.path_data = self.path_app + 'data/'
        self.path_results = self.path_app + 'results/'
        self.path_log = self.path_app + 'log/'
        self.path_db = self.path_app + 'db/'
        self.path_config = self.path_app + 'config/'

        # default db/tables names - can be changed but probably shouldn't be
        # These will go into a real database someday
        self.config_file_path = self.path_config + self.app_name + '_config.json'
        self.athletes_file_path = self.path_config + "athletes.csv"
        self.trial_mgr_filename = self.path_db + 'all_athletes.json'
        self.protocol_obj = None
        self.athletes_obj = None

        log.msg(f'path_app: {self.path_app}')
        log.msg(f'path_data: {self.path_data}')
        log.msg(f'path_results: {self.path_results}')
        log.msg(f'path_log: {self.path_log}')
        log.msg(f'path_db: {self.path_db}')
        log.msg(f'path_config: {self.path_config}')

        # setup protocol object
        try:
            self.protocol_obj = jtp.JT_protocol()
            ret = self.protocol_obj.validate_data()
            if len(ret) > 0:
                self.error_msg = "ERROR: Protocol Config Validation"
                self.error = True
                self.protocol_obj = None
        except:
            self.error_msg = f"Protocol Config File ERROR: {self.protocol_file_path} could not be opened or found"
            self.error = True
            log.error(self.error_msg)

        # setup athletes object
        try:
            # create the athletes Object
            self.athletes_obj = jta.JT_athletes(self) # get list of valid athletes from CSV file
            self.athletes_obj.get_athletes()
        except:
            self.error_msg = "Error: Athletes List Unable to be opened"
            self.error = True
            log.error(self.error_msg)
            self.athletes_obj = None

    #get the location of the documents folder for the particular OS
    def _get_os_document_path(self):
        if self.my_platform == "Darwin":

            # Get the path to the Documents folder on macOS
            self.documents_folder = os.path.expanduser("~/Documents") + '/'

        # Windows
        elif self.my_platform == "Windows":
            # Get the path to the Documents folder on macOS
            self.documents_folder = os.path.expanduser("~/Documents") + '/'

    def path_data_athlete(self, athlete):
        path = self.path_data + athlete + "/"
        # Check if the directory already exists
        if not os.path.exists(path):
            # Create the directory if it doesn't exist
            os.makedirs(path)
            log.msg(f'Directory created: {path}')
        return (path)

    def path_results_athlete(self, athlete):
        path = self.path_results + athlete + "/"
        # Check if the directory already exists
        if not os.path.exists(path):
            # Create the directory if it doesn't exist
            os.makedirs(path)
            log.msg(f'Directory created: {path}')
        return (path)

    def path_athlete_images(self, athlete):
        path = self.path_results + athlete + "/images/"
        # Check if the directory already exists
        if not os.path.exists(path):
            # Create the directory if it doesn't exist
            os.makedirs(path)
            log.msg(f'Directory created: {path}')
        return (path)

    #####################################
    # get key value - None is returned if not found/set
    #####################################
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

    #this function is used to convert paths if going between macOS and Windows.  Shouldn't affect anything if on same OS
    def convert_file_path(self, file_path):

        #only convert if file path does NOT exist
        if os.path.exists(file_path):
            return file_path

        # Find the index where "/Force Plate Testing/" ends
        app_dir = self.app_name + '/'
        index = file_path.find(app_dir)

        if index != -1:
            result = file_path[index + len(app_dir):]  # Extract everything after that part
            result = self.path_app + result
        else:
            log.info(f'convert_file_path ERROR:  {app_dir} not found in the file path')
            result = file_path

        if file_path != result:
            log.info(f"Converted: {file_path}\n    to:  {result}")

        return result

########################################################
# Utility functions
########################################################

    # function to validate if a image/icon/png is out there and if so it returns
    # a QImage, otherwise it returns None
    def validate_path_and_return_QImage(self, image_name):

        image_path = self.get_img_path() + image_name

        if not os.path.exists(image_path):
            log.error(f'Could not find image_path for: {image_path}')
            return None

        image = QImage(image_path)
        return image

    def validate_path_and_return_Pixmap(self, image_name):

        image_path = self.get_img_path() + image_name

        if not os.path.exists(image_path):
            log.error(f'Could not find image_path for: {image_path}')
            return None
        pixmap = QPixmap(image_path)
        return pixmap

    # Utility functions to access resources or demo files.  This is required for
    # pyinstaller which will hide these files away with in the imnage
    def get_img_path(self):

        path = os.path.join(self.base_path, 'resources/img/')
        return path

    def get_demo_path(self):
        path = os.path.join(self.base_path, 'resources/demo/')
        return path

########################################################

if __name__ == "__main__":
    # Test code
    file_path = 'config_testing.csv'  # Replace with the actual path to your CSV file

    # Create an instance of the DataProcessor
    config_obj = JT_Config('testLongName', 'TestSRT', None, file_path)

    config_obj.validate_install()

    log.debug( f"test1: should be nothing/fail: {config_obj.get_config('abc')}")
    log.debug( f"test2: stores a value: {config_obj.set_config('abc', 'abc_value1')}")
    log.debug( f"test3: stores a value: {config_obj.set_config('abc2', 'abc_value2')}")

    log.debug( f"test3: get abc2 value: {config_obj.get_config('abc2')}")
    log.debug( f"test3: get def2 value, should fail: {config_obj.get_config('def2')}")



