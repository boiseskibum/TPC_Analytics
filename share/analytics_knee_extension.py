# Import necessary modules
from dateutil import parser
from datetime import date

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF

try:
    from . import jt_util as util
    from . import jt_protocol as jtp
    from . import jt_athletes as jta
    from . import jt_config as jtc
    from . import jt_plot as jtpl

except:
    import jt_util as util
    import jt_protocol as jtp
    import jt_athletes as jta
    import jt_config as jtc
    import jt_plot as jtpl

# Importing Colors
colors_blue = sns.color_palette('Blues', 10)
colors_grey = sns.color_palette('Greys', 10)
colors = sns.color_palette('rocket', 10)
colors_icefire = sns.color_palette('icefire', 10)
colors3 = sns.color_palette('rainbow', 5)
colors_seismic = sns.color_palette('seismic', 10)
colors_PuBu = sns.color_palette('PuBu', 10)
colors_GnBu = sns.color_palette('GnBu', 10)

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

class JT_analytics_knee_ext_iso:
    def __init__(self, config_obj, athlete ):

        self.athlete = athlete
        self.config_obj = config_obj
        self.path_data_athlete = self.config_obj.path_data_athlete(self.athlete)
        self.path_results_athlete = self.config_obj.path_results_athlete(self.athlete)
        self.path_athlete_images = self.config_obj.path_athlete_images(self.athlete)
        self.today_date = date.today()

        self.plot_list = []

        # set up colors to make easier
        jt_color1 = colors_GnBu[7]
        jt_color2 = colors_grey[3]

        # get injured
        athletes_obj = self.config_obj.athletes_obj
        self.injured = athletes_obj.get_injured_side(self.athlete)

        # import data
        file_name = self.config_obj.path_db + "JTSext_data.csv"
        try:
            self.df = pd.read_csv(file_name)
        except:
            log.error(f'Unable to open DataFile: {file_name}')
            return

        # add date time stamp column, # this call the function parse.parse() for each row passing in col_timestamp_str
        self.df["datetime_object"] = self.df["col_timestamp_str"].apply(parser.parse)
        self.df["date_str"] = self.df["datetime_object"].apply(lambda x: x.strftime('%Y-%m-%d'))

        # filter data down to the specific athlete and make a copy of the data
        athlete_df = self.df[self.df['athlete_name'] == athlete].copy()

        # validate that there is a "left" and "right" for each date int he data set and if there isn't then make a
        # fake row with 0's in the values.  It will look ugly but be better than crashing
        # print('before fixing')
        # print(athlete_df)
        unique_dates = athlete_df['date_str'].unique()

        new_rows = []
        # Iterate over each unique date and check for left/right leg entries
        for my_date in unique_dates:
            for leg in ['left', 'right']:
                if not ((athlete_df['date_str'] == my_date) & (athlete_df['leg'] == leg)).any():
                    # Find a row for this my_date to duplicate
                    row_to_duplicate = athlete_df[athlete_df['date_str'] == my_date].iloc[0]

                    # Create a new row with the missing leg and other column values
                    new_row = row_to_duplicate.copy()
                    new_row['leg'] = leg
                    # Set other columns to 0 or appropriate default value
                    # Assuming other columns here which need to be set to 0
                    # new_row['other_column'] = 0

                    # Append the new row to the DataFrame
#                    athlete_df = athlete_df.append(new_row, ignore_index=True)
                    # Add the new row to the list
                    new_rows.append(new_row)

        # Append new rows to the DataFrame
        if new_rows:
            athlete_df = pd.concat([athlete_df, pd.DataFrame(new_rows)], ignore_index=True)

        # Sort and reset index if needed
        athlete_df = athlete_df.sort_values(by=['date_str', 'leg']).reset_index(drop=True)

        # print('Fixed data')
        # print(athlete_df)

        #make sure there is an index
        if athlete_df.index.empty:
            log.debug("DataFrame doesn't have an index.")
            # Add a default integer index
            athlete_df.reset_index(inplace=True)

        column_names_list = athlete_df.columns.tolist()
        log.debug(f'athlete_df columns: {column_names_list}')
        log.debug(f'number of rows: {len(athlete_df)}')

#        print(athlete_df[['athlete_name', 'col_timestamp_str']])

