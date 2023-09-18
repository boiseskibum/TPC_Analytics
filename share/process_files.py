import sys

# Import necessary modules
import os
import platform
import glob

import pandas as pd

#retrieve username and platform information
import getpass as gt
my_username = gt.getuser()
my_platform = platform.system()

if __name__ == "__main__":
    import jt_util as util
    import jt_athletes as jta
    import jt_protocol as jtp
    import jt_trial as jtt
    import jt_config as jtc
#    import JT_AFA.jt_athletes as jta
#    import JT_AFA.jt_protocol as jtp
else:
    from . import jt_util as util
    from . import jt_athletes as jta
    from . import jt_protocol as jtp
    from . import jt_trial as jtt
    from . import jt_config as jtc

from share import process_JTDcmj as p_JTDcmj, process_JTSext as p_JTSext

#set base and application path
path_base = util.jt_path_base()   # this figures out right base path for Colab, MacOS, and Windows

# setup path variables for base and misc
path_app = path_base + 'Force Plate Testing/'
path_data = path_app + 'data/'
path_db = path_app + 'db/'
path_results = path_app + 'results/'
path_log = path_app + 'log/'
path_temp = path_app + 'temp/'
path_temp2 = path_app + 'temp2/'
path_config = path_app + 'config/'


# Check if the directory already exists
if not os.path.exists(path_db):
    # Create the directory if it doesn't exist
    os.makedirs(path_db)
    print(f'Directory created: {path_db}')

#logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

log.msg(f'INFO - Valid logging levels are: {util.logging_levels}')
log.set_logging_level("WARNING")   # this will show errors but not files actually processed

# Save log file to the directory specifie
#log.set_log_file(path_log, 'cmj_')

log.msg(f"path_base: {path_base}")
log.msg(f"my_username: {my_username}")
log.msg(f"my_system: {my_platform}")

###############################################
# configuration object for keys and values setup
config_obj = jtc.JT_Config(path_app)

#protocol configs holds all the infor about single, double, name and actual protocol used
protocol_obj = None
try:
    protocol_obj = jtp.JT_protocol(config_obj)
except:
    log.critical(f"could not find protocol config file to open: {config_obj.protocol_file_path}.   Exiting program" )
    sys.exit(1)

##### Get Athletes #####

athletes_obj = None
try:
    # create the athletes Object
    athletes_obj = jta.JT_athletes(config_obj)  # get list of valid athletes from CSV file
except:
    log.critical(f"could not find athletes file to open: {config_obj.athletes_file_path}.   Exiting program")
    sys.exit(1)

do_work = True


###############################################
#### delete given athlete from output tiles
def delete_athlete(protocol, athlete):

    my_csv_filename = path_db + protocol + '_data.csv'
    if os.path.exists(my_csv_filename):

        # Read the DataFrame from CSV
        df = pd.read_csv(my_csv_filename)

        # Filter out rows with athlete_name="Steve Taylor"
        df_filtered = df[df['athlete_name'] != athlete]

        # Reset the index
        df_filtered = df_filtered.reset_index(drop=True)

        # Save the filtered DataFrame to a new CSV file
        df_filtered.to_csv(my_csv_filename, index=False)

    else:
        pass

###############################################
#### log results to csv file ####
def log_results(my_dict, protocol):

    my_list = [my_dict]
    if len(my_list) < 1:
        log.msg(f'NO rows to store for {protocol}: Nothing written to file')
        return

    #create dataframe from my_list
    df = pd.DataFrame(my_list)

    #set up where file is written and sort the dataframe if it is the debug_log
    if protocol == 'debug_log':
        my_csv_filename = path_log + protocol + '_data.csv'
    else:
        my_csv_filename = path_db + protocol + '_data.csv'

    #log.msg(f'Results for {protocol}: number of rows {len(my_list)} written to file: {my_csv_filename}')

    # append if file exists,  if not then create it
    log.debug(f'SAVING RESULTS to file: {my_csv_filename}')
    if os.path.exists(my_csv_filename):
        # append results
        df.to_csv(my_csv_filename, mode='a', header=not os.path.isfile(my_csv_filename), index=True)
    else:
        #create new file
        df.to_csv(my_csv_filename)

