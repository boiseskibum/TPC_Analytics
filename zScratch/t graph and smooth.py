import os
import platform
import glob
import shutil
import sys
import time
import datetime
from datetime import datetime
from datetime import timezone
from dateutil import parser
import pytz   # used for timezones
import matplotlib.gridspec as gridspec
from dateutil import parser
#!pip install fpdf2
# from fpdf import FPDF
# from fpdf.enums import XPos, YPos
from datetime import date


import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import json


# get which set of test data to look at
test_data_filename = "test_output_2023-05-15_20-58-43.txt"
test_data = 0
file_list = glob.glob("test_output*.txt")
print(file_list)
file = file_list[test_data]

for file in file_list:
    data = []
    try:
        with open(file, "r") as my_file:
            for line in my_file:
                line = line.strip()  # Remove leading/trailing whitespace, including newlines

                # Process the line here
                line = line.replace("'", "\"")
                json_data = json.loads(line)

                data.append(json_data)
                #print(f"{len(data)}  {line}")  # Or do something else with the line
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except IOError:
        print("Error reading the file.")

    my_file.close()

    # print(f" number line: {len(data)} ")  # Or do something else with the line

    # Create a pandas DataFrame from the data
    df = pd.DataFrame(data)
    if len(df) < 1:
        print(f"NO rows in dataframe for file: {file}")
    else:
        df['lbs'] = df['s1'] * (-1 / 6666)
        df['moving_average'] = df['lbs'].rolling(window=5).mean()

        plt.figure()
        plt.title(file, fontdict={'fontweight': 'bold', 'fontsize': 12})
        #plt.plot(df['left'], 'b.-', linewidth=1)
        plt.plot(df['lbs'], 'b.-', linewidth=1)
        #plt.plot(df['moving_average'], 'b.-', linewidth=1)
