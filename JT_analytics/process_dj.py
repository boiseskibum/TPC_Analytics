import sys
sys.path.append('../share')

import numpy as np
from scipy.integrate import cumtrapz

import matplotlib.pyplot as plt
import seaborn as sns

import jt_util as util

log = util.jt_logging()
log.set_logging_level("WARNING")   # this will show errors but not files actually processed

# Importing Colors
colors_blue = sns.color_palette('Blues', 10)
colors_grey = sns.color_palette('Greys', 10)
colors = sns.color_palette('rocket', 10)
colors_icefire = sns.color_palette('icefire', 10)
colors3 = sns.color_palette('rainbow', 5)
colors_seismic = sns.color_palette('seismic', 10)

#### DJ - process_dj_df() ##############################################
# process a cmj dataframe, must include which leg is injured ('Right', or 'Left')

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