def log_debug_results(my_dict):
    results_df = pd.DataFrame([my_dict])
    my_csv = path_temp2 + 'debug_data.csv'
    results_df.to_csv(my_csv)

    my_flatfile = path_temp2 + 'debug_data_flat.txt'
    #create flat file with value
    with open(my_flatfile, "w") as file:
        # Write each key/value pair to a new line
        for key, value in my_dict.items():
            file.write(f"{key} {value}\n")

#### Given filename, return protocol
def get_file_protocol(filename):
    #get protocol from the filename
    #this gets the characters to the "_" (ie cmj, or sl) then adds the '_' to those letters
    short_filename = os.path.splitext(os.path.basename(filename))[0]

    s_protocol = short_filename.split('_')[0] + '_'

    return(s_protocol)
###############################################################################
# overall_process() - Process all athletes and files
###############################################################################
def process_all_athletes():
    log.f()

    #get list of athletes (folders in data directory)
    folders = []
    for entry in os.scandir(path_data):
        if entry.is_dir():
            folders.append(entry.name)

    log.debug(f'folders: {folders}')

    # loop through all athletes
    for athlete in folders:
        log.msg(f'Processing files for athlete: {athlete}')
        process_athlete(athlete)

    log.msg(f'Completed processing for all athletes')


#### process_athlete ##############################################################
# Iterate through the athletes then process all files for each athlete, this forces all files to be redone
def process_athlete( athlete ):

    # get list of files for athlete
    path = path_data + athlete + '/*.csv'
    file_list = glob.glob(path)
    file_list = [os.path.normpath(file_path) for file_path in file_list]   # line added so windows doesn't put a backslash in.
    log.debug(f'PROCESSING all files for: {athlete}')
    file_list.sort(key=os.path.getmtime)
    #log.debug(f'filelist: {file_list}')

    delete_athlete('JTDcmj', athlete)
    delete_athlete('JTSext', athlete)

    # process each file one at a time
    j = 0
    errors = 0
    for filename in file_list:

        # counter for the number of files processed, for readability only
        j+= 1
        log_dict = {}
            #log.debug( f'***** Process Single file--> protocol: {protocol}, athlete: {athlete}, injured: {injured}  {filename}')
        result = process_single_file(filename)
        if result == None:
            errors += 1
        # used to show progress on processing files - readability only
        if(j % 20 == 0):
            log.msg( f'{j} files processed' )

    log.msg( f'{j} total files for {athlete}, good: {j-errors}, errors: {errors}' )


##### process a specific filen ####################################################
# valid protocols are filename starting with cmj or sl_
# this returns a dictionary containing any files created while running.  Mostly likely Graphs

