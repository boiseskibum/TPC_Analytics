# Import necessary modules
import os
import platform
import glob
import shutil
import sys

import datetime
from datetime import datetime
from datetime import timezone
import pandas as pd

import pytz  # used for timezones
import math
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pickle import FALSE

from scipy import signal
from scipy.integrate import cumtrapz
from scipy.signal import argrelextrema, find_peaks

np.set_printoptions(threshold=False)

# Importing Colors
colors_blue = sns.color_palette('Blues', 10)
colors_grey = sns.color_palette('Greys', 10)
colors = sns.color_palette('rocket', 10)
colors_icefire = sns.color_palette('icefire', 10)
colors3 = sns.color_palette('rainbow', 5)
colors_seismic = sns.color_palette('seismic', 10)

######################################################################
# set up path and debuggging

# retrieve username and platform information
import getpass as gt

my_username = gt.getuser()
my_platform = platform.system()

# appends the path to look for files to the existing path


# mount drive if in google collab()
my_platform = platform.system()

import jt_util as util

# set base and application path
path_base = util.jt_path_base()  # this figures out right base path for Colab, MacOS, and Windows
print(f"")

# setup path variables for base and misc
path_app = path_base + 'Force Plate Testing/'
path_data = path_app + 'data/'
path_results = path_app + 'results/'
path_log = path_app + 'log/'
path_temp = path_app + 'temp/'
path_temp2 = path_app + 'temp2/'
path_graphs = path_app + 'graphs/'

# validate that all paths exist
if not os.path.isdir(path_data):
    print(f'ERROR path: {path_data} does not exist')

# Check if the directory already exists
if not os.path.exists(path_graphs):
    # Create the directory if it doesn't exist
    os.makedirs(path_graphs)
    print(f'Directory created: {path_graphs}')

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

log.msg(f'INFO - Valid logging levels are: {util.logging_levels}')
log.set_logging_level("WARNING")  # this will show errors but not files actually processed
# log.set_logging_level("INFO")   # this will show each file processed


# Save log file to the directory specified
# log.set_log_file(path_log, 'cmj_')


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

"""#High Level Program Flow"""


###############################################################################
# Main() - Process all athletes and files
#

def main(process_all=False, single_athlete=None):
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

    # get list of athletes (folders in data directory)
    folders = []
    for entry in os.scandir(path_data):
        if entry.is_dir():
            folders.append(entry.name)

    log.debug(f'folders: {folders}')

    # process new files
    new_files = []

    # allow all athletes to be processed or just a single one
    if single_athlete == none:
        # process athletes one at a time
        for athlete in folders:
            log.msg(f'Processing files for athlete: {athlete}')
            process_athlete(athlete, new_files, processed_files)
    else:
        log.msg(f'Processing files for SINGLE athlete: {athlete}')
        process_athlete(single_athlete, new_files, processed_files)


# update the list of processed files
with open(processed_files_file, "a") as f:
    for filename in new_files:
        f.write(filename + "\n")

log.msg(f'Completed processing')

# for each type of test or jump save results to csv file (see globals above)
log_results(g_cmj_results_list, 'cmj', process_all)
log_results(g_sl_results_list, 'sl', process_all)
log_results(g_sj_results_list, 'sj', process_all)
log_results(g_dj_results_list, 'dj', process_all)
log_results(g_JTSext_results_list, 'JTSext', process_all)
log_results(g_debug_log, 'debug_log', process_all)  # write the debug_log

log.info(f'finished')


##### Main Single File##### ------------------------------------------

def main_single_file(s_filename=None):  # = app_data + 'Jade Warren/cmj_01.csv'):
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

    leg = get_athlete_injury(athlete)

    log.info(f"SINGLE File Process: {s_filename}")
    my_dict = process_file(path_data + s_filename, protocol, athlete, leg)

    results_df = pd.DataFrame([my_dict])
    my_csv = path_temp2 + 'debug_data.csv'
    results_df.to_csv(my_csv)

    my_flatfile = path_temp2 + 'debug_data_flat.txt'
    # create flat file with value
    with open(my_flatfile, "w") as file:
        # Write each key/value pair to a new line
        for key, value in my_dict.items():
            file.write(f"{key} {value}\n")


#### log results to csv file #### --------------------------------------
def log_results(my_list, protocol, process_all):
    if len(my_list) < 1:
        log.msg(f'NO rows to store for {protocol}: Nothing written to file')
        return

    # create dataframe from my_list
    df = pd.DataFrame(my_list)

    # set up where file is written and sort the dataframe if it is the debug_log
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


####Given athlete, return which leg is injured
def get_athlete_injury(athlete):
    # look in athletes.csv to see which leg is injured
    # if it can't find the athlete throw an error
    # the CSV file can be simplified to just the athletes_name and the injured column, nothing else is needed
    athletes_file = path_app + 'athletes.csv'
    df = pd.read_csv(athletes_file)

    # if there is no match for the athlete then raise an error
    try:
        row = df.loc[df['athletes_name'] == athlete].iloc[0]
        # log.debug(f'athete row {row}')
        injured = row['injured']
    except IndexError:
        log.critical(f'Skipping Athlete name: {athlete}, does not exist in file: {athletes_file}')
        return ('ERROR')

    return (injured)


#### Given filename, return protocol
def get_file_protocol(filename):
    # get protocol from the filename
    # this gets the characters to the "_" (ie cmj, or sl) then adds the '_' to those letters
    short_filename = os.path.splitext(os.path.basename(filename))[0]

    s_protocol = short_filename.split('_')[0] + '_'

    return (s_protocol)


#### convert timestamp to local time or return the current timestamp  #### ------------------
def get_local_timestamp(timestamp_obj=None):
    timezone = 'US/Mountain'
    local_tz = pytz.timezone(timezone)

    if timestamp_obj is None:
        local_timestamp_obj = datetime.now(local_tz)
    else:
        local_timestamp_obj = datetime.fromtimestamp(timestamp_obj, local_tz)

    return (local_timestamp_obj)


##### Iterate through the athletes
# then process all files for each athlete

#### process_athlete #### --------------------------------------

def process_athlete(athlete, new_files, processed_files):
    injured = get_athlete_injury(athlete)

    # get all csv files in a path and sort based upon time
    path = path_data + athlete + '/*.csv'
    log.msg(f'Processing files in folder: {path}')

    file_list = glob.glob(path)
    file_list.sort(key=os.path.getmtime)
    # log.debug(f'filelist: {file_list}')

    # process each file one at a time
    j = 0
    errors = 0
    for filename in file_list:

        if filename not in processed_files:

            # counter for the number of files processed, for readability only
            j += 1

            protocol = get_file_protocol(filename)

            log_dict = {}

            try:
                # log.debug( f'***** Process Single file--> protocol: {protocol}, athlete: {athlete}, injured: {injured}  {filename}')
                process_file(filename, protocol, athlete, injured)
                new_files.append(filename)

            except:
                log.error(f"FAILED TO PROCESS FILE: {filename}, {protocol}, {athlete}, {injured}")
                errors += 1

                # debug_log - write what information we can to even though there was an error processing the file
                short_filename = os.path.splitext(os.path.basename(filename))[0]
                log_dict['status'] = 'error'
                log_dict['athlete'] = athlete
                log_dict['protocol'] = protocol
                log_dict['short_filename'] = short_filename
                log_dict['filename'] = filename
                g_debug_log.append(log_dict)

            # used to show progress on processing files - readability only
            if (j % 20 == 0):
                log.msg(f'{j} files processed')

    log.msg(f'{j} total files for {athlete}, good: {j - errors}, errors: {errors}')


"""# process_file()"""

from matplotlib.patches import Ellipse


##### process a specific filename #####  ----------------------------------
# valid protocols are filename starting with cmj or sl_

