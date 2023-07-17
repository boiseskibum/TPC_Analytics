import sys
sys.path.append('../share')

# Import necessary modules
import os
import platform
import glob
import shutil

import datetime
from datetime import datetime
from datetime import timezone
import pytz  # used for timezones
import pandas as pd

#retrieve username and platform information
import getpass as gt
my_username = gt.getuser()
my_platform = platform.system()

import jt_util as util
import jt_athletes as jta

import process_cmj as p_cmj
import process_dj as p_dj
import process_sj as p_sj
import process_JTSext as p_JTSext

#set base and application path
path_base = util.jt_path_base()   # this figures out right base path for Colab, MacOS, and Windows
print(f"")

# setup path variables for base and misc
path_app = path_base + 'Force Plate Testing/'
path_data = path_app + 'data/'
path_results = path_app + 'results/'
path_log = path_app + 'log/'
path_temp = path_app + 'temp/'
path_temp2 = path_app + 'temp2/'
path_graphs = path_app + 'graphs/'
path_config = path_app + 'config/'

# Check if the directory already exists
if not os.path.exists(path_graphs):
    # Create the directory if it doesn't exist
    os.makedirs(path_graphs)
    print(f'Directory created: {path_graphs}')


#logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

log.msg(f'INFO - Valid logging levels are: {util.logging_levels}')
log.set_logging_level("WARNING")   # this will show errors but not files actually processed
#log.set_logging_level("INFO")   # this will show each file processed


# Save log file to the directory specified
#log.set_log_file(path_log, 'cmj_')

log.msg(f"path_base: {path_base}")
log.msg(f"my_username: {my_username}")
log.msg(f"my_system: {my_platform}")

# These are global variable that the dictionary full of columns from each test will be added to.
# if you add a new global make sure you add it to the reset_global() function
g_cmj_results_list = []
g_sl_results_list = []
g_sj_results_list = []
g_dj_results_list = []
g_JTSext_results_list = []
g_debug_log = []
global g_single_file_debug
g_single_file_debug = False


##### Get Athletes #####

athletes_list_filename = path_config + 'athletes.csv'
athletes_obj = None
try:
    # create the athletes Object
    athletes_obj = jta.JT_athletes(athletes_list_filename)  # get list of valid athletes from CSV file

except:
    log.critical(f"could not find athletes file to open {athletes_list_filename}" )

do_work = True

###############################################################################
# overall_process() - Process all athletes and files
###############################################################################
def overall_process(process_all=False, single_athlete = None):
    log.f()

    # reset or clear global results from last time program was run
    g_cmj_results_list.clear()
    g_sl_results_list.clear()
    g_sj_results_list.clear()
    g_dj_results_list.clear()
    g_JTSext_results_list.clear()
    g_debug_log.clear()
    global g_single_file_debug
    g_single_file_debug = False


    # path to the file that will store the list of processed files
    processed_files_file = path_log + 'processed_files.txt'

    # read the list of previously processed files
    processed_files = set()
    if process_all == False:
        if os.path.exists(processed_files_file):
            with open(processed_files_file, "r") as f:
                for line in f:
                    processed_files.add(line.strip())

    #get list of athletes (folders in data directory)
    folders = []
    for entry in os.scandir(path_data):
        if entry.is_dir():
            folders.append(entry.name)

    log.debug(f'folders: {folders}')

    # process new files
    new_files = []

    # allow all athletes to be processed or just a single one
    if single_athlete == None:
        # process athletes one at a time
        for athlete in folders:
            log.msg(f'Processing files for athlete: {athlete}')
            process_athlete(athlete, new_files, processed_files)
    else:
        log.msg(f'Processing files for SINGLE athlete: {single_athlete}')
        process_athlete(single_athlete, new_files, processed_files)

    # update the list of processed files
    with open(processed_files_file, "a") as f:
        for filename in new_files:
            f.write(filename + "\n")

    log.msg(f'Completed processing')

    #for each type of test or jump save results to csv file (see globals above)
    log_results(g_cmj_results_list, 'cmj', process_all)
    log_results(g_sl_results_list, 'sl', process_all)
    log_results(g_sj_results_list, 'sj', process_all)
    log_results(g_dj_results_list, 'dj', process_all)
    log_results(g_JTSext_results_list, 'JTSext', process_all)
    log_results(g_debug_log, 'debug_log', process_all)   #write the debug_log

    log.info(f'finished')