def process_single_file( file_path, debug=False):
    log.f(f"file_path: {file_path}, path_data: {path_data}")

    # get trial information
    trial = jtt.JT_Trial()
    # get dates and directories
    try:
        # get trial object which has all the details
        trial.validate_trial_path(file_path, path_data)

    except:
        log.info(f"File name didn't meet specification or exist (protocol_username_date_time) so ignoring: {file_path}")
        return False

    injured = athletes_obj.get_injured_side(trial.athlete)

    #create path where results go
    path_athlete_results = path_results + trial.athlete + '/' + trial.date_str + '/'
    # Check if the directory already exists for results and if not creates it
    if not os.path.exists(path_athlete_results):
        # Create the directory if it doesn't exist
        os.makedirs(path_athlete_results)
        log.debug(f'Directory created: {path_athlete_results}')

    #update file_path in case the JT_Trial object improved it by adding the full path to it
    file_path = trial.file_path

    log.f(f'File:  {file_path}, {trial.timestamp_str}, {trial.date_str}')

    ##### Process the File #####

    #debug code to create debug_log_data.csv
    log_dict = {}
    log_dict['status'] = 'success'
    log_dict['athlete'] = trial.athlete
    log_dict['protocol'] = trial.protocol
    log_dict['short_filename'] = trial.short_filename
    log_dict["timestamp_str"] = trial.timestamp_str
    log_dict["date_str"] = trial.date_str
    log_dict['filename'] = trial.file_path

    #set up my_dict to pass variables to the csv file
    my_dict = {}
    return_dict = {}

    # turn this flag to False to just provide list of all files to be processed
    if(do_work == True):

        try:
            standard_dict = {}
            standard_dict['original_filename'] = trial.short_filename + '.csv'
            standard_dict['athlete_name'] = trial.athlete
            standard_dict["col_timestamp_str"] = trial.timestamp_str
            standard_dict["date_str"] = trial.date_str

            # read in csv file to be processed


            # JT Single Extension, both R and L are processed the same way.  The leg is
            #included in the file as one of the columns so they are distinguished that way
            if trial.protocol.startswith("JTSext"):

                # get the leg being tested.   This is different than injured which is not used here
                tested_leg = protocol_obj.get_leg_by_protocol(trial.protocol)
                trial.shank_length = athletes_obj.get_shank_length(trial.athlete)

                df = pd.read_csv(file_path)
                process_obj = p_JTSext.process_iso_knee_ext(trial,  path_athlete_results)
                my_dict = process_obj.process()
                my_dict.update(standard_dict)

                if debug:
                    log_debug_results(my_dict)
                else:
                    # NOTE::::   for left and right protocols the values are all put into the same file, hence L and R are dropped
                    log_results(my_dict, "JTSext")
                    return_dict = {key: value for key, value in my_dict.items() if "GRAPH_" in key}

            elif trial.protocol == "JTDcmj":

                # Process the cmj file
                process_obj = p_JTDcmj.JTDcmj(trial, path_athlete_results)

                my_dict = process_obj.process()
                my_dict.update(standard_dict)

                if debug:
                    log_debug_results(my_dict)
                else:
                    log_results(my_dict, trial.protocol)
                    return_dict = {key: value for key, value in my_dict.items() if "GRAPH_" in key}

            else:
                log.error(f'FILE: {file_path} no such protocol: {trial.protocol}')
                return None

        except:
            log.error(f"FAILED TO PROCESS FILE: {file_path}, {trial.protocol}, {trial.athlete}, {injured}")

            log_dict = {}
            #debug_log - write what information we can to even though there was an error processing the file
            log_dict['status'] = 'error'
            log_dict['athlete'] = trial.athlete
            log_dict['protocol'] = trial.protocol
            log_dict['short_filename'] = trial.short_filename + '.csv'
            log_dict['filename'] = file_path

            log_results(log_dict, 'debug_log')

            return None

    else:
        pass

    #debug code to create debug_log_data.csv
    log_results(log_dict, 'debug_log')

    return return_dict


#####################################################################################
#### MAIN ###########################################################################
#####################################################################################
if __name__ == "__main__":

#    log.set_logging_level("WARNING")
#    log.set_logging_level("INFO")
    log.set_logging_level("DEBUG")

    do_work = True   # this is global that can be set to false and it doesn't actually do the processing

#    process_all_athletes()
#    process_athlete("Mickey")
#    process_athlete("Avery McBride")

    #process_single_file('Mickey/JTSextL_Mickey_20230627_201411.csv', True)   #True is for debug mode
    #process_single_file('Mickey/JTDcmj_Mickey_20230708_224659.csv', True)   #True is for debug mode
#    process_single_file('Avery McBride/JTSextR_Avery McBride_20230717_164704.csv', False)   #True is for debug mode
#    process_single_file('JTDcmj_huey_2023-08-17_00-46-31.csv', False)   #True is for debug mode

    process_single_file('JTDcmj_huey_2023-08-17_00-27-47.csv', False)  # True is for debug mode
