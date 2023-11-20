# jt_pdf_.py
# purpose: create pdf with graphs 2 across

# Import necessary modules
import os
from datetime import date

try:
    from . import jt_util as util
except:
    import jt_util as util

my_resources = 'resources/img/'

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

|class JT_PDF_2_across:
    def __init__(self, config_obj, athlete):

        self.config_obj = config_obj
        self.athlete = athlete


    def add_plots(self, plots):
        self.plots = plots

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