def process_file(filename, protocol, athlete, injured):
    creation_time_obj = os.path.getctime(filename)
    modification_time_obj = os.path.getmtime(filename)

    local_file_create_obj = get_local_timestamp(creation_time_obj)
    local_file_mod_obj = get_local_timestamp(modification_time_obj)

    # for debug
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

    # just the filename is created as it will be passed into the functions doing work below
    short_filename = os.path.splitext(os.path.basename(filename))[0]

    log.f(f'File:  {filename}, {datestamp_str}, {date_str}')

    # debug code to create debug_log_data.csv
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

    # set up my_dict to pass variables to the csv file
    my_dict = {}

    # turn this flag to False to just provide list of all files to be processed
    do_work = True
    if (do_work == True):

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
            my_dict = process_cmj_df(df, injured, short_filename, path_athlete_graph, athlete, date_str)
            my_dict['athlete_name'] = athlete
            my_dict["col_timestamp_str"] = datestamp_str
            my_dict["date_str"] = date_str
            my_dict["timezone"] = timezone
            g_cmj_results_list.append(my_dict)

        # single leg
        elif protocol == "sl_":

            # Process a Right or Left leg file
            my_dict = process_sl_cmj_df(df)
            if "sl_r" in filename:
                my_dict["leg"] = "right"
            else:
                my_dict["leg"] = "left"

            my_dict['athlete_name'] = athlete
            my_dict["col_timestamp_str"] = datestamp_str
            my_dict["date_str"] = date_str
            my_dict["timezone"] = timezone
            g_sl_results_list.append(my_dict)

        # drop jump
        elif protocol == "dj_":
            my_dict = process_dj_df(df, injured)
            my_dict['athlete_name'] = athlete
            my_dict["col_timestamp_str"] = datestamp_str
            my_dict["date_str"] = date_str
            my_dict["timezone"] = timezone
            g_dj_results_list.append(my_dict)

        # squat jump
        elif protocol == "sj_":
            my_dict = process_sj_df(df, injured)
            my_dict['athlete_name'] = athlete
            my_dict["col_timestamp_str"] = datestamp_str
            my_dict["date_str"] = date_str
            my_dict["timezone"] = timezone
            g_sj_results_list.append(my_dict)

        # JT Single Extension, both R and L are processed the same way.  The leg is
        # included in the file as one of the columns so they are distinguished that way
        elif protocol == "JTSextR_" or protocol == "JTSextL_":
            my_dict = process_iso_knee_ext(df)
            my_dict['athlete_name'] = athlete
            my_dict["col_timestamp_str"] = datestamp_str
            my_dict["date_str"] = date_str
            my_dict["timezone"] = timezone
            g_JTSext_results_list.append(my_dict)

        elif protocol == "bw_" or protocol == "rh_":
            pass

        else:
            log.error(f'FILE: {filename} no such protocol: {protocol}')

    else:
        pass

    # debug code to create debug_log_data.csv
    g_debug_log.append(log_dict)

    return (my_dict)  # my_dict only returned for single file processing


"""######  #Data Validation and fixing"""


##### validate a specific dataframe (from file)
# - returns a list of dictionaries where zero rows occured (dictionary has start, end, and left or right)

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

    log.debug(ic.format(f"VALIDATION 2 - count instances of unexected zero rows"))
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


##### #CMJ - process_cmj_df() #########################
##### process a cmj dataframe, must include which leg is injured ('Right', or 'Left')

def process_cmj_df(df, injured, short_filename, path_athlete, athlete, date):
    log.f()

    # rename columns so they are easier to deal with AND does abvolute value columns
    list_right = []
    df.rename(columns={'Fz': 'Right'}, inplace=True)
    # log.debug(df['Right'])
    df['Right'] = df['Right'].abs()  # absolute value of 'Right'
    list_right = df['Right'].to_list()  # adds data to form a list
    # log.debug(list_right)

    list_left = []
    df.rename(columns={'Fz.1': 'Left'}, inplace=True)
    df['Left'] = df['Left'].abs()  # absolute value of 'Left'
    list_left = df['Left'].to_list()  # adds data to form a list
    # log.debug(list_left)

    force_total = [sum(i) for i in zip(list_right, list_left)]  # sums the 2 lists so that total force can be calculated
    # log.debug(force_total)

    freq = 2400  # frequency
    g = 9.81  # gravity
    h = 0.3  # I don't know

    m_r = (np.mean(list_right[0:int(freq * 2)]) / g)  # calculation of Bodyweight - R
    m_l = (np.mean(list_left[0:int(freq * 2)]) / g)  # calculation of bodyweight - L
    mass = abs(float(m_r)) + abs(float(m_l))  # calculation of bodyweight total
    ('Subject Mass  {:.3f} kg'.format(mass))
    log.debug(f"mass: {mass}")

    # normalizing for bodyweight - See slides // subtract bodyweight and make BM = 0
    force_norm = np.subtract(force_total, mass * g)
    # log.debug(f"force_norm: {force_norm}")
    # plt.figure(figsize=(10,6))
    # plt.plot(force_norm, 'b.-', linewidth=1)

    # normalizing for bodyweight - R
    force_norm_r = np.subtract(list_right, (m_r * g))
    # log.debug(f"force_r: {force_norm_r}")
    # plt.figure(figsize=(10,6))
    # plt.plot(force_norm_r, 'b.-', linewidth=1)

    # normalizing for bodyweight - L
    force_norm_l = np.subtract(list_left, (m_l * g))
    # log.debug(f"force_l: {force_norm_l}")
    # plt.figure(figsize=(10,6))
    # plt.plot(force_norm_r,'g.-', linewidth=1)

    # plt.figure()
    # title = athlete + ' CMJ ' + date + ' ' + short_filename
    # plt.title(title, fontdict={'fontweight':'bold', 'fontsize': 12})
    # plt.plot(force_norm_r, linestyle = '-', label = 'Right', color=colors_seismic[2], linewidth = 1)
    # plt.plot(force_norm_l, linestyle = '-', label = 'Left', color=colors_icefire[4], linewidth = 1)
    # plt.xlabel('Time')
    # plt.ylabel('Force')
    # plt.legend()

    # graph_name = path_athlete + short_filename
    # log.debug(f"graph_name: {graph_name}")

    # plt.savefig(graph_name,
    #             transparent=False,
    #             facecolor='white', dpi=300,
    #             bbox_inches="tight")

    ##### Calling cmj calculation functions for both legs as well as left and right
    results_dict = cmj_calc(force_norm, mass)

    results_dict_l = cmj_sl_calc(force_norm_l, "left", m_l)
    cmj_arr_l = results_dict_l.get('cmj_arr')
    del results_dict_l['cmj_arr']

    results_dict_r = cmj_sl_calc(force_norm_r, "right", m_r)
    cmj_arr_r = results_dict_r.get('cmj_arr')
    del results_dict_r['cmj_arr']

    # create graph and have it stored permanently to file
    fig = plt.figure()
    title = athlete + ' CMJ ' + date + ' ' + short_filename
    plt.title(title, fontdict={'fontweight': 'bold', 'fontsize': 12})
    plt.plot(cmj_arr_l, linestyle='-', label='Left', color=colors_seismic[2], linewidth=1)
    plt.plot(cmj_arr_r, linestyle='-', label='Right', color=colors_icefire[4], linewidth=1)
    plt.xlabel('Time')
    plt.ylabel('Force')
    plt.legend()

    graph_name = path_athlete + short_filename
    log.debug(f"graph_name: {graph_name}")

    plt.savefig(graph_name,
                transparent=False,
                facecolor='white', dpi=300,
                bbox_inches="tight")
    plt.close(fig)

    # log.debug(f' L: {results_dict_l} R: {results_dict_r}')
    results_dict.update(results_dict_l)
    results_dict.update(results_dict_r)

    # force asymmetry calcs
    r = asym_index(results_dict['force_right'], results_dict['force_left'], injured, 'force_asymmetry_index')
    results_dict.update(r)
    r = asym_index(results_dict['unloading_force_right'], results_dict['unloading_force_left'], injured,
                   'unloading_force_asymmetry_index')
    results_dict.update(r)
    r = asym_index(results_dict['braking_force_right'], results_dict['braking_force_left'], injured,
                   'braking_force_asymmetry_index')
    results_dict.update(r)
    r = asym_index(results_dict['concentric_force_right'], results_dict['concentric_force_left'], injured,
                   'concentric_force_asymmetry_index')
    results_dict.update(r)

    # impulse asymmetry calcs
    r = asym_index(results_dict['impulse_right'], results_dict['impulse_left'], injured, 'impulse_asymmetry_index')
    results_dict.update(r)
    r = asym_index(results_dict['unloading_impulse_right'], results_dict['unloading_impulse_left'], injured,
                   'unloading_impulse_asymmetry_index')
    results_dict.update(r)
    r = asym_index(results_dict['braking_impulse_right'], results_dict['braking_impulse_left'], injured,
                   'braking_impulse_asymmetry_index')
    results_dict.update(r)
    r = asym_index(results_dict['concentric_impulse_right'], results_dict['concentric_impulse_left'], injured,
                   'concentric_impulse_asymmetry_index')
    results_dict.update(r)

    return results_dict


"""# process_sl_cmj_df()"""


##### process a single leg cmj file  NOTE: single leg

def process_sl_cmj_df(df):
    log.f()
    force_total = []
    df.rename(columns={'Fz': 'force'}, inplace=True)

    # log.debug('force')
    # log.debug(df['force'])
    df['force'] = df['force'].abs()  # absolute value of 'Right'
    force_total = df['force'].to_list()  # adds data to form a list
    # log.debug(force_total)

    freq = 2400  # frequency
    g = 9.81  # gravity
    h = 0.3  # I don't know

    mass = (np.mean(force_total[0:int(freq * 2)]) / g)
    ('Subject Mass  {:.3f} kg'.format(mass))
    mass = abs(float(mass))  # calculation of bodyweight total
    ('Subject Mass  {:.3f} kg'.format(mass))
    log.debug(f"mass: {mass}")

    # normalizing for bodyweight - See slides // subtract bodyweight and make BM = 0
    force_norm = np.subtract(force_total, mass * g)
    log.debug(f"force_norm: {force_norm}")

    ##### Calling CMJ function for both legs as well as left and right
    results_dict = cmj_calc(force_norm, mass)

    return results_dict


"""# cmj_calc() CMJ"""

##### cmj_calc() - does all calculations for a cmj

from numpy.linalg import tensorsolve


