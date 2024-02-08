
import pandas as pd
import numpy as np
from scipy.integrate import cumtrapz

import matplotlib.pyplot as plt
import seaborn as sns

try:
    from . import jt_util as util
    from . import jt_plot as jtpl

except ImportError:
    import jt_util as util
    import jt_plot as jtpl

log = util.jt_logging()

# Importing Colors
colors_blue = sns.color_palette('Blues', 10)
colors_grey = sns.color_palette('Greys', 10)
colors = sns.color_palette('rocket', 10)
colors_icefire = sns.color_palette('icefire', 10)
colors3 = sns.color_palette('rainbow', 5)
colors_seismic = sns.color_palette('seismic', 10)


def asym_index(i_r, i_l, injured, col_name):
    if injured == "right":
        injured_leg = i_r
        non_injured_leg = i_l
    else:
        injured_leg = i_l
        non_injured_leg = i_r

    total_impulse = i_r + i_l

    try:
        if total_impulse != 0:
            asymmetry_index = ((non_injured_leg - injured_leg) / total_impulse) * 100
        else:
            asymmetry_index = 0

#        log.info(f'     ****** : injured_leg: {injured_leg}, non_injured_leg: {non_injured_leg}, total_impulse {total_impulse},   asymmetry_index: {asymmetry_index}')

    except:
        log.info(f'UGLY ERROR: injured_leg: {injured_leg}, non_injured_leg: {non_injured_leg}, total_impulse {total_impulse}')

#    log.debug(f"{col_name}: {asymmetry_index}")

    results_dict = {}
    results_dict[col_name] = asymmetry_index

    return results_dict