##### Main Single File#####
def single_file_process(s_filename=None):  #= app_data + 'Jade Warren/cmj_01.csv'):
    log.f()

    g_cmj_results_list.clear()
    g_sl_results_list.clear()
    g_sj_results_list.clear()
    g_dj_results_list.clear()
    g_JTSext_results_list.clear()
    g_debug_log.clear()
    global g_single_file_debug
    g_single_file_debug = True

    athlete = s_filename.split('/')[0]
    protocol = get_file_protocol(s_filename)

    leg = athletes_obj.get_injured_side(athlete)

    log.info(f"SINGLE File Process: {s_filename}")
    my_dict = process_file(path_data + s_filename, protocol, athlete, leg)

    results_df = pd.DataFrame([my_dict])
    my_csv = path_temp2 + 'debug_data.csv'
    results_df.to_csv(my_csv)

    my_flatfile = path_temp2 + 'debug_data_flat.txt'
    #create flat file with value
    with open(my_flatfile, "w") as file:
        # Write each key/value pair to a new line
        for key, value in my_dict.items():
            file.write(f"{key} {value}\n")


#### log results to csv file ####
def log_results(my_list, protocol, process_all):

    if len(my_list) < 1:
        log.msg(f'NO rows to store for {protocol}: Nothing written to file')
    return

    #create dataframe from my_list
    df = pd.DataFrame(my_list)

    #set up where file is written and sort the dataframe if it is the debug_log
    if protocol == 'debug_log':
        my_csv_filename = path_log + protocol + '_data.csv'
        df = df.sort_values(['athlete', 'protocol', 'timestamp_str'], ascending=[True, True, True])
    else:
        my_csv_filename = path_app + protocol + '_data.csv'

    log.msg(f'Results for {protocol}: number of rows {len(my_list)} written to file: {my_csv_filename}')

    # append results if doing incremental processing AND there is rows to write
    # OR overwrite the existing file if 'processing all' files
    if process_all == False:
        df.to_csv(my_csv_filename, mode='a', header=not os.path.isfile(my_csv_filename), index=True)

    # over write file if in processing all files
    else:
        df.to_csv(my_csv_filename)

    # debug_log only: for backup purposes create a backup
    # copy the existing file to a permanent log file with the date appended
    if protocol == 'debug_log':
        file_name, file_ext = my_csv_filename.split('.')

    now = get_local_timestamp()
    date_str = now.strftime('%Y-%m-%d %H:%M:%S')

    backup_filename = f"{file_name} {date_str}.{file_ext}"

    log.msg(f'Copying {my_csv_filename} to backup: {backup_filename}')

    # Copy the original file to the new file with the date appended
    shutil.copyfile(my_csv_filename, backup_filename)

#### Given filename, return protocol
def get_file_protocol(filename):
    #get protocol from the filename
    #this gets the characters to the "_" (ie cmj, or sl) then adds the '_' to those letters
    short_filename = os.path.splitext(os.path.basename(filename))[0]

    s_protocol = short_filename.split('_')[0] + '_'

    return(s_protocol)

#### convert timestamp to local time or return the current timestamp  ####
def get_local_timestamp(timestamp_obj = None):

    timezone = 'US/Mountain'
    local_tz = pytz.timezone(timezone)

    if timestamp_obj is None:
        local_timestamp_obj = datetime.now(local_tz)
    else:
        local_timestamp_obj = datetime.fromtimestamp(timestamp_obj, local_tz)

    return(local_timestamp_obj)


#### process_athlete ##############################################################
# Iterate through the athletes then process all files for each athlete
def process_athlete(athlete, new_files, processed_files):

    injured = athletes_obj.get_injured_side(athlete)

    #get all csv files in a path and sort based upon time
    path = path_data + athlete + '/*.csv'
    log.msg(f'Processing files in folder: {path}')

    file_list = glob.glob(path)

    file_list = [os.path.normpath(file_path) for file_path in file_list]   # line added so windows doesn't put a backslash in.

    file_list.sort(key=os.path.getmtime)
    #log.debug(f'filelist: {file_list}')

    # process each file one at a time
    j = 0
    errors = 0
    for filename in file_list:

        if filename not in processed_files:

            # counter for the number of files processed, for readability only
            j+= 1

            protocol = get_file_protocol(filename)

            log_dict = {}

            try:
                #log.debug( f'***** Process Single file--> protocol: {protocol}, athlete: {athlete}, injured: {injured}  {filename}')
                process_file(filename, protocol, athlete, injured)
                new_files.append(filename)

            except:
                log.error(f"FAILED TO PROCESS FILE: {filename}, {protocol}, {athlete}, {injured}")
                errors += 1

                #debug_log - write what information we can to even though there was an error processing the file
                short_filename = os.path.splitext(os.path.basename(filename))[0]
                log_dict['status'] = 'error'
                log_dict['athlete'] = athlete
                log_dict['protocol'] = protocol
                log_dict['short_filename'] = short_filename
                log_dict['filename'] = filename
                g_debug_log.append(log_dict)

            # used to show progress on processing files - readability only
            if(j % 20 == 0):
                log.msg( f'{j} files processed' )

    log.msg( f'{j} total files for {athlete}, good: {j-errors}, errors: {errors}' )