def cmj_calc(trial, mass):
    log.f("** CMJ calc")

    force = np.array(trial)
    # log.debug(f"cmj force:{force}")
    # normalizing for time
    freq = 2400
    g = 9.81  # gravity
    time = np.arange(0, len(force) / freq, 1 / freq)
    # log.debug(f"time: {time}")

    # ******************************* Indexing Key Points in the Jump******************************

    # Onset of Jump
    start_jump = np.where((force[0:] > 20) | (force[0:] < -20))  # if want to use one function, need to perform mass / 2
    log.debug(f'start_jump: {start_jump}')

    jump_onset_moment_index = start_jump[0][0]  # time stamps jump moment
    log.debug(f"INDEX jump_onset_moment_index: {jump_onset_moment_index}")

    # Start of the flight phase
    start_flight = np.where(
        force[0:] < (np.amin(force) + 10))  # need to create if statement so that left and right can be calculated
    # log.debug(f"min: {np.amin(force)}")
    # log.debug(f"start_flight: {start_flight}")
    takeoff_moment_index = start_flight[0][0]  # time stamps takeoff moment
    log.debug(f"INDEX takeoff_moment_index: {takeoff_moment_index}")

    # jump time (from start of jump until in the air)
    time_ss = time[
              jump_onset_moment_index:takeoff_moment_index]  # creates a time subset from jump onset moment to takeoff
    # log.debug(f"time_ss: {time_ss}")
    jump_time = time_ss[-1] - time_ss[0]  # total time of jump
    log.debug(f"jump_time: {jump_time}")

    cmj_arr = force[
              jump_onset_moment_index:takeoff_moment_index]  # creates force array from jump onset moment to takeoff
    peak_force = cmj_arr.max()
    log.debug(f"  peak force: {peak_force}")

    # ***********************Calculating Jump Height Jump Height Using the Acceleration Curve - all variables end with 2***************

    # Calculating Acceleration using F=ma
    acceleration2 = cmj_arr / mass
    # Debug plot to show show acceleration
    global g_single_file_debug  # should go at bottom and graph all curves
    if (g_single_file_debug == True):
        #  Graph impulse and delta_velocity
        plt.figure()
        plt.title('Acceleration Curve', fontdict={'fontweight': 'bold', 'fontsize': 12})
        plt.plot(acceleration2, linestyle='-', label='Acceleration', color=colors_seismic[2], linewidth=1)
        plt.xlabel('Time')
        plt.ylabel('Acceleration (m/s^2)')

    # Calculating velocity by integrating acceleration
    velocity2 = cumtrapz(acceleration2, x=time_ss, initial=0)
    if (g_single_file_debug == True):
        #  Graph impulse and delta_velocity
        plt.figure()
        plt.title('Velocity Curve', fontdict={'fontweight': 'bold', 'fontsize': 12})
        plt.plot(velocity2, linestyle='-', label='Velocity', color=colors_seismic[2], linewidth=1)
        plt.xlabel('Time')
        plt.ylabel('Velocity (m/s)')

    # Calculating peak negative velocity by finding the minimum of the velocity curve

    peak_negative_velocity = velocity2.min()
    log.debug(f"  peak_negative_velocity: {peak_negative_velocity}")

    # ** Calculating Jump Height Through Impulse Momentum Relationship ***********

    cmj_arr = force[jump_onset_moment_index:takeoff_moment_index]  # indexes the force from jump onset moment to takeoff
    peak_force = cmj_arr.max()
    log.debug(f"  peak force: {peak_force}")

    # **************************** Calculating Jump Height Through Impulse Momentum Relationship *********************************

    # calculating impulse
    impulse_arr = cumtrapz(cmj_arr, x=time_ss, initial=0)  # integrates force curve to produce impulse
    # log.debug(f"impulse_arr: {impulse_arr}")

    # calculating peak impulse
    peak_impulse = impulse_arr.max()
    log.debug(f"  peak_impulse: {peak_impulse}")

    # Calculating final impulse
    final_impulse = impulse_arr[-1]
    log.debug(f"  final_impulse: {final_impulse}")

    # calculating velocity
    delta_velocity = impulse_arr / (mass)  # change in velocity = impulse_arr / mass

    # log.debug(f"delta_velocity: {delta_velocity}")
    # log.debug(f"delta_velocity_len: {len(delta_velocity)}")

    # Debug plot to show show impulse and delta_velocity
    # global g_single_file_debug
    if (g_single_file_debug == True):
        #  Graph impulse and delta_velocity
        plt.figure()
        plt.title('impulse', fontdict={'fontweight': 'bold', 'fontsize': 12})
        plt.plot(impulse_arr, 'b.-', linewidth=1)

        plt.figure()
        plt.title('Delta Velocity')
        plt.plot(delta_velocity, 'b.-', linewidth=1)

    ToV = final_impulse / (mass)  # takeoff velocity = peak_impulse / mass
    log.debug(f"  Takeoff Velocity(ToV): {ToV}")

    # Verify takeoff velocity

    ToV_VERIFY = delta_velocity[-1]
    log.debug(f"  Takeoff Velocity(ToV) VERIFY: {ToV_VERIFY}")

    # calculating jump height
    jump_height = ((ToV) ** 2) / (2 * g)  # jump height = (takeoff velocity)**2 / (2*gravity)
    log.debug(f"  jump_height: {jump_height}")

    # ** Calculating Jump Height Through TIA (Control)****************************

    # Calculating time in air
    start_land = np.where(
        force[0:] == (np.amax(force)))  # need to create if statement so that left and right can be calculated
    landing_moment = start_land[0][0]
    tia_ss = time[takeoff_moment_index:landing_moment]
    tia_ss_total = tia_ss[-1] - tia_ss[0]
    # log.debug(f"tia_ss_total: {tia_ss_total}")

    # Calculating Jump Height with TIA
    jump_height_tia = .5 * g * ((tia_ss_total / 2) ** 2)
    log.debug(f"  jump_height_tia: {jump_height_tia}")

    # ** Calculating Reactive Strength Index (Modified) **

    # Calculating RSI Mod
    rsi_mod = jump_height / jump_time
    log.debug(f"  rsi_mod: {rsi_mod}")

    # ** Calculating Power **

    # calculating mean Power
    power = force[jump_onset_moment_index:takeoff_moment_index] * delta_velocity  # power = force * velocity
    mean_power = np.mean(power)  # mean power = average of the power calculated over the duration of jump
    log.debug(f"  average_power: {mean_power}")

    # calculating peak power
    peak_power = np.max(power)  # np.max - finds max
    log.debug(f"  peak_power: {peak_power}")

    # ** Calculating Displacement of CoM (Version 2)**

    CoM_displacement = cumtrapz(delta_velocity, x=time_ss, initial=0)
    if (g_single_file_debug == True):
        #  Graph impulse and delta_velocity
        plt.figure()
        plt.title('Center of Mass Displacement Curve', fontdict={'fontweight': 'bold', 'fontsize': 12})
        plt.plot(CoM_displacement, linestyle='-', label='CoM Displacement', color=colors_seismic[2], linewidth=1)
        plt.xlabel('Time')
        plt.ylabel('Displacement (m/s)')

    CoM_displacement_initial = CoM_displacement[0]

    CoM_displacement_min = CoM_displacement.min()
    log.debug(f"  CoM_displacement_min: {CoM_displacement_min}")

    CoM_displacement_value = abs(CoM_displacement_initial - CoM_displacement_min)

    # ** Calculating Lower Limb Stiffness **

    # Currently using peak force - need to attain force that correlates to peak displacement
    limb_stiffness = peak_force / CoM_displacement_value
    limb_stiffness_norm = limb_stiffness / mass
    log.debug(f"  limb_stiffness_norm: {limb_stiffness_norm}")

    # ** Calculating Impulse During Specific Phases of the Jump **

    ##################################
    # Unloading Phase
    velocity_min = (np.amin(delta_velocity))
    # log.debug(f"velocity_min: {velocity_min}")

    velocity_min_index = np.where(delta_velocity == np.amin(delta_velocity))
    velocity_min_index = velocity_min_index[0][0]
    log.debug(f"INDEX velocity_min_index: {velocity_min_index}")

    unloading_end_index = (jump_onset_moment_index + velocity_min_index)
    log.debug(f"INDEX unloading_end_index: {unloading_end_index}")

    unloading_force_arr = force[jump_onset_moment_index:unloading_end_index]
    unloading_time_arr = time[jump_onset_moment_index:unloading_end_index]
    unloading_time = unloading_time_arr[-1] - unloading_time_arr[0]
    log.debug(f"unloading_time: {unloading_time}")

    unloading_impulse_arr = cumtrapz(unloading_force_arr, unloading_time_arr, initial=0)
    # log.debug(f"unloading_impulse_arr: {unloading_impulse_arr}")

    ##JT FORCE INSTEAD OF IMPULSE CHECK
    peak_unloading_force = unloading_force_arr.min()
    peak_unloading_impulse = unloading_impulse_arr.min()
    log.debug(f"  peak_unloading_impulse: {peak_unloading_impulse}")

    ##################################
    # Braking Phase

    velocity_zero_index = np.where(delta_velocity[velocity_min_index:] > 0)
    velocity_zero_index = velocity_zero_index[0][0]
    log.debug(f"INDEX velocity_zero_index: {velocity_zero_index}")

    braking_end_index = (jump_onset_moment_index + velocity_min_index + velocity_zero_index)
    log.debug(f"INDEX  braking_end_index: {braking_end_index}")

    braking_force_arr = force[unloading_end_index:braking_end_index]
    # log.debug(f"braking_force_arr: {braking_force_arr}")
    braking_time_arr = time[unloading_end_index:braking_end_index]
    braking_time = braking_time_arr[-1] - braking_time_arr[0]
    log.debug(f"braking_time: {braking_time}")

    braking_impulse_arr = cumtrapz(braking_force_arr, braking_time_arr, initial=0)
    # log.debug(f"braking_impulse_arr: {braking_impulse_arr}")

    ##JT FORCE INSTEAD OF IMPULSE CHECK
    peak_braking_force = braking_force_arr.max()
    relative_braking_force = peak_braking_force / mass
    peak_braking_impulse = braking_impulse_arr.max()
    relative_braking_impulse = peak_braking_impulse / mass
    log.debug(f"  peak_braking_impulse: {peak_braking_impulse}")

    # calculating force at zero velocity
    force_at_zero_velocity = braking_force_arr[-1]
    log.debug(f"  force_at_zero_velocity: {force_at_zero_velocity}")

    ##################################
    # Concentric Phase - Zero Point on velocity curve to max of velocity curve

    velocity_max = (np.amax(delta_velocity))
    # log.debug(f"velocity_max: {velocity_max}")

    velocity_max_index = np.where(delta_velocity == np.amax(delta_velocity))
    velocity_max_index = velocity_max_index[0][0]
    log.debug(f"INDEX velocity_max_index: {velocity_max_index}")

    #                                12944                  1640
    concentric_end_index = (jump_onset_moment_index + velocity_max_index)
    log.debug(f"INDEX concentric_end_index: {concentric_end_index}")
    concentric_force_arr = force[braking_end_index:concentric_end_index]
    # log.debug(f"concentric_force_arr: {concentric_force_arr}")
    concentric_time_arr = time[braking_end_index:concentric_end_index]
    concentric_time = concentric_time_arr[-1] - concentric_time_arr[0]
    log.debug(f"concentric_time: {concentric_time}")

    concentric_impulse_arr = cumtrapz(concentric_force_arr, concentric_time_arr, initial=0)
    # log.debug(f"concentric_impulse_arr: {concentric_impulse_arr}")

    ##JT FORCE INSTEAD OF IMPULSE CHECK
    peak_concentric_force = concentric_force_arr.max()
    relative_concentric_force = peak_concentric_force / mass
    peak_concentric_impulse = concentric_impulse_arr.max()
    relative_concentric_impulse = peak_concentric_impulse / mass
    log.debug(f"  peak_concentric_impulse: {peak_concentric_impulse}")

    # Debug plot to show different indexes

    if (g_single_file_debug == True):
        temp_force = force[jump_onset_moment_index:(takeoff_moment_index + 1000)]

        fig = plt.figure()
        plt.title('Debug Graph', fontdict={'fontweight': 'bold', 'fontsize': 12})
        plt.plot(temp_force, linestyle='-', label='Left', color=colors_seismic[2], linewidth=1)

        # defining an array
        xs = [0, 500]

        dif = jump_onset_moment_index
        # multiple lines all full height
        plt.vlines(x=[jump_onset_moment_index - dif, unloading_end_index - dif, braking_end_index - dif,
                      takeoff_moment_index - dif], ymin=0, ymax=max(xs),
                   colors='purple',
                   label='vline_multiple - full height')

        plt.xlabel('Time')
        plt.ylabel('Force')
        plt.legend()
        # plt.close(fig)

        fig = plt.figure()
        plt.title('Force Time Curve', fontdict={'fontweight': 'bold', 'fontsize': 12})
        plt.plot(temp_force, linestyle='-', label='Force', color=colors_seismic[2], linewidth=1)

        # defining an array
        xs = [0, 700]

        dif = jump_onset_moment_index
        # multiple lines all full height
        plt.vlines(x=[jump_onset_moment_index - dif, unloading_end_index - dif, braking_end_index - dif,
                      takeoff_moment_index - dif], ymin=-400, ymax=max(xs),
                   colors=colors_icefire[4])
        # label = 'Key Points')

        plt.xlabel('Time')
        plt.ylabel('Force')
        plt.legend()

        # plt.close(fig)

    results_dict = {'mass': mass}
    results_dict['force'] = peak_force
    results_dict['impulse'] = peak_impulse
    results_dict['jump_time'] = jump_time
    results_dict['ToV'] = ToV
    results_dict['jump_height'] = jump_height
    results_dict['peak_negative_velocity'] = peak_negative_velocity
    results_dict['rsi_mod'] = rsi_mod
    results_dict['mean_power'] = mean_power
    results_dict['peak_power'] = peak_power
    results_dict['CoM_displacement'] = CoM_displacement_value
    results_dict['limb_stiffness_norm'] = limb_stiffness_norm
    results_dict['peak_unloading_impulse'] = peak_unloading_impulse
    results_dict['peak_braking_force'] = peak_braking_force
    results_dict['relative_braking_force'] = relative_braking_force
    results_dict['peak_braking_impulse'] = peak_braking_impulse
    results_dict['relative_braking_impulse'] = relative_braking_impulse
    results_dict['force_at_zero_velocity'] = force_at_zero_velocity
    results_dict['peak_concentric_force'] = peak_concentric_force
    results_dict['relative_concentric_force'] = relative_concentric_force
    results_dict['peak_concentric_impulse'] = peak_concentric_impulse
    results_dict['relative_concentric_impulse'] = relative_concentric_impulse
    results_dict['unloading_time'] = unloading_time
    results_dict['braking_time'] = braking_time
    results_dict['concentric_time'] = concentric_time

    return results_dict


