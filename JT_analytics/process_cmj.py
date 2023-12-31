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

#### assymmetry index calcuation ****
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

