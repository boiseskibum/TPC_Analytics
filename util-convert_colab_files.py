# connecting google drive

# Import necessary modules
import os
import platform
import glob
import shutil
import sys
import time
import datetime
from datetime import timezone
from dateutil import parser
import pytz   # used for timezones

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pickle import FALSE

from scipy import signal
from scipy.integrate import cumtrapz
from scipy.signal import argrelextrema, find_peaks

np.set_printoptions(threshold=False)

######################################################################

#set base and application path
path_base = '/gdrive/MyDrive/Force Plate Testing/'   # code for Jake

path_base = '/gdrive/MyDrive/JTdata/'   # Steve's test configuration

path_base = 'C:/Users/Steve/My Drive/JTdata/'   # Windows test config

# steve_path ='C:/Users/Steve/My Drive'
# print(f'steve path: {os.listdir(steve_path)}')

path_data = path_base + 'data/'
path_new_TPC = path_base + 'new_TPC/'
print(f"path_base = {path_base}")
print(f'path_data: {path_data}')
print(f'path_new_TPC: {path_new_TPC}')

###############################################################################
# Main() - Process all athletes and files
#

def main():
  # setup path variables for base and misc

  objects = os.listdir(path_data)

#  print(objects)

  # List directories contained in path_data
  athletes = [d for d in os.listdir(path_data) if os.path.isdir(os.path.join(path_data, d))]
  print(f'Athletes: {athletes}')

  for athlete in athletes:
    print(f'#### converting: {athlete}')
    convert_athlete_files(athlete, path_data + athlete + '/', path_new_TPC)



###############################################################################
# Main() - Process all athletes and files
def main():
  # setup path variables for base and misc
  path_data = path_base + 'data/'
  path_new_TPC = path_base + 'new_TPC/'

  print(f'path_data: {path_data}')
  print(f'path_new_TPC: {path_new_TPC}')

  objects = os.listdir(path_data)

  print(objects)

  # List directories contained in path_data
  athletes = [d for d in os.listdir(path_data) if os.path.isdir(os.path.join(path_data, d))]
  print(f'Athletes: {athletes}')

  for athlete in athletes:
    print(f'#### converting: {athlete}')
    convert_athlete_files(athlete, path_data + athlete + '/', path_new_TPC)

def convert_athlete_files(athlete, athlete_path, new_path):

    prefix = 'cmj_'
    extension = '.csv'
    file_list = []
    j=0
    # gets files from data directory and appends them to file_list
    f = os.listdir(athlete_path)
    print(f'List of files in: {athlete_path}:  Number of files: {len(f)}')
#    print(f'    Here: {f}')
    for filename in f:
      # validates the extension, the prefix, and that it is file (instead of directory)
      if filename.endswith(extension) and filename.startswith(prefix):
        if '--' not in filename:
          j+=1

          file_path = athlete_path + filename
          # get creation time from filename
          creation_time = os.path.getctime(file_path)
          modification_time = os.path.getmtime(file_path)
          # turn creation time & modification time into datetime obj
          creation_time_obj = datetime.datetime.fromtimestamp(creation_time)
          modification_time_obj = datetime.datetime.fromtimestamp(modification_time)

          # figure out if creation time is actually newer than modification time and if
          # so then change creation time to the older time (modification).  It is a hack
          # but it works
          if creation_time_obj > modification_time_obj:
            datetime_obj_use = modification_time_obj
          else:
            datetime_obj_use = creation_time_obj

          # turn datetime obj to str
          datetime_str = datetime_obj_use.strftime('%Y-%m-%d_%H-%M-%S')

          new_filename = f'JTDcmj_{athlete}_' + datetime_str + extension

          # read in the filename
          df = pd.read_csv(file_path, skiprows=[1, 2, 4], header=1)
          start_rows = len(df)
#          print(df.iloc[0])   # prints out first row of data
#          print(df.head(1))

          # codeo to validate and fix the files before moving the to TPC format
          dl = validate_file(df)
          df = fix_cmj_zero_row(df, dl)
          final_rows = len(df)

          if (start_rows == final_rows):
            #print(f'rows of data: {final_rows}')
            pass
          else:
            print(f'FIXED DATA: start_rows: {start_rows} end_rows: {final_rows}, fixed: {start_rows - final_rows}')

          #create a elapsed_time_sec columns
          freq = 2400       #frequency in measurements per second
          df['elapsed_time_sec'] = df.index/freq
          elapsed_time = df['elapsed_time_sec'].iloc[-1]
#          print(f'elapsed_time: {elapsed_time}')
#          print(f'columns: {df.columns.tolist()}')


          # create new columns with the names TPC names:
          # rename columns with TPC AND does absolute value columns
          df['r_force_N'] = df['Right'].abs()        #absolute value of 'Right'
          df['l_force_N'] = df['Left'].abs()      #absolute value of 'Left'

          r_max = df['r_force_N'].max()
          l_max = df['l_force_N'].max()

          new_file_path = new_path + athlete + '/' + new_filename
          try:
            # Check if the directory exists, and if not, create it
            directory = os.path.dirname(new_file_path)
            if not os.path.exists(directory):
              os.makedirs(directory)
            df.to_csv(new_file_path, index=False)
          except:
            print(f'failed to save file!!!!!!!!!')
            return

          print(f'new_file: {new_file_path}')
          print(f'     len: {len(df)} Elapsed: {elapsed_time:.2f} l_max: {l_max} r_max: {r_max}')

          # if j > 1:
          #   return

    print(f'Number of Files converted: {j}')
    return




################################################################################################################
#### validate a specific dataframe (from file)
# - returns a list of dictionaries where zero rows occured (dictionary has start, end, and left or right)

def validate_file(df):
  df.rename(columns={'Fz': 'Right'}, inplace=True)
  df.rename(columns={'Fz.1': 'Left'}, inplace=True)

  # log.debug( "VALIDATION 1 - count zero values and left and right for comparison")

  # validation 1 - count zero values in left and right
  zero_counter_right = df['Right'].value_counts()[0]
  # log.debug( ic.format(zero_counter_right))
  zero_counter_left = df['Left'].value_counts()[0]
  # log.debug( ic.format(zero_counter_left))
  percent_dif = (zero_counter_right - zero_counter_left)/zero_counter_right * 100
  # log.debug( ic.format(percent_dif))

  zero_row_list = []

  #Validation 2 - count number of unexpected zero rows
  #Right Leg
  rc = 0
  rzc = 0
  lzc = 0
  ignore_zero = False
  df = df.reset_index()  # make sure indexes pair with number of rows

  for index, row in df.iterrows():

    #right side
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

    #left side
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

  #new_zero_row_list = []

  for my_dict in zero_row_list:
    sr = my_dict['start_row']
    er = my_dict['end_row']
    leg = my_dict['leg']
    #new_value = df.iloc[sr - 1][leg]
    i = sr
    # Interpolation Calculations
    nr = er - sr
    delta = (df.at[er, leg] - df.at[sr - 1, leg]) / (nr + 1)
    #log.debug(f'nr: {nr}')
    #log.debug(f'delta: {delta}')
    j = 1
    while i < er:
      new_value = ((delta)*j) + df.at[sr - 1, leg]
      #log.debug(f'    new_value: {new_value}')
      j += 1
      df.at[i, leg] = new_value
      i += 1

  return df


main()