"""# cmj_sl_calc() - CMJ Single leg"""

##### single leg CMJ function

from matplotlib.legend import legend_handler
from numpy.linalg import tensorsolve


def cmj_sl_calc(trial, leg, mass):  # leg - "left", "right"
    log.f(f"**** {leg} ")
    force_leg = np.array(trial)

    # normalizing for time
    freq = 2400
    g = 9.81  # gravity
    time = np.arange(0, len(force_leg) / freq, 1 / freq)
    # log.debug(f"time: {time}")

    # Onset of Jump
    start_jump = np.where(
        (force_leg[0:] > 20) | (force_leg[0:] < -20))  # if want to use one function, need to perform mass / 2
    jump_onset_moment_index = start_jump[0][0]  # time stamps jump moment
    # log.debug(f"start_jump: {len(start_jump)} {start_jump}")
    # log.debug(f"jump_onset_moment_index: {jump_onset_moment_index}")

    # Start of the flight phase
    start_flight = np.where(force_leg[0:] < (
                np.amin(force_leg) + 10))  # need to create if statement so that left and right can be calculated
    # amin_list = np.where(force_leg[0:] == (np.amin(force_leg)))
    # amin_list_index = amin_list[0][0]
    # true_min_list = force_leg[16581:16681]
    # log.debug(f"true_min_list: {true_min_list}")
    # log.debug(f"true_min: {np.amin(true_min_list)}")
    # log.debug(f"amin: {np.amin(force_leg)}")
    # log.debug(f"amin_list_index: {amin_list_index}")
    log.debug(f"start_flight: {start_flight}")
    takeoff_moment_index = start_flight[0][0]  # time stamps takeoff moment
    # log.debug(f"takeoff_moment_index_force_{leg}: {force_leg[takeoff_moment_index]}")
    log.debug(f"INDEX takeoff_moment_index_{leg}: {takeoff_moment_index}")
    # log.debug(f"difference_in_index_{leg}: {takeoff_moment_index - jump_onset_moment_index}")

    # indexing values between jump_onset_moment_index and takoff_moment
    cmj_arr = force_leg[
              jump_onset_moment_index:takeoff_moment_index]  # indexes the force_leg from jump onset moment to takeoff

    peak_force = cmj_arr.max()
    log.debug(f"peak_force: {peak_force}")

    time_ss = time[
              jump_onset_moment_index:takeoff_moment_index]  # creates a time subset from jump onset moment to takeoff
    # log.debug(f"jump: {cmj_arr}")
    jump_time = time_ss[-1]  # total time of jump

    # ** calculating impulse **
    impulse_arr = cumtrapz(cmj_arr, x=time_ss, initial=0)  # integrates force_leg curve to produce impulse
    log.debug(f"impulse_{leg}: {impulse_arr}")

    peak_impulse = impulse_arr.max()
    log.debug(f"peak_impulse: {peak_impulse}")
    global g_single_file_debug
    if (g_single_file_debug == True):
        # plt.figure(figsize=(10,6))
        # plt.title('force and impulse', fontdict={'fontweight':'bold', 'fontsize': 12})
        # plt.plot(cmj_arr, 'g.-', linewidth=1)

        # plt.figure(figsize=(10,6))
        # plt.plot(impulse_arr, 'g.-', linewidth=1)
        pass

    # ** calculating velocity **

    delta_velocity = impulse_arr / (mass)  # change in velocity = impulse_arr / mass

    # ** Calculating SL Impulse During Specific Phases of the Jump **

    ##################################
    # Unloading Phase
    velocity_min = (np.amin(delta_velocity))
    # print(f"velocity_min: {velocity_min}")

    velocity_min_index = np.where(delta_velocity == np.amin(delta_velocity))
    velocity_min_index = velocity_min_index[0][0]
    # print(f"velocity_min_index: {velocity_min_index}")

    unloading_end_index = (jump_onset_moment_index + velocity_min_index)
    # print(f"unloading_end_index: {unloading_end_index}")
    unloading_force_arr = force_leg[jump_onset_moment_index:unloading_end_index]
    unloading_time_arr = time[jump_onset_moment_index:unloading_end_index]
    # print(f"eccentric_rfd_1_time_index: {ecc_rfd_1_time_index}")

    unloading_impulse_arr = cumtrapz(unloading_force_arr, unloading_time_arr, initial=0)
    # print(f"unloading_impulse_arr: {unloading_impulse_arr}")

    ##JT FORCE INSTEAD OF IMPULSE CHECK
    peak_unloading_force = unloading_force_arr.min()
    peak_unloading_impulse = unloading_impulse_arr.min()
    # print(f"peak_unloading_impulse: {peak_unloading_impulse}")

    ##################################
    # Braking Phase

    velocity_zero_index = np.where(delta_velocity[velocity_min_index:] > 0)
    velocity_zero_index = velocity_zero_index[0][0]
    # print(f"velocity_zero_index: {velocity_zero_index}")

    ### modified this to add all three together
    braking_end_index = (jump_onset_moment_index + velocity_min_index + velocity_zero_index)
    # print(f"INDEX braking_end_index: {braking_end_index}")
    braking_force_arr = force_leg[unloading_end_index:braking_end_index]
    # print(f"braking_force_arr: {braking_force_arr}")
    braking_time_arr = time[unloading_end_index:braking_end_index]
    # print(f"braking_time_arr: {braking_time_arr}")

    braking_impulse_arr = cumtrapz(braking_force_arr, braking_time_arr, initial=0)
    # print(f"braking_impulse_arr: {braking_impulse_arr}")

    ##JT FORCE INSTEAD OF IMPULSE CHECK
    peak_braking_force = braking_force_arr.max()
    peak_braking_impulse = braking_impulse_arr.max()
    # print(f"peak_braking_impulse_arr: {peak_braking_impulse_arr}")

    ##################################
    # Concentric Phase - Zero Point on velocity curve to max of velocity curve

    velocity_max = (np.amax(delta_velocity))
    # print(f"velocity_max: {velocity_max}")

    velocity_max_index = np.where(delta_velocity == np.amax(delta_velocity))
    velocity_max_index = velocity_max_index[0][0]
    # print(f"INDEX velocity_max_index: {velocity_max_index}")

    concentric_end_index = (jump_onset_moment_index + velocity_max_index)
    # print(f"INDEX concentric_end_index: {concentric_end_index}")
    concentric_force_arr = force_leg[braking_end_index:concentric_end_index]
    # print(f"concentric_force_arr: {concentric_force_arr}")
    concentric_time_arr = time[braking_end_index:concentric_end_index]
    # print(f"concentric_time_arr: {concentric_time_arr}")

    concentric_impulse_arr = cumtrapz(concentric_force_arr, concentric_time_arr, initial=0)
    # print(f"  concentric_impulse_arr: {concentric_impulse_arr}")

    ##JT FORCE INSTEAD OF IMPULSE CHECK
    peak_concentric_force = concentric_force_arr.max()
    peak_concentric_impulse = concentric_impulse_arr.max()
    # print(f"  peak_concentric_impulse: {peak_concentric_impulse}")

    ##################################

    results_dict = {}
    results_dict['force_' + leg] = peak_force
    results_dict['unloading_force_' + leg] = peak_unloading_force
    results_dict['braking_force_' + leg] = peak_braking_force
    results_dict['concentric_force_' + leg] = peak_concentric_force

    results_dict['impulse_' + leg] = peak_impulse
    results_dict['unloading_impulse_' + leg] = peak_unloading_impulse
    results_dict['braking_impulse_' + leg] = peak_braking_impulse
    results_dict['concentric_impulse_' + leg] = peak_concentric_impulse

    results_dict['cmj_arr'] = cmj_arr

    return results_dict


