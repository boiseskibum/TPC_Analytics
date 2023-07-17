
import sys
sys.path.append('../share')

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


#### SJ - process_sj_df() sj_calc()  #######
# process a cmj dataframe, must include which leg is injured ('Right', or 'Left')
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