##### process a specific filen ####################################################
# valid protocols are filename starting with cmj or sl_
def process_file(filename, protocol, athlete, injured):

    creation_time_obj = os.path.getctime(filename)
    modification_time_obj = os.path.getmtime(filename)

    local_file_create_obj = get_local_timestamp(creation_time_obj)
    local_file_mod_obj = get_local_timestamp(modification_time_obj)

    #for debug
    local_file_create_str = local_file_create_obj.strftime('%Y-%m-%d %H:%M:%S')
    local_file_mod_str = local_file_mod_obj.strftime('%Y-%m-%d %H:%M:%S')

    # figure out if creation time is actually newer than modification time and if
    # so then change creation time to the older time (modification).  It is a hack
    # but it works
    if local_file_create_obj > local_file_mod_obj:
        local_datestamp_obj = local_file_mod_obj
    else:
        local_datestamp_obj = local_file_create_obj

    datestamp_str = local_datestamp_obj.strftime('%Y-%m-%d %H:%M:%S')
    date_str = local_datestamp_obj.strftime('%Y-%m-%d')

    path_athlete_graph = path_graphs + athlete + '/' + date_str + '/'
    # Check if the directory already exists
    if not os.path.exists(path_athlete_graph):
        # Create the directory if it doesn't exist
        os.makedirs(path_athlete_graph)
        log.debug(f'Directory created: {path_athlete_graph}')

    #just the filename is created as it will be passed into the functions doing work below
    short_filename = os.path.splitext(os.path.basename(filename))[0]

    log.f(f'File:  {filename}, {datestamp_str}, {date_str}')

    #debug code to create debug_log_data.csv
    log_dict = {}
    log_dict['status'] = 'success'
    log_dict['athlete'] = athlete
    log_dict['protocol'] = protocol
    log_dict['short_filename'] = short_filename
    log_dict["timestamp_str"] = str(local_datestamp_obj)  # by doing this it includeds the UTC offset
    log_dict["date_str"] = date_str
    log_dict["file create time"] = local_file_create_str
    log_dict["file mod time"] = local_file_mod_str
    log_dict['filename'] = filename

    #set up my_dict to pass variables to the csv file
    my_dict = {}

    # turn this flag to False to just provide list of all files to be processed

    if(do_work == True):

        # files starting with JT are all of Jakes protocols since leaving BSU and these files open as a normal CSV unlike the
        # BSU files where we had to skiprows and have a header line called out.
        if protocol[:2] == "JT":
            df = pd.read_csv(filename)
        else:
            df = pd.read_csv(filename, skiprows=[1, 2, 4], header=1)

        if protocol == "cmj_":

            # Validate and fix files if there are problems
            dl = validate_file(df)
            df = fix_cmj_zero_row(df, dl)

            # Process the cmj file
            my_dict = p_cmj.process_cmj_df(df, injured, short_filename, path_athlete_graph, athlete, date_str)
            my_dict['athlete_name'] = athlete
            my_dict ["col_timestamp_str"] = datestamp_str
            my_dict ["date_str"] = date_str
            my_dict ["timezone"] = timezone
            g_cmj_results_list.append(my_dict)

        # single leg
        elif protocol == "sl_":

            # Process a Right or Left leg file
            my_dict = p_cmj.process_sl_cmj_df(df)
            if "sl_r" in filename:
                my_dict["leg"] = "right"
            else:
                my_dict["leg"] = "left"

            my_dict['athlete_name'] = athlete
            my_dict ["col_timestamp_str"] = datestamp_str
            my_dict ["date_str"] = date_str
            my_dict ["timezone"] = timezone
            g_sl_results_list.append(my_dict)

        # drop jump
        elif protocol == "dj_":
            my_dict = p_dj.process_dj_df(df, injured)
            my_dict['athlete_name'] = athlete
            my_dict ["col_timestamp_str"] = datestamp_str
            my_dict ["date_str"] = date_str
            my_dict ["timezone"] = timezone
            g_dj_results_list.append(my_dict)

        # squat jump
        elif protocol == "sj_":
            my_dict = p_sj.process_sj_df(df, injured)
            my_dict['athlete_name'] = athlete
            my_dict ["col_timestamp_str"] = datestamp_str
            my_dict ["date_str"] = date_str
            my_dict ["timezone"] = timezone
            g_sj_results_list.append(my_dict)

        # JT Single Extension, both R and L are processed the same way.  The leg is
        #included in the file as one of the columns so they are distinguished that way
        elif protocol == "JTSextR_" or protocol == "JTSextL_":
            my_dict = p_JTSext.process_iso_knee_ext(df)
            my_dict['athlete_name'] = athlete
            my_dict ["col_timestamp_str"] = datestamp_str
            my_dict ["date_str"] = date_str
            my_dict ["timezone"] = timezone
            g_JTSext_results_list.append(my_dict)

        elif protocol == "bw_" or protocol == "rh_":
            pass

        else:
            log.error(f'FILE: {filename} no such protocol: {protocol}')

    else:
        pass

    #debug code to create debug_log_data.csv
    g_debug_log.append(log_dict)

    return(my_dict)   #my_dict only returned for single file processing