"""# DJ - process_dj_df()  dj_calc()"""


##### process a cmj dataframe, must include which leg is injured ('Right', or 'Left')

def process_dj_df(df, injured):
    log.f()
    list_right = []
    df.rename(columns={'Fz': 'Right'}, inplace=True)
    # log.debug(df['Right'])
    df['Right'] = df['Right'].abs()  # absolute value of 'Right'
    list_right = df['Right'].to_list()  # adds data to form a list
    # log.debug(list_right)

    list_left = []
    df.rename(columns={'Fz.1': 'Left'}, inplace=True)
    df['Left'] = df['Left'].abs()  # absolute value of 'Left'
    list_left = df['Left'].to_list()  # adds data to form a list
    # log.debug(list_left)

    ### NEED TO FIGURE OUT BW
    mass = 55
    m_r = 55 / 2
    m_l = 55 / 2

    force_total = [sum(i) for i in zip(list_right, list_left)]  # sums the 2 lists so that total force can be calculated
    # log.debug(force_total)

    freq = 2400  # frequency
    g = 9.81  # gravity
    h = 0.3  # I don't know

    # m_r = (np.mean(list_right[0:int(freq*2)]) / g)  #calculation of Bodyweight - R
    # m_l = (np.mean(list_left[0:int(freq*2)]) / g) #calculation of bodyweight - L
    # mass = abs(float(m_r)) + abs(float(m_l))  #calculation of bodyweight total
    ('Subject Mass  {:.3f} kg'.format(mass))
    log.debug(f"mass: {mass}")

    # normalizing for bodyweight - See slides // subtract bodyweight and make BM = 0
    force_norm = np.subtract(force_total, mass * g)
    # log.debug(f"force_norm: {force_norm}")
    # plt.figure(figsize=(10,6))
    # plt.plot(force_norm, 'b.-', linewidth=1)

    # normalizing for bodyweight - R
    force_norm_r = np.subtract(list_right, (m_r * g))

    # normalizing for bodyweight - L
    force_norm_l = np.subtract(list_left, (m_l * g))

    # plt.title('CMJ', fontdict={'fontweight':'bold', 'fontsize': 12})
    # plt.plot(force_norm_r, linestyle = '-', label = 'Right', color=colors_seismic[2], linewidth = 1)
    # plt.plot(force_norm_l, linestyle = '-', label = 'Left', color=colors_icefire[4], linewidth = 1)
    # plt.xlabel('Time')
    # plt.ylabel('Force')
    # plt.legend()

    results_dict = {}
    ##### Calling cmj calculation functions for both legs as well as left and right
    results_dict = dj_calc(force_total, mass)
    # results_dict_l = dj_sl_calc(force_norm_l, "left")
    # results_dict_r = dj_sl_calc(force_norm_r, "right")

    # log.debug(f' L: {results_dict_l} R: {results_dict_r}')
    # results_dict.update(results_dict_l)
    # results_dict.update(results_dict_r)

    # results_dict_asymmetry = asymmetry_index(results_dict, injured)
    # results_dict.update(results_dict_asymmetry)

    return results_dict


"""# DJ Calc"""

##### dj_calc() - does all calculations for a dj

from numpy.linalg import tensorsolve


