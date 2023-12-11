# jt_pdf_.py
# purpose: create pdf with graphs 2 across

# Import necessary modules
import os, time
from datetime import date

from fpdf import FPDF
from PyQt6.QtWidgets import QProgressDialog
from PyQt6 import QtCore, QtWidgets


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

class JT_PDF_2_across:
    def __init__(self, config_obj, athlete, protocol_title, report_author, output_file):

        self.config_obj = config_obj
        self.athlete = athlete
        self.output_file = output_file
        self.title = protocol_title
        self.report_author = report_author

    def add_plots_and_create_pdf(self, plots, my_pyqt_app = None):
        self.plots = plots

        today_date = date.today()

        logo = self.config_obj.get_img_path() + "jt.png"
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
        title = self.title
        report_author = self.report_author

        class PDF(FPDF):
            def __init__(self):
                super().__init__()
                self.alias_nb_pages()  # Initialize the alias for total number of pages

            def header(self):
                # Rendering logo:
                if logo is not None:
                    self.image(logo, 10, 8, 12)  # last parameter - "12" is how to change the size
                # Setting font: helvetica bold
                self.set_font("helvetica", "B", 12)
                # Moving cursor to the right:
                self.cell(pw / 2 - 20)  # the 20 is a fudge factor to account for the logo
                # Printing title:
                self.cell(30, 10, f"{title} Assessment:  " + athlete_name, align="C")
                # Performing a line break:

            def footer(self):

                # Position cursor at 1.5 cm from bottom:
                self.set_y(-15)
                # Setting font: helvetica italic 8
                self.set_font("helvetica", "I", 8)

                # Widths for the cells
                page_width = 210  # or self.epw for the effective page width
                page_width = 190
                name_width = 60
                date_width = 40
                page_number_width = page_width - (name_width + date_width)

                # Printing 'Taylor Performance Consulting' on the left
                self.set_x(10)  # Adjust the X position as needed
                self.cell(name_width, 10, report_author, 0, 0, "L")

                # Printing page number in the center
                self.set_x(10 + name_width)  # Position to the right of the name cell
                self.cell(page_number_width, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")

                # Printing date on the right
                formatted_date = today_date.strftime("%m-%d-%Y")
                self.set_x(10 + name_width + page_number_width)  # Position to the right of the page number cell
                self.cell(date_width, 10, f"{formatted_date}", 0, 0, "R")

        plot_num = 1
        total_plots = len(plots)
        row = 1

        if my_pyqt_app is not None:
            my_progressDialog = QProgressDialog("Processing graph...", "cancel", 0, total_plots, my_pyqt_app)
            my_progressDialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
            QtWidgets.QApplication.processEvents()  # Process events to update the UI
            time.sleep(1)  # delay a moment

        ### create PDF
        pdf = PDF()
        pdf.add_page()
        pdf.set_font('Helvetica', '', 10)

        # constant for half way across the page (2 columns)
        half_pw = 100 + 15
        x_start = 20
        master_y_start_master = 30
        y_start = master_y_start_master

        # set image width and height between graphs
        image_w = 70
        image_h = 62

#        total_plots = 3   # allows me to shorten the list so I don't have to wait while debugging
        for plot in plots[:total_plots]:

            filepath = plot.save_plot_to_file()

            # odd plot #
            if plot_num % 2 != 0:
                pdf.image(filepath, x=x_start, y=y_start, w=image_w, h=0)
                # 0 for height allows image to scale, with value it will squish or fatten the image

            # even plot #
            else:
                pdf.image(filepath, x=half_pw, y=y_start, w=image_w, h=0)
                y_start += image_h
                row += 1

            #update progress on number of plots complete
            if my_pyqt_app is not None:
                my_progressDialog.setValue(plot_num)
                str = f"Processing graph {plot_num}/{total_plots}"
                my_progressDialog.setLabelText(str)
#                print(f'***{str}')
                QtWidgets.QApplication.processEvents()  # Process events to update the UI
                if total_plots < 15:
                    time.sleep(.1)  # Simulate file processing time

            plot_num += 1

            # add a new page if the 8th graph has been shown
            if (plot_num - 1) % 8 == 0:
                pdf.add_page()
                y_start = master_y_start_master
                row = 1

        if my_pyqt_app is not None:
            my_progressDialog.setValue(total_plots)  # Ensure the progress bar reaches 100%
            my_progressDialog.setLabelText(f"Processing graph {plot_num}/{total_plots}")
            QtWidgets.QApplication.processEvents()  # Process events to update the UI
            time.sleep(2)  # Simulate file processing time

        # save PDF File
        try:
            pdf.output(self.output_file)
            log.info(f'saved PDF file: {self.output_file}')
        except:
            log.error((f'Could not save PDF file: {self.output_file}'))

        return self.output_file

if __name__ == "__main__":

    # set base and application path
    config_obj = jtc.JT_Config('taylor performance', 'TPC', None)
    config_obj.validate_install()

    output_file = 'testing/jt_pdf_2_across.pdf'
#    plots = jtpl.test_plots(17)
    plots = jtpl.test_plots(2)
    pdf_obj = JT_PDF_2_across(config_obj, "Carl Lewis", "BIG TIME", "Luke, I am your father", output_file)
    pdf_obj.add_plots_and_create_pdf(plots)
