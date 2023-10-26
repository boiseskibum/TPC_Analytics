# Import necessary modules
import os, platform, glob, shutil
import sys, time, datetime
from datetime import datetime
from datetime import timezone
from dateutil import parser

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pickle import FALSE

from scipy import signal
from scipy.integrate import cumtrapz
from scipy.signal import argrelextrema, find_peaks

try:
    from . import jt_util as util
    from . import jt_protocol as jtp
    from . import jt_athletes as jta
except:
    import jt_util as util
    import jt_protocol as jtp
    import jt_athletes as jta


# Importing Colors
colors_blue = sns.color_palette('Blues', 10)
colors_grey = sns.color_palette('Greys', 10)
colors = sns.color_palette('rocket', 10)
colors_icefire = sns.color_palette('icefire', 10)
colors3 = sns.color_palette('rainbow', 5)
colors_seismic = sns.color_palette('seismic', 10)
colors_PuBu = sns.color_palette('PuBu', 10)
colors_GnBu = sns.color_palette('GnBu', 10)


from numpy.ma.extras import median


class JT_graphs_knee_extension_iso:
    def __init__(self, config_obj ):
        self.config_obj = config_obj
        self.my_summary_path = self.config_obj.path_db + 'JTSext_data.csv'
        self.df = pd.read_csv(self.my_summary_path)

        # add date time stamp column
        self.df["datetime_object"] = self.df["col_timestamp_str"].apply(parser.parse)  # this call the function parse.parse() for each row passing in col_timestamp_str

        athlete_list = self.df.athlete_name.unique()
        # print(f"athlete_list {athlete_list}")

        # set up colors to make easier
        jt_color1 = colors_GnBu[7]
        jt_color2 = colors_grey[3]

        for athlete in athlete_list:
            # print(f"athlete {athlete}")

            athlete_filter = self.df[self.df['athlete_name'] == athlete]
            # print(f"athlete_filter {athlete_filter}")

            # get injured leg from athletes.csv
            injured = get_athlete_injury(athlete)

            # Filter the dataframe by "leg" and create two new dataframes "self.df_right" and "self.df_left"
            self.df_right = self.df[athlete_filter["leg"] == "right"].copy()
            # Reset Index for self.df_right
            self.df_right.reset_index(drop=True, inplace=True)
            # print(f"self.df_right {self.df_right}")
            self.df_left = self.df[athlete_filter["leg"] == "left"].copy()
            # Reset Index for self.df_left
            self.df_left.reset_index(drop=True, inplace=True)

            # Add a new 'Trial' column using apply() and f-string formatting
            self.df_right['trial'] = self.df_right.apply(lambda row: f'T-{row.name + 1}', axis=1)

            # print(self.df_right)

            self.df_right['combine'] = self.df_right['leg'] + " " + self.df_right['trial']

            # Select rows for a specific date (e.g., '2023-07-15')
            # selected_date = '2023-07-15'
            # selected_rows_R = self.df_right[self.df_right['date'] == selected_date]

            # Step 1: Convert 'Date' column to pandas' datetime objects
            self.df_right['date'] = pd.to_datetime(self.df_right['col_timestamp_str'])

            # Step 2: Find the latest date
            latest_date = self.df_right['date'].max()

            # # Step 3: Use boolean indexing to filter rows with the latest date
            latest_rows_r = self.df_right[self.df_right['date'].dt.date == latest_date.date()]
            # print("latest rows r")
            # print(latest_rows_r)

            # Calculate the mean of latest_rows_r
            latest_rows_r_mean = latest_rows_r.mean(numeric_only=True)
            # print(f'latest_rows_r_mean {latest_rows_r_mean}')
            # Calculate the median of latest_rows_r
            latest_rows_r_median = latest_rows_r.median(numeric_only=True)
            # print(f'latest_rows_r_median {latest_rows_r_median}')
            # Calculate the max of latest_rows_r
            latest_rows_r_max = latest_rows_r.max(numeric_only=True)
            # print(f'latest_rows_r_max {latest_rows_r_max}')
            # Calculate the standard deviation of latest_rows_r
            latest_rows_r_std = latest_rows_r.std(numeric_only=True)
            # print(f'latest_rows_r_std {latest_rows_r_std}')

            ########################################################

            # Add a new 'Trial' column using apply() and f-string formatting
            self.df_left['trial'] = self.df_left.apply(lambda row: f'T-{row.name + 1}', axis=1)

            # print(self.df_left)

            self.df_left['combine'] = self.df_left['leg'] + " " + self.df_left['trial']

            # Step 1: Convert 'Date' column to pandas' datetime objects
            self.df_left['date'] = pd.to_datetime(self.df_left['col_timestamp_str'])

            # Step 2: Find the latest date
            latest_date = self.df_left['date'].max()

            # Step 3: Use boolean indexing to filter rows with the latest date
            latest_rows_l = self.df_left[self.df_left['date'].dt.date == latest_date.date()]
            # print("latest rows L")
            # print(latest_rows_l)

            # Calculate the mean of latest_rows_r
            latest_rows_l_mean = latest_rows_l.mean(numeric_only=True)
            # print(f'latest_rows_l_mean {latest_rows_l_mean}')
            # Calculate the median of latest_rows_r
            latest_rows_l_median = latest_rows_l.median(numeric_only=True)
            # print(f'latest_rows_l_median {latest_rows_l_median}')
            # Calculate the max of latest_rows_r
            latest_rows_l_max = latest_rows_l.max(numeric_only=True)
            # print(f'latest_rows_l_max {latest_rows_l_max}')
            # Calculate the standard deviation of latest_rows_r
            latest_rows_l_std = latest_rows_l.std(numeric_only=True)
            # print(f'latest_rows_l_std {latest_rows_l_std}')

            selected_rows = pd.concat([latest_rows_r, latest_rows_l])

            # Sort values by the 'Category' column
            selected_rows = selected_rows.sort_values(by='trial')

            # print(selected_rows)

            grouped_df = selected_rows.groupby('leg')['peak_torque'].apply(list)
            # print(grouped_df)

            peak_asymmetry_index = asym_index(latest_rows_r_max, latest_rows_l_max, injured)

            #############################
            # Create the bar chart

            plt.figure(figsize=(3, 5))
            bar_width = .4
            plt.bar(df_left['leg'], latest_rows_l_mean['peak_torque'], yerr=latest_rows_l_std['peak_torque'], capsize=5,
                    color=jt_color2, width=bar_width, label='Left')
            plt.bar(df_right['leg'], latest_rows_r_mean['peak_torque'], yerr=latest_rows_r_std['peak_torque'], capsize=5,
                    color=jt_color1, width=bar_width, label='Right')

            # Set chart title and axis labels

            plt.title(f'Peak Torque Comparison {latest_date}')
            plt.xlabel('Leg')
            plt.ylabel('Peak Torque')

            # Add data values above each bar

            # Show the chart
            plt.show()

            # Plot the box plot using matplotlib
            plt.figure(figsize=(8, 6))
            plt.boxplot(grouped_df, labels=grouped_df.keys())
            plt.title('Box Plot for left and right')
            plt.xlabel('Category')
            plt.ylabel('Value')
            plt.show()


##### Calculate Asymmetry Index - Calculated as percentage

def asym_index(i_r, i_l, injured):
    if injured == "right":
        injured_leg = i_r
        non_injured_leg = i_l
    else:
        injured_leg = i_l
        non_injured_leg = i_r

    total_impulse = i_r + i_l

    asymmetry_index = ((non_injured_leg - injured_leg) / total_impulse) * 100

    return asymmetry_index