def dj_calc(trial, mass):
    log.f("***** dj calc")

    force = np.array(trial)
    # log.debug(f"cmj force:{force}")
    # normalizing for time
    freq = 2400
    g = 9.81  # gravity
    time = np.arange(0, len(force) / freq, 1 / freq)
    # log.debug(f"time: {time}")

    # *****************Indexing Key Points in the Jump******************************

    # Onset of Landing
    start_land = np.where((force[0:] > 20) | (force[0:] < -20))  # if want to use one function, need to perform mass / 2
    land_onset_moment_index = start_land[0][0]  # time stamps jump moment
    log.debug(f"start_land: {start_land}, land_onset_moment_index: {land_onset_moment_index}")

    # Start of the flight phase
    start_flight = np.where(force[land_onset_moment_index:] < (np.amin(
        force[land_onset_moment_index:]) + 10))  # need to create if statement so that left and right can be calculated
    log.debug(f"min_debug: {np.amin(force[land_onset_moment_index:])}")
    log.debug(f"min: {np.amin(force)}")
    log.debug(f"start_flight: {start_flight}")
    takeoff_moment_index = land_onset_moment_index + start_flight[0][0]  # time stamps takeoff moment
    log.debug(f"takeoff_moment_index: {takeoff_moment_index}")

    dj_temp = force[land_onset_moment_index:takeoff_moment_index]  # indexes the force from jump onset moment to takeoff
    plt.title('dj_temp', fontdict={'fontweight': 'bold', 'fontsize': 12})
    plt.plot(dj_temp, linestyle='-', label='Force', color=colors_seismic[2], linewidth=1)
    plt.xlabel('Time')
    plt.ylabel('Force')
    plt.legend()

    # jump time (from start of landing until in the air)
    time_ss = time[
              land_onset_moment_index:takeoff_moment_index]  # creates a time subset from jump onset moment to takeoff
    # creates a time subset from jump onset moment to takeoff
    log.debug(f"time_ss: {time_ss}")
    jump_time = time_ss[-1] - time_ss[0]  # total time of jump
    log.debug(f"jump_time: {jump_time}")

    # ***********************Calculating Jump Height Through Impulse Momentum Relationship***********************************

    dj_index = force[
               land_onset_moment_index:takeoff_moment_index]  # indexes the force from jump onset moment to takeoff
    plt.title('dj_index', fontdict={'fontweight': 'bold', 'fontsize': 12})
    plt.plot(dj_index, linestyle='-', label='Force', color=colors_seismic[2], linewidth=1)
    plt.xlabel('Time')
    plt.ylabel('Force')
    plt.legend()

    # calculating impulse
    impulse_arr = cumtrapz(dj_index, x=time_ss, initial=0)  # integrates force curve to produce impulse
    # log.debug(f"impulse_arr: {impulse_arr}")
    # plt.figure(figsize=(10,6))
    # plt.plot(impulse_arr,'b.-', linewidth=1)

    # calculating velocity
    delta_velocity = impulse_arr / (mass)  # change in velocity = impulse_arr / mass

    # log.debug(f"delta_velocity: {delta_velocity}")
    # log.debug(f"delta_velocity_len: {len(delta_velocity)}")

    # plt.figure(figsize=(10,6))
    # plt.plot(delta_velocity,'b.-', linewidth=1)

    # calculating takeoff velocity

    peak_impulse = impulse_arr.max()
    log.debug(f"peak_impulse: {peak_impulse}")

    ToV = peak_impulse / (mass)  # takeoff velocity = impulse / mass
    log.debug(f"Takeoff Velocity: {ToV}")

    # calculating jump height
    jump_height = ((ToV) ** 2) / (2 * g)  # jump height = (takeoff velocity)**2 / (2*gravity)
    log.debug(f"jump_height: {jump_height}")

    # ***********************Calculating Jump Height Through TIA (Control)***********************************

    # Calculating time in air
    start_land = np.where(
        force[0:] == (np.amax(force)))  # need to create if statement so that left and right can be calculated
    landing_moment = start_land[0][0]
    tia_ss = time[takeoff_moment_index:landing_moment]
    tia_ss_total = tia_ss[-1] - tia_ss[0]
    # log.debug(f"tia_ss_total: {tia_ss_total}")

    # Calculating Jump Height with TIA
    jump_height_tia = .5 * g * ((tia_ss_total / 2) ** 2)
    log.debug(f"jump_height_tia: {jump_height_tia}")

    # ***********************Calculating Reactive Strength Index (Modified)***********************************

    # Calculating RSI Mod
    rsi_mod = jump_height / jump_time
    log.debug(f"rsi_mod: {rsi_mod}")

    # ***********************Calculating Power***********************************

    # calculating mean Power
    power = force[land_onset_moment_index:takeoff_moment_index] * delta_velocity  # power = force * velocity
    mean_power = np.mean(power)  # mean power = average of the power calculated over the duration of jump
    log.debug(f"average_power: {mean_power}")

    # calculating peak power
    peak_power = np.max(power)  # np.max - finds max
    log.debug(f"peak_power: {peak_power}")

    # ***********************Calculating Displacement of CoM (Version 2)***********************************

    CoM_displacement = cumtrapz(delta_velocity, x=time_ss, initial=0)

    CoM_displacement_initial = CoM_displacement[0]

    CoM_displacement_min = CoM_displacement.min()
    log.debug(f"CoM_displacement_min: {CoM_displacement_min}")

    CoM_displacement_value = CoM_displacement_initial - CoM_displacement_min

    # ***********************Calculating Impulse During Specific Phases of the Jump***********************************

    ##################################
    # Unloading Phase
    velocity_min = (np.amin(delta_velocity))
    # log.debug(f"velocity_min: {velocity_min}")

    velocity_min_index = np.where(delta_velocity == np.amin(delta_velocity))
    velocity_min_index = velocity_min_index[0][0]
    log.debug(f"velocity_min_index: {velocity_min_index}")

    unloading_end_index = (land_onset_moment_index + velocity_min_index)
    # log.debug(f"unloading_end_index: {unloading_end_index}")
    unloading_force_arr = force[land_onset_moment_index:unloading_end_index]

    unloading_time_arr = time[land_onset_moment_index:unloading_end_index]
    # log.debug(f"eccentric_rfd_1_time_index: {ecc_rfd_1_time_index}")
    unloading_impulse_arr = cumtrapz(unloading_force_arr, unloading_time_arr, initial=0)
    # log.debug(f"unloading_impulse_arr: {unloading_impulse_arr}")
    peak_unloading_impulse = unloading_impulse_arr.min()
    log.debug(f"peak_unloading_impulse: {peak_unloading_impulse}")

    ##################################
    # Braking Phase

    velocity_zero_index = np.where(delta_velocity[velocity_min_index:] > 0)
    velocity_zero_index = velocity_zero_index[0][0]
    # log.debug(f"velocity_zero_index: {velocity_zero_index}")

    ### modified this to add all three together
    braking_end_index = (land_onset_moment_index + velocity_min_index + velocity_zero_index)
    # log.debug(f"braking_end_index: {braking_end_index}")
    braking_force_arr = force[unloading_end_index:braking_end_index]
    # log.debug(f"braking_force_arr: {braking_force_arr}")
    braking_time_arr = time[unloading_end_index:braking_end_index]
    # log.debug(f"braking_time_arr: {braking_time_arr}")
    braking_impulse_arr = cumtrapz(braking_force_arr, braking_time_arr, initial=0)
    # log.debug(f"braking_impulse_arr: {braking_impulse_arr}")
    peak_braking_impulse = braking_impulse_arr.max()
    log.debug(f"peak_braking_impulse: {peak_braking_impulse}")

    ##################################
    # Concentric Phase - Zero Point on velocity curve to max of velocity curve

    velocity_max = (np.amax(delta_velocity))
    # log.debug(f"velocity_max: {velocity_max}")

    velocity_max_index = np.where(delta_velocity == np.amax(delta_velocity))
    velocity_max_index = velocity_max_index[0][0]
    # log.debug(f"velocity_max_index: {velocity_max_index}")

    concentric_end_index = (land_onset_moment_index + velocity_min_index + velocity_zero_index + velocity_max_index)
    # log.debug(f"concentric_end_index: {concentric_end_index}")
    concentric_force_arr = force[braking_end_index:concentric_end_index]
    # log.debug(f"concentric_force_arr: {concentric_force_arr}")
    concentric_time_arr = time[braking_end_index:concentric_end_index]
    # log.debug(f"concentric_time_arr: {concentric_time_arr}")

    concentric_impulse_arr = cumtrapz(concentric_force_arr, concentric_time_arr, initial=0)
    # log.debug(f"concentric_impulse_arr: {concentric_impulse_arr}")
    peak_concentric_impulse = concentric_impulse_arr.max()
    log.debug(f"peak_concentric_impulse: {peak_concentric_impulse}")

    ##################################

    results_dict = {"mass": mass}
    results_dict["impulse"] = peak_impulse
    results_dict["jump_time"] = jump_time
    results_dict["ToV"] = ToV
    results_dict["jump_height"] = jump_height
    results_dict["rsi_mod"] = rsi_mod
    results_dict["mean_power"] = mean_power
    results_dict["peak_power"] = peak_power
    results_dict["CoM_displacement"] = CoM_displacement_value
    results_dict["unloading_impulse"] = peak_unloading_impulse
    results_dict["braking_impulse"] = peak_braking_impulse
    results_dict["concentric_impulse"] = peak_concentric_impulse

    return results_dict


"""# SJ - process_sj_df() sj_calc()"""


##### process a cmj dataframe, must include which leg is injured ('Right', or 'Left')