#        athlete_df = self.df[self.df['athlete_name'] == athlete]

        # summarized_df = df.groupby(['date', 'leg'])['peak_force'].max().reset_index()
        summarized_df = athlete_df.groupby(['date_str', 'leg'])['peak_torque'].agg(['max', 'mean', 'median']).reset_index()

        # pivoted_df - will pivot out each of max mean and median values
        pivoted_df = summarized_df.pivot(index='date_str', columns='leg')

        # Rename the columns to reflect the leg and the aggregation function:
        pivoted_df.columns = ['{}_{}'.format(func, leg) for leg, func in pivoted_df.columns]
        pivoted_df.reset_index(inplace=True)

        #calculate Peak and Mean Asymmetry indexes
        pivoted_df['peak_asym_index'] = pivoted_df.apply(lambda row: asym_index(row['right_max'], row['left_max'], self.injured), axis=1)
        pivoted_df['mean_asym_index'] = pivoted_df.apply(lambda row: asym_index(row['right_mean'], row['left_mean'], self.injured), axis=1)

        # Date object
        pivoted_df["datetime_object"] = pivoted_df["date_str"].apply(parser.parse)

        #print(pivoted_df)

        # ********************  Max Force Comparison graph ***********************
        line_data = [{'x': pivoted_df['datetime_object'], 'y': pivoted_df['right_max'], 'label': 'Max Force Right',
                      'color': jt_color1},
                     {'x': pivoted_df['datetime_object'], 'y': pivoted_df['left_max'], 'label': 'Max Force Left',
                      'color': jt_color2}]
        my_plot = jtpl.JT_plot('Leg Extension Peak Force Comparison', 'Date', 'Force (N)', line_data)
        my_plot.set_yminmax(0, None)
        my_plot.set_output_filepath(self.path_athlete_images + 'leg_ext_max_force_comparison_graph.png')
        self.plot_list.append(my_plot)

        # ********************  Mean Force Comparison graph ***********************
        line_data = [{'x': pivoted_df['datetime_object'], 'y': pivoted_df['right_mean'], 'label': 'Mean Force Right',
                      'color': jt_color1},
                     {'x': pivoted_df['datetime_object'], 'y': pivoted_df['left_mean'], 'label': 'Mean Force Left',
                      'color': jt_color2}]
        my_plot = jtpl.JT_plot('Leg Extension Mean Force Comparison', 'Date', 'Force (N)', line_data)
        my_plot.set_yminmax(0, None)
        my_plot.set_output_filepath(self.path_athlete_images + 'leg_ext_mean_force_comparison_graph.png')
        self.plot_list.append(my_plot)

        # ********************  Peak Asymmetry graph ***********************
        line_data = [{'x': pivoted_df['datetime_object'], 'y': pivoted_df['peak_asym_index'], 'label': 'Asymmetry Index',
                      'color': jt_color1}]
        my_plot = jtpl.JT_plot('Leg Extension Peak Asymmetry Index', 'Date', '%', line_data)
        my_plot.set_yminmax(-60, 60)
        my_plot.set_yBounds([0])
        my_plot.set_output_filepath(self.path_athlete_images + 'leg_ext_peak_asymmetry_graph.png')
        self.plot_list.append(my_plot)

        # ********************  Mean Asymmetry graph ***********************
        line_data = [{'x': pivoted_df['datetime_object'], 'y': pivoted_df['mean_asym_index'], 'label': 'Asymmetry Index',
                      'color': jt_color1}]
        my_plot = jtpl.JT_plot('Leg Extension Mean Asymmetry Index', 'Date', '%', line_data)
        my_plot.set_yminmax(-60, 60)
        my_plot.set_yBounds([0])
        my_plot.set_output_filepath(self.path_athlete_images + 'leg_ext_mean_asymmetry_graph.png')
        self.plot_list.append(my_plot)

    def jt_original_code(self, athlete_df):

        # Group data by leg and date
        grouped = athlete_df.groupby(['leg', 'date_str'])['peak_torque'].apply(list).reset_index(name='peak_torque')

        # Filter the dataframe by "leg" and create two new dataframes "self.df_right" and "self.df_left"
        athlete_df_right = athlete_df[athlete_df["leg"] == "right"].copy()
        # Reset Index for self.df_right
        athlete_df_right.reset_index(drop=True, inplace=True)

        # log.debug(f"self.df_right {self.df_right}")
        athlete_df_left = athlete_df[athlete_df["leg"] == "left"].copy()
        # Reset Index for self.df_left
        athlete_df_left.reset_index(drop=True, inplace=True)

        if athlete_df_right.index.empty:
            log.debug("DataFrame doesn't have an index.")
            # Add a default integer index
            athlete_df_right.reset_index(inplace=True)
        if athlete_df_left.index.empty:
            log.debug("DataFrame doesn't have an index.")
            # Add a default integer index
            athlete_df_left.reset_index(inplace=True)


        # Add a new 'Trial' column using apply() and f-string formatting
        athlete_df_right['trial_new'] = athlete_df_right.apply(lambda row: f'T-{row.name + 1}', axis=1)
        # log.debug(athlete_df_right)

        athlete_df_right['combine'] = athlete_df_right['leg'] + " " + athlete_df_right['trial_new']

        # Step 1: Convert 'Date' column to pandas' datetime objects
        athlete_df_right['date'] = pd.to_datetime(athlete_df_right['col_timestamp_str'])

        # Step 2: Find the latest date
        latest_date = athlete_df_right['date'].max()

        # # Step 3: Use boolean indexing to filter rows with the latest date
        latest_rows_r = athlete_df_right[athlete_df_right['date'].dt.date == latest_date.date()]
        # log.debug("latest rows r")

        # Calculate the mean of latest_rows_r
        latest_rows_r_mean = latest_rows_r.mean(numeric_only=True)
        # log.debug(f'latest_rows_r_mean {latest_rows_r_mean}')

        # Calculate the median of latest_rows_r
        latest_rows_r_median = latest_rows_r.median(numeric_only=True)
        # log.debug(f'latest_rows_r_median {latest_rows_r_median}')

        # Calculate the max of latest_rows_r
        latest_rows_r_max = latest_rows_r.max(numeric_only=True)
        # log.debug(f'latest_rows_r_max {latest_rows_r_max}')

        # Calculate the standard deviation of latest_rows_r
        latest_rows_r_std = latest_rows_r.std(numeric_only=True)
        # log.debug(f'latest_rows_r_std {latest_rows_r_std}')

        ########################################################
        # Add a new 'Trial' column using apply() and f-string formatting
        athlete_df_left['trial_new'] = athlete_df_left.apply(lambda row: f'T-{row.name + 1}', axis=1)

        # log.debug(athlete_df_left)
        athlete_df_left['combine'] = athlete_df_left['leg'] + " " + athlete_df_left['trial_new']

        # Step 1: Convert 'Date' column to pandas' datetime objects
        athlete_df_left['date'] = pd.to_datetime(athlete_df_left['col_timestamp_str'])

        # Step 2: Find the latest date
        latest_date = athlete_df_left['date'].max()

        # Step 3: Use boolean indexing to filter rows with the latest date
        latest_rows_l = athlete_df_left[athlete_df_left['date'].dt.date == latest_date.date()]
        # log.debug("latest rows L")
        # log.debug(latest_rows_l)

        # Calculate the mean of latest_rows_r
        latest_rows_l_mean = latest_rows_l.mean(numeric_only=True)
        # log.debug(f'latest_rows_l_mean {latest_rows_l_mean}')

        # Calculate the median of latest_rows_r
        latest_rows_l_median = latest_rows_l.median(numeric_only=True)
        # log.debug(f'latest_rows_l_median {latest_rows_l_median}')

        # Calculate the max of latest_rows_r
        latest_rows_l_max = latest_rows_l.max(numeric_only=True)
        # log.debug(f'latest_rows_l_max {latest_rows_l_max}')

        # Calculate the standard deviation of latest_rows_r
        latest_rows_l_std = latest_rows_l.std(numeric_only=True)
        # log.debug(f'latest_rows_l_std {latest_rows_l_std}')

        selected_rows = pd.concat([latest_rows_r, latest_rows_l])

        # Sort values by the 'Category' column
        selected_rows = selected_rows.sort_values(by='trial_new')
        # log.debug(selected_rows)

        grouped_df = selected_rows.groupby('leg')['peak_torque'].apply(list)
        # log.debug(grouped_df)

        peak_asymmetry_index = asym_index(latest_rows_r_max, latest_rows_l_max, self.injured)

        #############################
        # Create the bar chart

        plt.figure(figsize=(3, 5))
        bar_width = .4
        plt.bar(athlete_df_left['leg'], latest_rows_l_mean['peak_torque'], yerr=latest_rows_l_std['peak_torque'], capsize=5,
                color=jt_color2, width=bar_width, label='Left')
        plt.bar(athlete_df_right['leg'], latest_rows_r_mean['peak_torque'], yerr=latest_rows_r_std['peak_torque'], capsize=5,
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
        # Add a new 'Trial' column using apply() and f-string formatting
        athlete_df_right['trial_new'] = athlete_df_right.apply(lambda row: f'T-{row.name + 1}', axis=1)
        # log.debug(athlete_df_right)

        athlete_df_right['combine'] = athlete_df_right['leg'] + " " + athlete_df_right['trial_new']

        # Step 1: Convert 'Date' column to pandas' datetime objects
        athlete_df_right['date'] = pd.to_datetime(athlete_df_right['col_timestamp_str'])

        # Step 2: Find the latest date
        latest_date = athlete_df_right['date'].max()

        # # Step 3: Use boolean indexing to filter rows with the latest date
        latest_rows_r = athlete_df_right[athlete_df_right['date'].dt.date == latest_date.date()]
        # log.debug("latest rows r")

        # Calculate the mean of latest_rows_r
        latest_rows_r_mean = latest_rows_r.mean(numeric_only=True)
        # log.debug(f'latest_rows_r_mean {latest_rows_r_mean}')

        # Calculate the median of latest_rows_r
        latest_rows_r_median = latest_rows_r.median(numeric_only=True)
        # log.debug(f'latest_rows_r_median {latest_rows_r_median}')

        # Calculate the max of latest_rows_r
        latest_rows_r_max = latest_rows_r.max(numeric_only=True)
        # log.debug(f'latest_rows_r_max {latest_rows_r_max}')

        # Calculate the standard deviation of latest_rows_r
        latest_rows_r_std = latest_rows_r.std(numeric_only=True)
        # log.debug(f'latest_rows_r_std {latest_rows_r_std}')

    def calc_leg(self, leg_df):

        # Add a new 'Trial' column using apply() and f-string formatting
        leg_df['trial_new'] = leg_df.apply(lambda row: f'T-{row.name + 1}', axis=1)
        # print(leg_df)

        leg_df['combine'] = leg_df['leg'] + " " + leg_df['trial_new']

        # Step 1: Convert 'Date' column to pandas' datetime objects
        leg_df['date'] = pd.to_datetime(leg_df['col_timestamp_str'])

        # Step 2: Find the latest date
        latest_date = leg_df['date'].max()

        # # Step 3: Use boolean indexing to filter rows with the latest date
        latest_rows = leg_df[leg_df['date'].dt.date == latest_date.date()]
        # print("latest rows r")

        return(latest_rows)

    def create_pdf(self):
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
#                self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, align="C")
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
        pdf.image(self.path_athlete_images + 'leg_ext_max_force_comparison_graph.png',
                  x=x_start, y=y_start, w=image_w,
                  h=0)  # 0 for height allows image to scale, with value it will squish or fatten the image

        pdf.image(self.path_athlete_images + 'leg_ext_peak_asymmetry_graph.png',
                  x=half_pw, y=y_start, w=image_w, h=0)

        # row 2
        y_start += image_h
        pdf.image(self.path_athlete_images + 'leg_ext_mean_force_comparison_graph.png',
                  x=x_start, y=y_start, w=image_w, h=0)

        pdf.image(self.path_athlete_images + 'leg_ext_mean_asymmetry_graph.png',
                  x=half_pw, y=y_start, w=image_w, h=0)


        # save PDF File
        output_file = self.path_results_athlete + 'knee extension report.pdf'
        print(f'PDF created: {output_file}')
        # save PDF File
        pdf.output(output_file)

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


if __name__ == "__main__":

    config_obj = jtc.JT_Config('taylor performance', 'TPC', None)
    val = config_obj.validate_install()
    print('convig_obj.validate return value: {val}')

    leg_ext_analytics = JT_analytics_knee_ext_iso(config_obj, 'Isaiah Wright')

    for plot in leg_ext_analytics.plot_list:
        plot.save_to_file(True)

    leg_ext_analytics.create_pdf()

#    my_pdf = JT_analytics_knee_ext_iso(config_obj, 'dewey')
    #    my_pdf.create_athlete_pdf()