############################################
#### assymmetry index calcuation ****
class JTDcmj:

    def __init__(self, trial, path_athlete_graph=None):

        self.df = None
        self.trial = trial
        self.injured = trial.injured
        self.path_athlete_graph = path_athlete_graph
        self.athlete = trial.athlete
        self.date = trial.date_str
        self.debug_graphs = False
        self.gravity = 9.81
        self.error = False
        self.error_msg = ""
        self.force_range = 20   # this is starting point and is roughly 10% of the body weight of a small female.  It will
        # get replaced by 10% of of the force generated later on

    def process(self):
        # read in the data
        try:
            self.df = pd.read_csv(self.trial.file_path)
        except:
            log.critical(f"setup_data: file does not exist: {self.file_path}")
            return

        self.elapsed_time = self.df['elapsed_time_sec'].to_list()

        overall_time = self.elapsed_time[-1]
        num_values = len(self.elapsed_time)
        self.freq = num_values/overall_time   # calculate the frequency
        log.debug(f"JTDcmj - data point freq: {self.freq}, overall time: {overall_time}, num_value: {num_values}")

        # rename columns so they are easier to deal with AND does absolute value columns
        try:
            self.df['Right'] = self.df['r_force_N'].abs()  # absolute value of 'Right'
            list_right = self.df['Right'].to_list()  # adds data to form a list
            self.df['Left'] = self.df['l_force_N'].abs()  # absolute value of 'Left'
            list_left = self.df['Left'].to_list()  # adds data to form a list
        except:
            log.debug(f"failed abs and to_list on left or right: \n {self.df.columns}")
            return

        # mass calculations.  the freq * 2 is basically take the first 2 seconds of measurements and average them
        # for each leg and make it the bodyweight of the individual.
        self.mass_r = (np.mean(list_right[0:int(self.freq * 2)]) / self.gravity)  # calculation of Bodyweight - R
        self.mass_l = (np.mean(list_left[0:int(self.freq * 2)]) / self.gravity)  # calculation of bodyweight - L
        self.mass = abs(float(self.mass_r)) + abs(float(self.mass_l))  # calculation of bodyweight total
        ('Subject mass  {:.3f} kg'.format(self.mass))
        # log.debug(f"mass: {self.mass}")
        self.force_range = self.mass/2 * self.gravity * .08   # Use 8% of the force from one leg as the range
        log.debug(f"mass: {self.mass}, force_range: {self.force_range}")

        # normalizing for bodyweight - R
        self.force_total = [sum(i) for i in zip(list_right, list_left)]  # sums the 2 lists so that total force can be calculated

        self.force_norm_r = np.subtract(list_right, (self.mass_r * self.gravity))
        # log.debug(f"force_r: {self.force_norm_r}")
        # plt.figure(figsize=(10,6))
        # plt.plot(force_norm_r, 'b.-', linewidth=1)

        # normalizing for bodyweight - L
        self.force_norm_l = np.subtract(list_left, (self.mass_l * self.gravity))

        # log.debug(f"force_l: {self.force_norm_l}")
        # plt.figure(figsize=(10,6))
        # plt.plot(force_norm_r,'g.-', linewidth=1)
        ##### process a cmj dataframe, must include which leg is injured ('Right', or 'Left')

        ### Full timeline graph
        title = self.athlete + ' CMJ ' + self.date
        xlabel = "Time"
        ylabel = "Force (Nm)"

        if self.debug_graphs:
            plt.figure(figsize=(10, 6))
            plt.title(title, fontdict={'fontweight':'bold', 'fontsize': 12})
            plt.plot(self.force_norm_r, linestyle = '-', label = 'Right', color=colors_seismic[2], linewidth = 1)
            plt.plot(self.force_norm_l, linestyle = '-', label = 'Left', color=colors_icefire[4], linewidth = 1)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.legend()
            plt.show()

        # store the lines away for later use in the Trial Object
        line_data = [
            {'y': self.force_norm_l, 'label': 'Left', 'color': 0},
            {'y': self.force_norm_r, 'label': 'Right', 'color': 1}]

        my_plot = jtpl.JT_plot(title, xlabel, ylabel, line_data)
        my_plot.set_marker_none()

        graph = {}
        graph['title'] = title
        graph['xlabel'] = xlabel
        graph['ylabel'] = ylabel
        graph['lines'] = {'Left': self.force_norm_l, 'Right': self.force_norm_r }
        graph['elapsed_time'] = self.elapsed_time[-1]   #get the total time of the run
        self.trial.main_graph = graph

        log.debug(f'Setup data {self.athlete}, {self.date}')

        # normalizing for bodyweight - See slides // subtract bodyweight and make BM = 0
        force_norm = np.subtract(self.force_total, self.mass * self.gravity)
        # log.debug(f"force_norm: {force_norm}")

        if (self.debug_graphs is True):

            # force total graph
            plt.figure(figsize=(10,6))
            title = self.athlete + ' force_total ' + self.date
            plt.title(title, fontdict={'fontweight':'bold', 'fontsize': 12})
            plt.plot(self.force_total, 'b.-', linewidth=1)
            plt.xlabel('Time')
            plt.ylabel('Force')
            plt.show()

            # force norm graph
            plt.figure(figsize=(10,6))
            title = self.athlete + ' force_norm ' + self.date
            plt.title(title, fontdict={'fontweight':'bold', 'fontsize': 12})
            plt.plot(force_norm, 'b.-', linewidth=1)
            plt.xlabel('Time')
            plt.ylabel('Force')
            plt.show()

        ######################################
        ##### CMJ calculation functions for both legs, Left, and right
        ######################################
        try:
            results_dict = self.cmj_calc(force_norm, self.mass)
        except:
            self.error_msg = "Failed cmj_calc"
            self.error = True
            log.error(self.error_msg)
            return

        #Left Leg calcs
        try:
            results_dict_l = self.cmj_sl_calc(self.force_norm_l, "left", self.mass_l)
            cmj_arr_l = results_dict_l.get('cmj_arr')
            del results_dict_l['cmj_arr']
        except:
            self.error_msg = "Failed cmjP_sl_calc LEFT"
            self.error = True
            log.error(self.error_msg)
            return

        #Right Leg calcs
        try:
            results_dict_r = self.cmj_sl_calc(self.force_norm_r, "right", self.mass_r)
            cmj_arr_r = results_dict_r.get('cmj_arr')
            del results_dict_r['cmj_arr']
        except:
            self.error_msg = "Failed cmjP_sl_calc Right"
            self.error = True
            log.error(self.error_msg)
            return

        ######################################

        # create graph and have it stored permanently to file
        title = self.athlete + ' CMJ ' + self.date
        xlabel = "Time"
        ylabel = "Force N"

        fig = plt.figure()
        plt.title(title, fontdict={'fontweight': 'bold', 'fontsize': 12})
        plt.plot(cmj_arr_l, linestyle='-', label='Left', color=colors_seismic[2], linewidth=1)
        plt.plot(cmj_arr_r, linestyle='-', label='Right', color=colors_icefire[4], linewidth=1)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend()

        if self.path_athlete_graph is not None:
            graph_filename = self.path_athlete_graph + self.trial.short_filename
            log.debug(f"graph_filename: {graph_filename}")

            plt.savefig(graph_filename,
                        transparent=False,
                        facecolor='white', dpi=300,
                        bbox_inches="tight")

            results_dict['GRAPH_1'] = graph_filename

        plt.close(fig)


        # log.debug(f' L: {results_dict_l} R: {results_dict_r}')
        results_dict.update(results_dict_l)
        results_dict.update(results_dict_r)

        # force asymmetry calcs
        r = asym_index(results_dict['force_right'], results_dict['force_left'], self.injured, 'force_asymmetry_index')
        results_dict.update(r)
        r = asym_index(results_dict['unloading_force_right'], results_dict['unloading_force_left'], self.injured, 'unloading_force_asymmetry_index')
        results_dict.update(r)
        r = asym_index(results_dict['braking_force_right'], results_dict['braking_force_left'], self.injured, 'braking_force_asymmetry_index')
        results_dict.update(r)
        r = asym_index(results_dict['concentric_force_right'], results_dict['concentric_force_left'], self.injured, 'concentric_force_asymmetry_index')
        results_dict.update(r)

        # impulse asymmetry calcs
        r = asym_index(results_dict['impulse_right'], results_dict['impulse_left'], self.injured, 'impulse_asymmetry_index')
        results_dict.update(r)
        r = asym_index(results_dict['unloading_impulse_right'], results_dict['unloading_impulse_left'], self.injured, 'unloading_impulse_asymmetry_index')
        results_dict.update(r)
        r = asym_index(results_dict['braking_impulse_right'], results_dict['braking_impulse_left'], self.injured, 'braking_impulse_asymmetry_index')
        results_dict.update(r)
        r = asym_index(results_dict['concentric_impulse_right'], results_dict['concentric_impulse_left'], self.injured, 'concentric_impulse_asymmetry_index')
        results_dict.update(r)

        return results_dict

    ####################################################
    ##### cmj_calc() - does all calculations for a cmj
    def cmj_calc(self, single_force, mass):
        log.debug("** CMJ calc")

        force = np.array(single_force)
        # log.debug(f"cmj force:{force}")
        # normalizing for time

        time = np.arange(0, len(force) / self.freq, 1 / self.freq)
        # log.debug(f"time: {time}")

        # ******************************* Indexing Key Points in the Jump******************************
        # Onset of Jump
        start_jump = np.where((force[0:] > self.force_range) | (force[0:] < -self.force_range))  # if want to use one function, need to perform mass / 2
        #log.debug(f'start_jump: {start_jump}')

        jump_onset_moment_index = start_jump[0][0]  # time stamps jump moment
        log.debug(f"INDEX jump_onset_moment_index: {jump_onset_moment_index}")

        # NEW CODE
        # Start of the flight phase
        # to do this we know it is after the onset moment.  By studying data we know that crouching and jumping is
        # around .6 to .8 seconds.   Therefore I picked .3 seconds to delay looking for the minimum point.  This was
        # done to deal with the fact if they crouch quick enough they essentially have zero weight on their feet
        # which was triggering the start of flight at that point rather than after they actually jumped.
        fudge_factor = int(.3 * self.freq)   #seconds * FPS (or measurements per second)
        starting_pt_index = jump_onset_moment_index + fudge_factor