def process_sj_df(df, injured):
    log.f()
    list_right = []
    df.rename(columns={'Fz': 'Right'}, inplace=True)
    # log.debug(df['Right'])
    df['Right'] = df['Right'].abs()  # absolute value of 'Right'
    list_right = df['Right'].to_list()  # adds data to form a list
    # log.debug(list_right)

    list_left = []
    df.rename(columns={'Fz.1': 'Left'}, inplace=True)
    df['Left'] = df['Left'].abs()  # absolute value of 'Left'
    list_left = df['Left'].to_list()  # adds data to form a list
    # log.debug(list_left)

    force_total = [sum(i) for i in zip(list_right, list_left)]  # sums the 2 lists so that total force can be calculated
    # log.debug(force_total)

    freq = 2400  # frequency
    g = 9.81  # gravity
    h = 0.3  # I don't know

    m_r = (np.mean(list_right[0:int(freq * 2)]) / g)  # calculation of Bodyweight - R
    m_l = (np.mean(list_left[0:int(freq * 2)]) / g)  # calculation of bodyweight - L
    mass = abs(float(m_r)) + abs(float(m_l))  # calculation of bodyweight total
    ('Subject Mass  {:.3f} kg'.format(mass))
    log.debug(f"mass: {mass}")

    # normalizing for bodyweight - See slides // subtract bodyweight and make BM = 0
    force_norm = np.subtract(force_total, mass * g)
    log.debug(f"force_norm: {force_norm}")
    # plt.figure(figsize=(10,6))
    # plt.plot(force_norm, 'b.-', linewidth=1)

    # normalizing for bodyweight - R
    force_norm_r = np.subtract(list_right, (m_r * g))
    log.debug(f"force_r: {force_norm_r}")
    # plt.figure(figsize=(10,6))
    # plt.plot(force_norm_r, 'b.-', linewidth=1)

    # normalizing for bodyweight - L
    force_norm_l = np.subtract(list_left, (m_l * g))
    log.debug(f"force_l: {force_norm_l}")
    # plt.figure(figsize=(10,6))
    # plt.plot(force_norm_r,'g.-', linewidth=1)

    plt.title('SJ', fontdict={'fontweight': 'bold', 'fontsize': 12})
    plt.plot(force_norm_r, linestyle='-', label='Right', color=colors_seismic[2], linewidth=1)
    plt.plot(force_norm_l, linestyle='-', label='Left', color=colors_icefire[4], linewidth=1)
    plt.xlabel('Time')
    plt.ylabel('Force')
    plt.legend()

    ##### Calling cmj calculation functions for both legs as well as left and right
    results_dict = {}
    results_dict = sj_calc(force_norm, mass)
    results_dict_l = sj_sl_calc(force_norm_l, "left")
    results_dict_r = sj_sl_calc(force_norm_r, "right")

    # # log.debug(f' L: {results_dict_l} R: {results_dict_r}')
    results_dict.update(results_dict_l)
    results_dict.update(results_dict_r)

    r = asym_index(results_dict['impulse_right'], results_dict['impulse_left'], injured, 'asymmetry_index')
    results_dict.update(r)

    return results_dict


##### sj_calc() - does all calculations for a cmj

from numpy.linalg import tensorsolve


def sj_calc(trial, mass):
    log.f("***** CMJ calc")

    force = np.array(trial)
    log.debug(f"cmj force:{force}")
    # normalizing for time
    freq = 2400
    g = 9.81  # gravity
    time = np.arange(0, len(force) / freq, 1 / freq)
    # log.debug(f"time: {time}")

    # *****************Indexing Key Points in the Jump******************************

    # Onset of Jump
    start_jump = np.where((force[0:] > 50) | (force[0:] < -50))  # if want to use one function, need to perform mass / 2
    jump_onset_moment_index = start_jump[0][0]  # time stamps jump moment
    log.debug(f"start_jump: {start_jump}, jump_onset_moment_index: {jump_onset_moment_index}")

    # Start of the flight phase
    start_flight = np.where(
        force[0:] < (np.amin(force) + 10))  # need to create if statement so that left and right can be calculated
    # log.debug(f"min: {np.amin(force)}")
    # log.debug(f"start_flight: {start_flight}")
    takeoff_moment_index = start_flight[0][0]  # time stamps takeoff moment
    log.debug(f"takeoff_moment_index: {takeoff_moment_index}")

    # jump time (from start of jump until in the air)
    time_ss = time[
              jump_onset_moment_index:takeoff_moment_index]  # creates a time subset from jump onset moment to takeoff
    # log.debug(f"time_ss: {time_ss}")
    jump_time = time_ss[-1] - time_ss[0]  # total time of jump
    # log.debug(f"jump_time: {jump_time}")

    # ***********************Calculating Jump Height Through Impulse Momentum Relationship***********************************

    sj_index = force[
               jump_onset_moment_index:takeoff_moment_index]  # indexes the force from jump onset moment to takeoff

    # calculating impulse
    impulse_arr = cumtrapz(sj_index, x=time_ss, initial=0)  # integrates force curve to produce impulse
    # log.debug(f"impulse_arr: {impulse_arr}")
    # plt.figure(figsize=(10,6))
    # plt.plot(impulse_arr,'b.-', linewidth=1)

    # calculating velocity
    delta_velocity = impulse_arr / (mass)  # change in velocity = impulse_arr / mass

    # log.debug(f"delta_velocity: {delta_velocity}")
    # log.debug(f"delta_velocity_len: {len(delta_velocity)}")

    # plt.figure(figsize=(10,6))
    # plt.plot(delta_velocity,'b.-', linewidth=1)

    # calculating takeoff velocity

    peak_impulse = impulse_arr.max()
    log.debug(f"peak_impulse: {peak_impulse}")

    ToV = peak_impulse / (mass)  # takeoff velocity = impulse_arr / mass
    log.debug(f"Takeoff Velocity: {ToV}")

    # calculating jump height
    jump_height = ((ToV) ** 2) / (2 * g)  # jump height = (takeoff velocity)**2 / (2*gravity)
    log.debug(f"jump_height: {jump_height}")

    # ***********************Calculating Jump Height Through TIA (Control)***********************************

    # Calculating time in air
    start_land = np.where(
        force[0:] == (np.amax(force)))  # need to create if statement so that left and right can be calculated
    landing_moment = start_land[0][0]
    tia_ss = time[takeoff_moment_index:landing_moment]
    tia_ss_total = tia_ss[-1] - tia_ss[0]
    # log.debug(f"tia_ss_total: {tia_ss_total}")

    # Calculating Jump Height with TIA
    jump_height_tia = .5 * g * ((tia_ss_total / 2) ** 2)
    log.debug(f"jump_height_tia: {jump_height_tia}")

    # ***********************Calculating Reactive Strength Index (Modified)***********************************

    # Calculating RSI Mod
    rsi_mod = jump_height / jump_time
    log.debug(f"rsi_mod: {rsi_mod}")

    # ***********************Calculating Power***********************************

    # calculating mean Power
    power = force[jump_onset_moment_index:takeoff_moment_index] * delta_velocity  # power = force * velocity
    mean_power = np.mean(power)  # mean power = average of the power calculated over the duration of jump
    log.debug(f"average_power: {mean_power}")

    # calculating peak power
    peak_power = np.max(power)  # np.max - finds max
    log.debug(f"peak_power: {peak_power}")

    results_dict = {"mass": mass}
    results_dict["impulse"] = peak_impulse
    results_dict["jump_time"] = jump_time
    results_dict["ToV"] = ToV
    results_dict["jump_height"] = jump_height
    results_dict["rsi_mod"] = rsi_mod
    results_dict["mean_power"] = mean_power
    results_dict["peak_power"] = peak_power

    return results_dict


##### single leg SJ function

from matplotlib.legend import legend_handler
from numpy.linalg import tensorsolve


def sj_sl_calc(trial, leg):  # leg - "left", "right"
    log.f(f"**** {leg} ")
    force_leg = np.array(trial)

    # normalizing for time
    freq = 2400
    g = 9.81  # gravity
    time = np.arange(0, len(force_leg) / freq, 1 / freq)
    # log.debug(f"time: {time}")

    # Onset of Jump
    start_jump = np.where(
        (force_leg[0:] > 50) | (force_leg[0:] < -50))  # if want to use one function, need to perform mass / 2
    jump_onset_moment_index = start_jump[0][0]  # time stamps jump moment
    # log.debug(f"start_jump: {len(start_jump)} {start_jump}")
    # log.debug(f"jump_onset_moment_index: {jump_onset_moment_index}")

    # Start of the flight phase
    start_flight = np.where(force_leg[0:] < (
                np.amin(force_leg) + 10))  # need to create if statement so that left and right can be calculated
    # amin_list = np.where(force_leg[0:] == (np.amin(force_leg)))
    # amin_list_index = amin_list[0][0]
    # true_min_list = force_leg[16581:16681]
    # log.debug(f"true_min_list: {true_min_list}")
    # log.debug(f"true_min: {np.amin(true_min_list)}")
    # log.debug(f"amin: {np.amin(force_leg)}")
    # log.debug(f"amin_list_index: {amin_list_index}")
    log.debug(f"start_flight: {start_flight}")
    takeoff_moment_index = start_flight[0][0]  # time stamps takeoff moment
    # log.debug(f"takeoff_moment_index_force_{leg}: {force_leg[takeoff_moment_index]}")
    log.debug(f"takeoff_moment_index_{leg}: {takeoff_moment_index}")
    # log.debug(f"difference_in_index_{leg}: {takeoff_moment_index - jump_onset_moment_index}")

    # indexing values between jump_onset_moment_index and takoff_moment
    sj_index = force_leg[
               jump_onset_moment_index:takeoff_moment_index]  # indexes the force_leg from jump onset moment to takeoff
    # plt.figure(figsize=(10,6))
    # plt.plot(cmj_arr, 'g.-', linewidth=1)

    time_ss = time[
              jump_onset_moment_index:takeoff_moment_index]  # creates a time subset from jump onset moment to takeoff
    # log.debug(f"jump: {cmj_arr}")
    jump_time = time_ss[-1]  # total time of jump

    # calculating impulse
    impulse_arr = cumtrapz(sj_index, x=time_ss, initial=0)  # integrates force_leg curve to produce impulse
    log.debug(f"impulse_{leg}: {impulse_arr}")
    # plt.figure(figsize=(10,6))
    # plt.plot(impulse_arr, 'g.-', linewidth=1)
    peak_impulse = impulse_arr.max()
    log.debug(f"peak_impulse: {peak_impulse}")

    results_dict = {}
    results_dict["impulse_" + leg] = peak_impulse

    return results_dict


