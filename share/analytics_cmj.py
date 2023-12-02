# from """CMJ_graphing_base_profile.ipynb

import os, platform, glob

import matplotlib.pyplot as plt
import seaborn as sns
colors_blue = sns.color_palette('Blues', 10)
colors_grey = sns.color_palette('Greys', 10)
colors = sns.color_palette('rocket', 10)
colors_icefire = sns.color_palette('icefire', 10)
colors3 = sns.color_palette('rainbow', 5)
colors_seismic = sns.color_palette('seismic', 10)

import numpy as np
import pandas as pd
import matplotlib.gridspec as gridspec
from dateutil import parser
from datetime import date

from fpdf import FPDF
#from fpdf.enums import XPos, YPos

#from fpdf.enums import XPos, YPos

try:
    from . import jt_util as util
    from . import jt_plot as jtpl
    from . import jt_config as jtc

except:
    import jt_util as util
    import jt_plot as jtpl
    import jt_config as jtc

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

class JT_analytics_cmj:
    def __init__(self, config_obj, athlete):

        self.athlete = athlete
        self.config_obj = config_obj
        self.path_data_athlete = self.config_obj.path_data_athlete(self.athlete)
        self.path_results_athlete = self.config_obj.path_results_athlete(self.athlete)
        self.path_athlete_images = self.config_obj.path_athlete_images(self.athlete)
        self.today_date = date.today()

        # import data
        file_name = self.config_obj.path_db + "JTDcmj_data.csv"
        try:
            df = pd.read_csv(file_name)
        except:
            log.error(f'Unable to open DataFile: {file_name}')
            return

        # add date time stamp column, # this call the function parse.parse() for each row passing in col_timestamp_str
        df["datetime_object"] = df["col_timestamp_str"].apply(parser.parse)

        # set up colors to make easier
        jt_color1 = colors_seismic[2]
        jt_color2 = colors_icefire[4]

        #filter data down to the specific athlete
        athlete_filter = df[df['athlete_name'] == athlete]

#        print(athlete_filter.columns)
        log.debug(athlete_filter[['athlete_name', 'col_timestamp_str']])