#        print(f'--jump_onset_moment_index {jump_onset_moment_index} starting_pt_index: {starting_pt_index}')

        start_flight = np.where(
            force[starting_pt_index:] < (np.amin(force[starting_pt_index:]) + 10))  # need to create if statement so that left and right can be calculated
#        print( start_flight)
        # log.debug(f"min: {np.amin(force)}")
        # log.debug(f"start_flight: {start_flight}")
        takeoff_moment_index = starting_pt_index + start_flight[0][0]  # time stamps takeoff moment
        log.debug(f"INDEX takeoff_moment_index: {takeoff_moment_index}")

        # jump time (from start of jump until in the air)
        time_ss = time[
                  jump_onset_moment_index:takeoff_moment_index]  # creates a time subset from jump onset moment to takeoff
        # log.debug(f"time_ss: {time_ss}")

        # check to see if enough variables to calculate jumptime, must be 2 of themm - Dad added this
        if len(time_ss) < 2:
            jump_time = 0
        else:
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
        if (self.debug_graphs is True):
            #  Graph impulse and delta_velocity
            plt.figure()
            plt.title('Acceleration Curve', fontdict={'fontweight': 'bold', 'fontsize': 12})
            plt.plot(acceleration2, linestyle='-', label='Acceleration', color=colors_seismic[2], linewidth=1)
            plt.xlabel('Time')
            plt.ylabel('Acceleration (m/s^2)')

        # Calculating velocity by integrating acceleration
        velocity2 = cumtrapz(acceleration2, x=time_ss, initial=0)
        if (self.debug_graphs is True):
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
        if (self.debug_graphs is True):
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
        jump_height = ((ToV) ** 2) / (2 * self.gravity)  # jump height = (takeoff velocity)**2 / (2*gravity)
        log.debug(f"  jump_height: {jump_height}")

        # ** Calculating Jump Height Through TIA (Control)****************************

        # Calculating time in air
        #start_land = np.where(force[0:] == (np.amax(force)))  # need to create if statement so that left and right can be calculated

        max_value = np.amax(force[takeoff_moment_index:])
        start_land = np.where( force[takeoff_moment_index:] == max_value)[0] + takeoff_moment_index

        landing_moment = start_land[0]
        log.debug(f"  takeoff_moment_index: {takeoff_moment_index},  landing_moment_index: {landing_moment}")
        tia_ss = time[takeoff_moment_index:landing_moment]
        tia_ss_total = tia_ss[-1] - tia_ss[0]
        # log.debug(f"tia_ss_total: {tia_ss_total}")

        # Calculating Jump Height with TIA
        jump_height_tia = .5 * self.gravity * ((tia_ss_total / 2) ** 2)
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
        if (self.debug_graphs is True):
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
        # SRT ERROR CHECK FOR divide by zero
        if CoM_displacement_value == 0:
            log.debug("Would be divide by zero so changing CoM_displacement_value to 1")
            CoM_displacement_value = 1

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
        if velocity_zero_index[0].size > 0:
            velocity_zero_index = velocity_zero_index[0][0]
        else:
            velocity_zero_index = len(delta_velocity)
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
        #SRT - maybe a hack but the bottom line is the braking_end_index must be less and the concentric_end_index
        # this doesn't happen that often but occassionally it does.  Sooo, if it does modify concentric end to be 2 more
        # than the braking end_index.  I have no idea how bad this corrupts things so smarter people will have to decide
        # otherwise the code will continue to fail
        if braking_end_index >= concentric_end_index:
            log.debug(f"for both legs had to tweak concentric_end_index to be one more than braking end_index:  {self.trial.original_filename}")
            concentric_end_index = braking_end_index + 1

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

        if (self.debug_graphs is True):
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

        # add in elapsed time for the key indexes
        results_dict['jump_onset_moment_time'] = self.elapsed_time[jump_onset_moment_index]
        results_dict['takeoff_moment_time'] = self.elapsed_time[takeoff_moment_index]
        results_dict['unloading_end_time'] = self.elapsed_time[unloading_end_index]
        results_dict['braking_end_time'] = self.elapsed_time[braking_end_index]

        results_dict['velocity_min_time'] = self.elapsed_time[velocity_min_index]
        results_dict['velocity_zero_time'] = self.elapsed_time[velocity_zero_index]
        results_dict['velocity_max_time'] = self.elapsed_time[velocity_max_index]
        results_dict['concentric_end_time'] = self.elapsed_time[concentric_end_index]

        # add in indexes (cause why not, it is easier than picking the time)
        results_dict['jump_onset_moment_index'] = jump_onset_moment_index
        results_dict['takeoff_moment_index'] = takeoff_moment_index
        results_dict['unloading_end_index'] = unloading_end_index
        results_dict['braking_end_index'] = braking_end_index

        results_dict['velocity_min_index'] = velocity_min_index
        results_dict['velocity_zero_index'] = velocity_zero_index
        results_dict['velocity_max_index'] = velocity_max_index
        results_dict['concentric_end_index'] = concentric_end_index


        return results_dict

    ###############################################
    ##### single leg CMJ function
    def cmj_sl_calc(self, single_leg_force, leg, mass):  # leg - "left", "right"
        log.debug(f"**** {leg} ")
        force_leg = np.array(single_leg_force)

        # normalizing for time

        time = np.arange(0, len(force_leg) / self.freq, 1 / self.freq)
        # log.debug(f"time: {time}")

        # Onset of Jump - need to divide teh force_range by 2 because it is just one leg and not both
        start_jump = np.where(
            (force_leg[0:] > self.force_range) | (force_leg[0:] < -self.force_range))  # if want to use one function, need to perform mass / 2
        jump_onset_moment_index = start_jump[0][0]  # time stamps jump moment
        # log.debug(f"start_jump: {len(start_jump)} {start_jump}")
        log.debug(f"jump_onset_moment_index: {jump_onset_moment_index}")

        # NEW CODE
        # Start of the flight phase
        # to do this we know it is after the onset moment.  By studying data we know that crouching and jumping is
        # around .6 to .8 seconds.   Therefore I picked .3 seconds to delay looking for the minimum point.  This was
        # done to deal with the fact if they crouch quick enough they essentially have zero weight on their feet
        # which was triggering the start of flight at that point rather than after they actually jumped.
        fudge_factor = int(.3 * self.freq)  # seconds * FPS (or measurements per second)
        starting_pt_index = jump_onset_moment_index + fudge_factor
        #        print(f'--jump_onset_moment_index {jump_onset_moment_index} starting_pt_index: {starting_pt_index}')

        start_flight = np.where(
            force_leg[starting_pt_index:] < (np.amin(force_leg[starting_pt_index:]) + 10))  # need to create if statement so that left and right can be calculated
        #        print( start_flight)
        # log.debug(f"min: {np.amin(force)}")
        # log.debug(f"start_flight: {start_flight}")
        takeoff_moment_index = starting_pt_index + start_flight[0][0]  # time stamps takeoff moment
        log.debug(f"INDEX takeoff_moment_index: {takeoff_moment_index}")

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
        #log.debug(f"impulse_{leg}: {impulse_arr}")

        peak_impulse = impulse_arr.max()
        log.debug(f"peak_impulse: {peak_impulse}")

        if (self.debug_graphs is True):
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
        #handle error condition where velocity min is zero
        if velocity_min_index != 0:
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
        else:
            #error condition - probably not the right answer but better than crashing
            peak_unloading_force = 0
            peak_unloading_impulse = 0

        ##################################
        # Braking Phase

        velocity_zero_index = np.where(delta_velocity[velocity_min_index:] > 0)
        # Check if any index was found   SRT Modified if it can't find any sets it to zero
        if velocity_zero_index[0].size > 0:
            velocity_zero_index = velocity_zero_index[0][0]
        else:
            velocity_zero_index = len(delta_velocity)
        log.debug(f"INDEX velocity_zero_index: {velocity_zero_index}")

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
        log.debug(f"INDEX velocity_max_index: {velocity_max_index}")

        concentric_end_index = (jump_onset_moment_index + velocity_max_index)
        log.debug(f"INDEX concentric_end_index: {concentric_end_index}")
        #SRT - maybe a hack but the bottom line is the braking_end_index must be less and the concentric_end_index
        # this doesn't happen that often but occassionally it does.  Sooo, if it does modify concentric end to be 2 more
        # than the braking end_index.  I have no idea how bad this corrupts things so smarter people will have to decide
        # otherwise the code will continue to fail
        if braking_end_index >= concentric_end_index:
            log.debug(f"for single leg had to tweak concentric_end_index to be one more than braking end_index: {self.trial.original_filename}")
            concentric_end_index = braking_end_index + 1

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