"""# Asymmetry Index

"""


##### Calculate Asymmetry Index - Calculated as percentage

def asym_index(i_r, i_l, injured, col_name):
    if injured == "right":
        injured_leg = i_r
        non_injured_leg = i_l
    else:
        injured_leg = i_l
        non_injured_leg = i_r

    total_impulse = i_r + i_l

    asymmetry_index = ((non_injured_leg - injured_leg) / total_impulse) * 100
    log.debug(f"{col_name}: {asymmetry_index}")

    results_dict = {}
    results_dict[col_name] = asymmetry_index

    return results_dict


"""#SL ISO Knee Extension Testing"""


##### process a cmj dataframe, must include which leg is injured ('Right', or 'Left')

def process_iso_knee_ext(df):
    # set moment arm in meters
    moment_arm = .4
    # set knee angle (degrees)
    knee_angle_deg = 60
    # convert knee angle (degrees) to radians
    knee_angle_rad = math.radians(knee_angle_deg)
    print(f"knee_angle_rad: {knee_angle_rad}")
    # calculating sin(knee_angle_rad)
    sin_theta = (math.sin(knee_angle_rad))
    print(f"sin_theta: {sin_theta}")
    # test frequency
    freq = 80

    #print(df)

    # determining leg
    leg = df.loc[0, 'leg']
    #print(f"leg: {leg}")

    # rename columns so they are easier to deal with AND does abvolute value columns
    force = []
    force = df['force_N'].to_list()  # adds data to form a list
    # print(f"force: {force}")

    # getting time column from df
    elapsed_time = []
    elapsed_time = df['elapsed_time_sec'].to_list()

    torque = np.multiply(force, moment_arm * sin_theta)
    # print(f"torque: {torque}")

    # print(f"list_torque: {list_torque}")

    # create graph and have it stored permanently to file
    fig = plt.figure()
    title = ' Iso Knee Extension'
    plt.title(title, fontdict={'fontweight': 'bold', 'fontsize': 12})
    plt.plot(torque, linestyle='-', label='Left', color=colors_seismic[2], linewidth=1)
    plt.xlabel('Time')
    plt.ylabel('Torque(Nm)')
    plt.legend()
    plt.show()

    results_dict = iso_knee_ext_calc(torque, elapsed_time, start_torque_average, leg)

    return results_dict


def iso_knee_ext_calc(torque, elapsed_time, leg):  # leg - "left", "right"

    print(f"***** ISO Knee Ext")

    # torque = np.array(trial)
    # print(f"torque:{torque}")

    # normalizing for time
    freq = 80
    time = np.arange(0, len(torque) / freq, 1 / freq)
    # log.debug(f"time: {time}")

    # *****************Indexing Key Points in the Contraction******************************

    # Indexing Onset of Contraction
    start_iso = np.where((torque[0:] > .25))
    onset_moment_index = start_iso[0][0]  # time stamps jump moment
    # print(f"start_iso: {start_iso}, onset_moment_index: {onset_moment_index}")

    # Indexing peak torque and calculating peak torque
    peak_torque = torque.max()
    print(f"peak_torque: {peak_torque}")
    # Indexing peak torque moment
    peak_torque_index = np.where(torque == np.amax(torque))
    peak_torque_index = peak_torque_index[0][0]
    print(f"peak_torque_index: {peak_torque_index}")

    # Creating torque array (from onset to peak)
    torque_arr = torque[onset_moment_index:peak_torque_index]
    # Creating torque time array (from onset to peak)
    torque_time_arr = time[onset_moment_index:peak_torque_index]
    # print(f"torque_time_arr: {torque_time_arr}")
    # Calculating time to peak torque
    time_to_peak_torque = torque_time_arr[-1]
    print(f"time_to_peak_torque: {time_to_peak_torque}")
    # Calculating peak force impulse
    peak_torque_impulse_arr = cumtrapz(torque_arr, x=torque_time_arr, initial=0)
    # print(f"peak_torque_impulse_arr: {peak_torque_impulse_arr}")
    # calculating peak impulse
    peak_torque_impulse = peak_torque_impulse_arr.max()
    print(f"peak_torque_impulse: {peak_torque_impulse}")

    # Indexing Early RFD < 100ms
    i = onset_moment_index
    while i < len(elapsed_time):
        if elapsed_time[i] > .1 + elapsed_time[onset_moment_index]:
            break
        i += 1

    early_rfd_index = i

    # calculating early rfd torque from early rfd_index
    early_rfd_torque = torque[early_rfd_index]
    print(f"early_rfd_torque: {early_rfd_torque}")
    # creating early rfd torque array
    early_rfd_torque_arr = torque[onset_moment_index:early_rfd_index]
    print(f"early_rfd_torque_arr: {early_rfd_torque_arr}")
    # creating early rfd time array
    early_rfd_time_arr = time[onset_moment_index:early_rfd_index]
    print(f"early_rfd_time_arr: {early_rfd_time_arr}")
    # calcuting early rfd impulse using cumtrapz
    early_rfd_impulse_arr = cumtrapz(early_rfd_torque_arr, x=early_rfd_time_arr, initial=0)
    print(f"early_rfd_impulse_arr: {early_rfd_impulse_arr}")
    # calculating impulse using .max()
    peak_early_rfd_impulse = early_rfd_impulse_arr.max()
    print(f"peak_early_rfd_impulse: {peak_early_rfd_impulse}")

    # Indexing Early RFD < 100ms

    while i < len(elapsed_time):
        if elapsed_time[i] > .2 + elapsed_time[onset_moment_index]:
            break
        i += 1

    late_rfd_index = i

    # calculating late rfd torque from late_rfd_index
    late_rfd_torque = torque[late_rfd_index]
    print(f"late_rfd_torque: {late_rfd_torque}")
    # creating late rfd torque array
    late_rfd_torque_arr = torque[onset_moment_index:late_rfd_index]
    print(f"late_rfd_torque_arr: {late_rfd_torque_arr}")
    # creating late rfd time array
    late_rfd_time_arr = time[onset_moment_index:late_rfd_index]
    print(f"late_rfd_time_arr: {late_rfd_time_arr}")
    # calculating late rfd impulse using cumtrapz
    late_rfd_impulse_arr = cumtrapz(late_rfd_torque_arr, x=late_rfd_time_arr, initial=0)
    print(f"late_rfd_impulse_arr: {late_rfd_impulse_arr}")
    # calculating late rfd impulse using .max()
    peak_late_rfd_impulse = late_rfd_impulse_arr.max()
    print(f"peak_late_rfd_impulse: {peak_late_rfd_impulse}")

    peak_torque_slope_values = np.polyfit(torque_time_arr, torque_arr, 1)
    print(f"peak_torque_slope_values: {peak_torque_slope_values}")
    peak_torque_slope = peak_torque_slope_values[0]
    print(f"peak_torque_slope: {peak_torque_slope}")

    fig = plt.figure()
    plt.title('Debug Graph', fontdict={'fontweight': 'bold', 'fontsize': 12})
    plt.plot(torque, linestyle='-', label='Torque', color=colors_seismic[2], linewidth=1)

    # defining an array
    xs = [0, peak_torque]

    dif = onset_moment_index
    # multiple lines all full height
    plt.vlines(x=[onset_moment_index, early_rfd_index, late_rfd_index, peak_torque_index], ymin=0, ymax=max(xs),
               colors='purple',
               label='vline_multiple - full height')

    plt.xlabel('Time')
    plt.ylabel('Torque')
    plt.legend()
    plt.show(fig)

    results_dict = {}
    results_dict['peak_torque_' + leg] = peak_torque
    results_dict['peak_torque_impulse_' + leg] = peak_torque_impulse
    results_dict['peak_torque_slope_' + leg] = peak_torque_slope
    results_dict['time_to_peak_torque_' + leg] = time_to_peak_torque

    results_dict['early_rfd_torque_' + leg] = early_rfd_torque
    results_dict['early_rfd_impulse_' + leg] = peak_early_rfd_impulse
    results_dict['late_rfd_torque_' + leg] = late_rfd_torque
    results_dict['late_rfd_impulse_' + leg] = peak_late_rfd_impulse

    return results_dict


"""#Main"""

# log.set_logging_level("WARNING")

# main(True)
# log.set_logging_level("DEBUG")
# main_single_file('Ben Ford/sj_01.csv')
# main_single_file('Sophia Avalos/cmj_03 (3).csv')

# failing files
# log.set_logging_level("DEBUG")
# main_single_file('Sophia Avalos/cmj_02.csv') # failing to run
# main("Sophia Avalos/sl_r_03.csv")
# main("Sophia Avalos/sl_l_03.csv")

# Debug timestamp for files

# log.set_logging_level("WARNING")
#log.set_logging_level("DEBUG")

main()

# log.set_logging_level("INFO")
# main_single_file('Jade Warren/JTSextR_Jade Warren_20230630_182746.csv')
# main_single_file('Sophia Avalos/cmj_04.csv')
# main_single_file('Sophia Avalos/cmj_05 (1)(1).csv')