#        print(athlete_filter[['col_timestamp_str']])
        log.debug(f'number of rows: {len(athlete_filter)}')

        # temp_df = athlete_filter.groupby(['athlete_name', pd.Grouper(key='datetime_object', axis=0, freq='D', sort=True)]).mean()
        temp_df = athlete_filter.groupby(pd.Grouper(key='datetime_object', axis=0, freq='D', sort=True)).mean(numeric_only=True).reset_index()
        mean_df = temp_df.dropna()
        # print(f'mean_df {mean_df.columns}')
        # print(mean_df['datetime_object'])

        self.plot_list = []

        # ********************* Create impulse graph ****************************
        line_data = [{'x': mean_df['datetime_object'], 'y': mean_df['impulse'], 'label': 'Total Impulse', 'color': jt_color1}]
        my_plot = jtpl.JT_plot('CMJ Impulse', 'Date', 'Impulse (N-s)', line_data)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_Impulse_graph.png')
        self.plot_list.append(my_plot)

        # ******************** Create ToV graph ***********************
        line_data = [{'x': mean_df['datetime_object'], 'y': mean_df['ToV'], 'label': 'ToV', 'color': jt_color1}]
        my_plot = jtpl.JT_plot('CMJ ToV', 'Date', 'ToV (m/s)', line_data)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_ToV_graph.png')
        self.plot_list.append(my_plot)

        # ******************** Create CMJ RSI Modified graph ***********************
        line_data = [
            {'x': mean_df['datetime_object'], 'y': mean_df['rsi_mod'], 'label': 'RSI-Mod', 'color': jt_color1}]
        my_plot = jtpl.JT_plot('CMJ RSI Modified', 'Date', 'RSI Mod', line_data)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_RSI_graph.png')
        self.plot_list.append(my_plot)

        # ******************** Create Jump Contraction Time graph ***********************
        line_data = [
            {'x': mean_df['datetime_object'], 'y': mean_df['jump_time'], 'label': 'Jump Time', 'color': jt_color1}]
        my_plot = jtpl.JT_plot('Jump Contraction Time', 'Date', 'Time (s)', line_data)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_jump_time_graph.png')
        self.plot_list.append(my_plot)

        # ******************** Create CoM Displacement graph ***********************
        line_data = [
            {'x': mean_df['datetime_object'], 'y': mean_df['CoM_displacement'], 'label': 'CoM Displacement', 'color': jt_color1}]
        my_plot = jtpl.JT_plot('CMJ CoM Displacement', 'Date', 'Time (s)', line_data)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_CoM_displacement_graph.png')
        self.plot_list.append(my_plot)

        # ******************** Create Force Comparison graph ***********************
        line_data = [{'x': mean_df['datetime_object'], 'y': mean_df['force_right'], 'label': 'Force Right',
                      'color': jt_color1},
                     {'x': mean_df['datetime_object'], 'y': mean_df['force_left'], 'label': 'Force Left',
                      'color': jt_color2}]
        my_plot = jtpl.JT_plot('CMJ Peak Force Comparison', 'Date', 'Force (N)', line_data)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_force_comparison_graph.png')
        self.plot_list.append(my_plot)

        # ******************** Create Force Asymmetry Graph ***********************
        line_data = [
            {'x': mean_df['datetime_object'], 'y': mean_df['force_asymmetry_index'], 'label': 'Asymmetry Index','color': jt_color1}]
        my_plot = jtpl.JT_plot('CMJ Force Asymmetry Index', 'Date', 'Asymmetry Index (%)', line_data)
        my_plot.set_yBounds([15, -15])
        my_plot.set_yminmax(-40, 40)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_force_asymmetry_graph.png')
        self.plot_list.append(my_plot)

        # ******************** Create Unloading Impulse Graph ***********************
        line_data = [
            {'x': mean_df['datetime_object'], 'y': mean_df['peak_unloading_impulse'], 'label': 'Unloading Impulse', 'color': jt_color1}]
        my_plot = jtpl.JT_plot('CMJ Unloading Impulse', 'Date', 'Impulse (N-s)', line_data)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_unloading_impulse_graph.png')
        self.plot_list.append(my_plot)

        # ******************** Create SL Unloading Force Graph ***********************
        line_data = [
            {'x': mean_df['datetime_object'], 'y': mean_df['unloading_force_right'], 'label': 'Force Right',
             'color': jt_color1},
            {'x': mean_df['datetime_object'], 'y': mean_df['unloading_force_left'], 'label': 'Force Left',
             'color': jt_color2}]
        my_plot = jtpl.JT_plot('CMJ Unloading Force Comparison', 'Date', 'Force (N)', line_data)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_sl_unloading_force_graph.png')
        self.plot_list.append(my_plot)

        # ******************** Create Unloading Force Asymmetry Graph ***********************
        line_data = [{'x': mean_df['datetime_object'], 'y': mean_df['unloading_force_asymmetry_index'],
                      'label': 'Asymmetry Index', 'color': jt_color1}]
        my_plot = jtpl.JT_plot('CMJ Unloading Force Asymmetry Index', 'Date', 'Asymmetry Index (%)', line_data)
        my_plot.set_yBounds([15, -15])
        my_plot.set_yminmax(-40, 40)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_unloading_force_asymmetry_graph.png')
        self.plot_list.append(my_plot)

        # ******************** Create Braking Impulse Graph ***********************
        line_data = [{'x': mean_df['datetime_object'], 'y': mean_df['peak_braking_impulse'], 'label': 'Braking Impulse', 'color': jt_color1}]
        my_plot = jtpl.JT_plot('CMJ Braking Impulse', 'Date', 'Impulse (N-s)', line_data)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_braking_impulse_graph.png')
        self.plot_list.append(my_plot)

        # ******************** Create SL Braking Force Graph ***********************
        line_data = [{'x': mean_df['datetime_object'], 'y': mean_df['braking_force_right'], 'label': 'Force Right',
                      'color': jt_color1},
                     {'x': mean_df['datetime_object'], 'y': mean_df['braking_force_left'], 'label': 'Force Left',
                      'color': jt_color2}]
        my_plot = jtpl.JT_plot('CMJ Braking Force Comparison', 'Date', 'Force (N)', line_data)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_sl_braking_force_graph.png')
        self.plot_list.append(my_plot)

        # ******************** Create Braking Force Asymmetry Graph ***********************
        line_data = [{'x': mean_df['datetime_object'], 'y': mean_df['braking_force_asymmetry_index'],
                      'label': 'Asymmetry Index', 'color': jt_color1}]
        my_plot = jtpl.JT_plot('CMJ Braking Force Asymmetry Index', 'Date', 'Asymmetry Index (%)', line_data)
        my_plot.set_yBounds([15, -15])
        my_plot.set_yminmax(-40, 40)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_braking_force_asymmetry_graph.png')
        self.plot_list.append(my_plot)

        # ******************** Create Concentric Impulse Graph ***********************
        line_data = [
            {'x': mean_df['datetime_object'], 'y': mean_df['peak_concentric_impulse'], 'label': 'Concentric Impulse', 'color': jt_color1}]
        my_plot = jtpl.JT_plot('CMJ Concentric Impulse', 'Date', 'Impulse (N-s)', line_data)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_concentric_impulse_graph.png')
        self.plot_list.append(my_plot)

        # ******************** Create SL Concentric Force Graph ***********************
        line_data = [
            {'x': mean_df['datetime_object'], 'y': mean_df['concentric_force_right'], 'label': 'Force Right',
             'color': jt_color1},
            {'x': mean_df['datetime_object'], 'y': mean_df['concentric_force_left'], 'label': 'Force Left',
             'color': jt_color2}]
        my_plot = jtpl.JT_plot('CMJ Concentric Force Comparison', 'Date', 'Force (N)', line_data)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_sl_concentric_force_graph.png')
        self.plot_list.append(my_plot)

        # ******************** Create Concentric Force Asymmetry Graph ***********************
        line_data = [{'x': mean_df['datetime_object'], 'y': mean_df['concentric_force_asymmetry_index'],
                      'label': 'Asymmetry Index', 'color': jt_color1}]
        my_plot = jtpl.JT_plot('CMJ Concentric Force Asymmetry Index', 'Date', 'Asymmetry Index (%)', line_data)
        my_plot.set_yBounds([15, -15])
        my_plot.set_yminmax(-40, 40)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_concentric_force_asymmetry_graph.png')
        self.plot_list.append(my_plot)

        # ********************* Create Mean Power Graph ****************************
        line_data = [{'x': mean_df['datetime_object'], 'y': mean_df['mean_power'], 'label': 'Mean Power', 'color': jt_color1}]
        my_plot = jtpl.JT_plot('Mean Power', 'Date', 'Power (W)', line_data)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_mean_power_graph.png')
        self.plot_list.append(my_plot)

        # ********************* Create Peak Power Graph ****************************
        line_data = [{'x': mean_df['datetime_object'], 'y': mean_df['peak_power'], 'label': 'Peak Power', 'color': jt_color1}]
        my_plot = jtpl.JT_plot('Peak Power', 'Date', 'Power (W)', line_data)
        my_plot.set_output_filepath(self.path_athlete_images + 'cmj_peak_power_graph.png')
        self.plot_list.append(my_plot)

    def save_to_disk(self):

        for plot in self.plot_list:
            plot.save_to_file()

    # PDF Standard graphs
    # code to create header and footer
    # Documentation here: https://pyfpdf.github.io/fpdf2/Tutorial.html
    def create_pdf(self):

        today_date = date.today()

        logo = self.config_obj.resources + "jt.png"
        if not os.path.exists(logo):
            logo = "jt.png"
            if not os.path.exists(logo):
                logo = None

        log.debug(f"logo: {logo}")

        # Margin
        m = 10
        # Page width: Width of A4 is 210mm
        pw = 210 - 2 * m

        athlete_name = self.athlete
        class PDF(FPDF):
            def header(self):
                # Rendering logo:
                if logo is not None:
                    self.image(logo, 10, 8, 12)  # last parameter - "12" is how to change the size
                # Setting font: helvetica bold
                self.set_font("helvetica", "B", 12)
                # Moving cursor to the right:
                self.cell(pw / 2 - 20)  # the 20 is a fudge factor to account for the logo
                # Printing title:
                self.cell(30, 10, "Force Plate Assessment:  " + athlete_name, align="C")
                # Performing a line break:

            def footer(self):
                # Position cursor at 1.5 cm from bottom:
                self.set_y(-15)
                # Setting font: helvetica italic 8
                self.set_font("helvetica", "I", 8)
                # Printing Date:
                self.cell(0, 10, f"Date {today_date}", align="L")
                # Printing page number:
#                self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, align="C")
                # Printing name
                self.cell(0, 0, f"Taylor Performance Consulting", align="L")

        ### create PDF
        pdf = PDF()
        pdf.add_page()
        pdf.set_font('Helvetica', '', 10)

        # constant for half way across the page (2 columns)
        half_pw = 100
        x_start = 0
        y_start = 30

        # set image width and height between graphs
        image_w = 100
        image_h = 65

        # row 1
        pdf.image(self.path_athlete_images + 'cmj_Impulse_graph.png',
                  x=x_start, y=y_start, w=image_w,
                  h=0)  # 0 for height allows image to scale, with value it will squish or fatten the image

        pdf.image(self.path_athlete_images + 'cmj_force_comparison_graph.png',
                  x=half_pw, y=y_start, w=image_w, h=0)

        # row 2
        y_start += image_h
        pdf.image(self.path_athlete_images + 'cmj_ToV_graph.png',
                  x=x_start, y=y_start, w=image_w, h=0)

        pdf.image(self.path_athlete_images + 'cmj_RSI_graph.png',
                  x=half_pw, y=y_start, w=image_w, h=0)

        # row 3
        y_start += image_h
        pdf.image(self.path_athlete_images + 'cmj_jump_time_graph.png',
                  x=x_start, y=y_start, w=image_w, h=0)

        pdf.image(self.path_athlete_images + 'cmj_CoM_displacement_graph.png',
                  x=half_pw, y=y_start, w=image_w, h=0)

        # row 4 - just one image
        y_start += image_h
        pdf.image(self.path_athlete_images + 'cmj_force_asymmetry_graph.png',
                  x=half_pw / 2, y=y_start, w=image_w, h=0)

        output_file = self.path_results_athlete + 'cmj report.pdf'
        print(f'PDF created: {output_file}')
        # save PDF File
        pdf.output(output_file)


    # Advanced PDF
    # code to create header and footer
    # Documentation here: https://pyfpdf.github.io/fpdf2/Tutorial.html
    def create__pdf2(self):
        today_date = date.today()
        logo = self.config_obj.resources + "jt.png"
        if not os.path.exists(logo):
            logo = "jt.png"
            if not os.path.exists(logo):
                logo = None
        print(f"logo: {logo}")

        # Margin
        m = 10
        # Page width: Width of A4 is 210mm
        pw = 210 - 2 * m
        athlete_name = self.athlete

        class PDF(FPDF):
            def header(self):
                # Rendering logo:
                if logo is not None:
                    self.image(logo, 10, 8, 12)  # last parameter - "12" is how to change the size
                # Setting font: helvetica bold
                self.set_font("helvetica", "B", 12)
                # Moving cursor to the right:
                self.cell(pw / 2 - 20)  # the 20 is a fudge factor to account for the logo
                # Printing title:
                self.cell(30, 10, "Advanced Force Plate Assessment:  " + athlete_name, align="C")
                # Performing a line break:

            def footer(self):
                # Position cursor at 1.5 cm from bottom:
                self.set_y(-15)
                # Setting font: helvetica italic 8
                self.set_font("helvetica", "I", 8)
                # Printing Date:
                self.cell(0, 10, f"Date {today_date}", align="L")
                # Printing page number:
                self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                # Printing name
                self.cell(0, 0, f"Taylor Performance Consulting", align="L")

        ### creaTE PDF
        pdf = PDF()
        pdf.add_page()
        pdf.set_font('Helvetica', '', 10)
        # pdf.cell(w=0, h=10, txt="Force Plate Assessment", new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 8)
        # pdf.cell(txt="Date:    "+today_date, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # pdf.cell(txt="Athlete: "+athlete, new_x=XPos.LEFT, new_y=YPos.NEXT)

        # constant for half way across the page (2 columns)
        half_pw = 100
        x_start = 0
        y_start = 30

        # set image width and height between graphs
        image_w = 100
        image_h = 65

        # row 1
        pdf.image(self.path_athlete_images + 'cmj_braking_impulse_graph.png',
                  x=x_start, y=y_start, w=image_w,
                  h=0)  # 0 for height allows image to scale, with value it will squish or fatten the image

        pdf.image(self.path_athlete_images + 'cmj_braking_force_asymmetry_graph.png',
                  x=half_pw, y=y_start, w=image_w, h=0)

        # row 2
        y_start += image_h
        pdf.image(self.path_athlete_images + 'cmj_concentric_impulse_graph.png',
                  x=x_start, y=y_start, w=image_w, h=0)

        pdf.image(self.path_athlete_images + 'cmj_concentric_force_asymmetry_graph.png',
                  x=half_pw, y=y_start, w=image_w, h=0)

        # row 3
        y_start += image_h
        pdf.image(self.path_athlete_images + 'cmj_mean_power_graph.png',
                  x=x_start, y=y_start, w=image_w, h=0)

        pdf.image(self.path_athlete_images + 'cmj_peak_power_graph.png',
                  x=half_pw, y=y_start, w=image_w, h=0)

        # save PDF File
        output_file = self.path_results_athlete + 'cmj advanced report.pdf'
        print(f'PDF created: {output_file}')
        # save PDF File
        pdf.output(output_file)

if __name__ == "__main__":

    config_obj = jtc.JT_Config('taylor performance', 'TPC', None)
    val = config_obj.validate_install()
    print('convig_obj.validate return value: {val}')

    cmj_analytics = JT_analytics_cmj(config_obj, 'huey')

    #show graphs by passisng save_to_file a False parameter
    for plot in cmj_analytics.plot_list:
        plot.save_to_file()

    cmj_analytics.create_pdf()

    #save all plots to disk
#    cmj_analytics.save_to_disk()

