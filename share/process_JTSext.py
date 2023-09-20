import math
import numpy as np
import pandas as pd

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

try:
    from . import jt_util as util
except ImportError:
    import jt_util as util


log = util.jt_logging()
log.set_logging_level("WARNING")  # this will show errors but not files actually processed

"""#SL ISO Knee Extension Testing"""


class JTSext:

    def __init__(self, trial, path_athlete_graph=None):
        self.df = None
        self.trial = trial
        self.injured = trial.injured
        self.shank_length = trial.shank_length
        self.athlete = trial.athlete
        self.path_athlete_graph = path_athlete_graph
        self.debug_graphs = False
        self.error = False
        self.error_msg = ""

    def process(self):
        
        # read in the data
        try:
            self.df = pd.read_csv(self.trial.file_path)
        except:
            self.error = True
            self.error_msg = f"process, file does not exist: {self.file_path}"
            log.critical(self.error_msg)
            return

        self.elapsed_time = self.df['elapsed_time_sec'].to_list()

        # set moment arm in meters
        # shank_length = moment_arm
        # set knee angle (degrees)
        knee_angle_deg = 60
        # convert knee angle (degrees) to radians
        knee_angle_rad = math.radians(knee_angle_deg)
        log.debug(f"knee_angle_rad: {knee_angle_rad}")
        # calculating sin(knee_angle_rad)
        sin_theta = (math.sin(knee_angle_rad))
        log.debug(f"sin_theta: {sin_theta}")
        # test frequency
        freq = 80

        #log.debug(self.df)

        # determining leg
        leg = self.df.loc[0, 'leg']
        log.debug(f"leg: {leg}")

        # rename columns so they are easier to deal with AND does abvolute value columns
        force = []
        force = self.df['force_N'].to_list()  # adds data to form a list
        # log.debug(f"force: {force}")

        # getting time column from df
        elapsed_time = []
        elapsed_time = self.df['elapsed_time_sec'].to_list()

        torque = np.multiply(force, self.shank_length * sin_theta)
        # log.debug(f"torque: {torque}")

        # calculate the starting torque by finding the average of the first 40 (1/2 sec) of torque list
        start_torque = sum(torque[:40]) / len(torque[:40])
        # log.debug(f"start_torque: {start_torque}")

        # log.debug(f"list_torque: {list_torque}")

        # create graph and have it stored permanently to file
        fig = plt.figure()
        title = ' Iso Knee Extension'
        xlabel = "Time"
        ylabel = "Force (Nm)"

        plt.title(title, fontdict={'fontweight': 'bold', 'fontsize': 12})
        plt.plot(torque, linestyle='-', label=ylabel, color=colors_seismic[2], linewidth=1)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend()
        plt.show()

        graph = {}
        graph['title'] = title
        graph['xlabel'] = xlabel
        graph['ylabel'] = ylabel
        graph['lines'] = {'torque': torque}
        graph['elapsed_time'] = self.elapsed_time[-1]   #get the total time of the run
        self.trial.main_graph = graph

        results_dict = self.iso_knee_ext_calc(torque, elapsed_time, start_torque, leg)

        return results_dict


    def iso_knee_ext_calc(self, torque, elapsed_time, start_torque, leg):  # leg - "left", "right"

        log.debug(f"***** ISO Knee Ext")

        # torque = np.array(trial)
        # log.debug(f"torque:{torque}")

        # normalizing for time
        freq = 80
        time = np.arange(0, len(torque) / freq, 1 / freq)
        # log.debug(f"time: {time}")

        # *****************Indexing Key Points in the Contraction******************************

        # Indexing Onset of Contraction - calculatec when torque is greater than 5Nm greater than start torque
        start_iso = np.where((torque[0:] > start_torque + 5))
        onset_moment_index = start_iso[0][0]  # time stamps jump moment
        # log.debug(f"start_iso: {start_iso}, onset_moment_index: {onset_moment_index}")

        # Indexing peak torque and calculating peak torque
        peak_torque = torque.max()
        log.debug(f"peak_torque: {peak_torque}")
        # Indexing peak torque moment
        peak_torque_index = np.where(torque == np.amax(torque))
        peak_torque_index = peak_torque_index[0][0]
        log.debug(f"peak_torque_index: {peak_torque_index}")

        # Creating torque array (from onset to peak)
        torque_arr = torque[onset_moment_index:peak_torque_index]
        # Creating torque time array (from onset to peak)
        torque_time_arr = time[onset_moment_index:peak_torque_index]
        # log.debug(f"torque_time_arr: {torque_time_arr}")
        # Calculating time to peak torque
        time_to_peak_torque = torque_time_arr[-1]
        log.debug(f"time_to_peak_torque: {time_to_peak_torque}")
        # Calculating peak force impulse
        peak_torque_impulse_arr = cumtrapz(torque_arr, x=torque_time_arr, initial=0)
        # log.debug(f"peak_torque_impulse_arr: {peak_torque_impulse_arr}")
        # calculating peak impulse
        peak_torque_impulse = peak_torque_impulse_arr.max()
        log.debug(f"peak_torque_impulse: {peak_torque_impulse}")

        # Indexing Early RFD < 100ms
        i = onset_moment_index
        while i < len(elapsed_time):
            if elapsed_time[i] > .1 + elapsed_time[onset_moment_index]:
                break
            i += 1

        early_rfd_index = i

        # calculating early rfd torque from early rfd_index
        early_rfd_torque = torque[early_rfd_index]
        log.debug(f"early_rfd_torque: {early_rfd_torque}")
        # creating early rfd torque array
        early_rfd_torque_arr = torque[onset_moment_index:early_rfd_index]
        log.debug(f"early_rfd_torque_arr: {early_rfd_torque_arr}")
        # creating early rfd time array
        early_rfd_time_arr = time[onset_moment_index:early_rfd_index]
        log.debug(f"early_rfd_time_arr: {early_rfd_time_arr}")
        # calcuting early rfd impulse using cumtrapz
        early_rfd_impulse_arr = cumtrapz(early_rfd_torque_arr, x=early_rfd_time_arr, initial=0)
        log.debug(f"early_rfd_impulse_arr: {early_rfd_impulse_arr}")
        # calculating impulse using .max()
        peak_early_rfd_impulse = early_rfd_impulse_arr.max()
        log.debug(f"peak_early_rfd_impulse: {peak_early_rfd_impulse}")

        # Indexing Early RFD < 100ms

        while i < len(elapsed_time):
            if elapsed_time[i] > .2 + elapsed_time[onset_moment_index]:
                break
            i += 1

        late_rfd_index = i

        # calculating late rfd torque from late_rfd_index
        late_rfd_torque = torque[late_rfd_index]
        log.debug(f"late_rfd_torque: {late_rfd_torque}")
        # creating late rfd torque array
        late_rfd_torque_arr = torque[onset_moment_index:late_rfd_index]
        log.debug(f"late_rfd_torque_arr: {late_rfd_torque_arr}")
        # creating late rfd time array
        late_rfd_time_arr = time[onset_moment_index:late_rfd_index]
        log.debug(f"late_rfd_time_arr: {late_rfd_time_arr}")
        # calculating late rfd impulse using cumtrapz
        late_rfd_impulse_arr = cumtrapz(late_rfd_torque_arr, x=late_rfd_time_arr, initial=0)
        log.debug(f"late_rfd_impulse_arr: {late_rfd_impulse_arr}")
        # calculating late rfd impulse using .max()
        peak_late_rfd_impulse = late_rfd_impulse_arr.max()
        log.debug(f"peak_late_rfd_impulse: {peak_late_rfd_impulse}")

        peak_torque_slope_values = np.polyfit(torque_time_arr, torque_arr, 1)
        log.debug(f"peak_torque_slope_values: {peak_torque_slope_values}")
        peak_torque_slope = peak_torque_slope_values[0]
        log.debug(f"peak_torque_slope: {peak_torque_slope}")

        if self.debug_graphs:
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
        results_dict['leg'] = leg
        results_dict['peak_torque'] = peak_torque
        results_dict['peak_torque_impulse'] = peak_torque_impulse
        results_dict['peak_torque_slope'] = peak_torque_slope
        results_dict['time_to_peak_torque'] = time_to_peak_torque

        results_dict['early_rfd_torque'] = early_rfd_torque
        results_dict['early_rfd_impulse'] = peak_early_rfd_impulse
        results_dict['late_rfd_torque'] = late_rfd_torque
        results_dict['late_rfd_impulse'] = peak_late_rfd_impulse

        return results_dict