#### Validation code  ############################################################

def validate_file(df):
    log.f()
    df.rename(columns={'Fz': 'Right'}, inplace=True)
    df.rename(columns={'Fz.1': 'Left'}, inplace=True)

    # log.debug( "VALIDATION 1 - count zero values and left and right for comparison")

    # validation 1 - count zero values in left and right
    zero_counter_right = df['Right'].value_counts()[0]
    # log.debug( ic.format(zero_counter_right))
    zero_counter_left = df['Left'].value_counts()[0]
    # log.debug( ic.format(zero_counter_left))
    percent_dif = (zero_counter_right - zero_counter_left) / zero_counter_right * 100
    # log.debug( ic.format(percent_dif))

    zero_row_list = []

    log.debug(f"VALIDATION 2 - count instances of unexpected zero rows")
    # Validation 2 - count number of unexpected zero rows
    # Right Leg
    rc = 0
    rzc = 0
    lzc = 0
    ignore_zero = False
    df = df.reset_index()  # make sure indexes pair with number of rows

    for index, row in df.iterrows():

        # right side
        if row.Right == 0:
            rzc += 1
            if lzc > 0:
                ignore_zero = True
        elif rzc > 0:
            if ignore_zero == False:
                # log.debug(f"Found Right: {rzc} zero rows at row count {rc}")
                start_row = rc - rzc
                end_row = rc
                zero_row_dict = {'start_row': start_row, 'end_row': end_row, 'leg': "Right"}
                zero_row_list.append(zero_row_dict)
            rzc = 0
            if ignore_zero == True and lzc == 0:
                ignore_zero = False

        # left side
        if row.Left == 0:
            lzc += 1
            if rzc > 0:
                ignore_zero = True
        elif lzc > 0:
            if ignore_zero == False:
                # log.debug(f"Found Left: {lzc} zero rows at row count {rc}")
                start_row = rc - lzc
                end_row = rc
                zero_row_dict = {'start_row': start_row, 'end_row': end_row, 'leg': "Left"}
                zero_row_list.append(zero_row_dict)
            lzc = 0
            if ignore_zero == True and rzc == 0:
                ignore_zero = False
        rc += 1

    return zero_row_list


##### fix/eliminate zero rows in a specific cmj_data_frame

def fix_cmj_zero_row(df, zero_row_list):
    log.f()
    # new_zero_row_list = []

    for my_dict in zero_row_list:
        log.debug(f'          my_dict: {my_dict}')
        sr = my_dict['start_row']
        er = my_dict['end_row']
        leg = my_dict['leg']
        # new_value = df.iloc[sr - 1][leg]
        i = sr
        # Interpolation Calculations
        nr = er - sr
        delta = (df.at[er, leg] - df.at[sr - 1, leg]) / (nr + 1)
        # log.debug(f'nr: {nr}')
        # log.debug(f'delta: {delta}')
        j = 1
        while i < er:
            new_value = ((delta) * j) + df.at[sr - 1, leg]
            # log.debug(f'    new_value: {new_value}')
            j += 1
            df.at[i, leg] = new_value
            i += 1

    # filename = path_app +'fixed_data.csv'

    # df.to_csv(filename)

    return df


#####################################################################################
if __name__ == "__main__":

    # log.set_logging_level("WARNING")
    # log.set_logging_level("INFO")
    log.set_logging_level("DEBUG")

    # main(True)

    do_work = True   # this is global that can be set to false and it doesn't actually do the processing

#    overall_process(True, "Mickey", )

    single_file_process('Mickey/JTSextL_Mickey_20230716_153212.csv')   #JTSextL_, Mickey, left
    # single_file_process('Sophia Avalos/cmj_04.csv')
