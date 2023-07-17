
import sys
sys.path.append('../share')

import math
import numpy as np
from scipy.integrate import cumtrapz

import matplotlib.pyplot as plt
import seaborn as sns
# Importing Colors
colors_blue = sns.color_palette('Blues', 10)
colors_grey = sns.color_palette('Greys', 10)
colors = sns.color_palette('rocket', 10)
colors_icefire = sns.color_palette('icefire', 10)
colors3 = sns.color_palette('rainbow', 5)
colors_seismic = sns.color_palette('seismic', 10)

import jt_util as util

log = util.jt_logging()
log.set_logging_level("WARNING")   # this will show errors but not files actually processed

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

    print(df)

    # determining leg
    leg = df.loc[0, 'leg']
    print(f"leg: {leg}")

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