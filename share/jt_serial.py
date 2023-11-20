import serial
import serial.tools.list_ports
import pandas as pd
import json
import time
import threading

import tkinter as tk

try:
    from . import jt_util as util
except:
    import jt_util as util

default_baud_rate = 115200

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()


class SerialDataReader(threading.Thread):
    def __init__(self):
        super().__init__()
        self.baud_rate = 115200
        self.port_name = None

        self.recorded_data = []
        self.serial_port = None

        self.error_str = ""
        self.num_line_errors = 0
        self.initial_wait = .5   #number of seconds to wait after configuring the serial port before reading allowing it to be read from
        self.debug_mode = False

    #### gets list of port names
    def get_available_ports(self):
        devices = []

        # Get a list of available serial ports
        available_ports = list(serial.tools.list_ports.comports())

        for port in available_ports:
            # eliminate any ports that contain the value below.  In this case I don't want to show Bluetooth ports

            if "usbserial" in port.device:  # handles MacOS case
                devices.append(port.device)
            elif "COM" in port.device:      # handles Microsoft Windows case
                devices.append(port.device)

        if len(devices) < 1:
            self.error_str = "No serial ports found!"

        return devices

    #### validates port name
    def valid_port_name(self, port_name):
        ports = self.get_available_ports()
        if port_name in ports:
            return True
        else:
            return False

    #### set up port - timeout defaults to 1 second
    def configure_serial_port(self, port, baud_rate=default_baud_rate):
        self.baud_rate = baud_rate
        self.port_name = port
        my_return = False

        log.f(f"Attempting connection to port: {self.port_name}")

        try:

            if self.port_name == None:
                my_return = False
                log.debug(f"Serial port name is None")
            elif self.serial_port == None:


                # timeout after 1 second if nothing is
                self.serial_port = serial.Serial(port=self.port_name, baudrate=self.baud_rate)
#                self.serial_port = serial.Serial(port=self.port_name, baudrate=self.baud_rate, timeout=my_timeout)

                #sleep for a moment and give a chance for the serial port to gets its brains
                time.sleep(self.initial_wait)

                if self.serial_port.isOpen() == True:
                    log.info(f"Successfully connected to port {self.port_name}, OID: = {self.serial_port}")
                    my_return = True
                else:
                    log.error(f"Failed to connected to port |{self.port_name}|, OID: = {self.serial_port}")
            else:  #
                if self.serial_port.isOpen():
                    log.debug(f"Serial Port: {self.port_name} is already open")
                    my_return = True

        except:
            log.error(f"Could not connect to port: |{self.port_name}| Baud: {self.baud_rate}, OID: = {self.serial_port}")
            self.serial_port = None

        return my_return

    # validate if serial port is getting any sorts of data
    def test_serial_port(self):

        log.f()
        if self.serial_port:
            try:

                #flush port and read the first 2 lines
                self.serial_port.flushInput()
                self.serial_port.readline().decode('utf-8').strip()
                line = self.serial_port.readline().decode('utf-8').strip()

                if line:
                    log.debug(f"Data received from serial port: {line}")
                    return True
                else:
                    self.error_str = f"No data received from serial port."
                    log.debug(self.error_str)

            except serial.SerialException:
                self.error_str = f"Error reading from serial port. {self.port_name}"
                log.debug(self.error_str)

        log.debug(f"could not connect to serial port, try and configure the serial port")
        return False


    #validates that a port has the required portion of the string contained in a line such as 's1' or 's2'
    def serial_port_validate_data(self, required_str):

        line = ""

        if self.serial_port == None:
            return False, line

        if self.serial_port == None:
            return False, "Serial Port NOT configured"

        line = "n/a"
        log.f(f"Validate data from port: {self.port_name}")
        try:

            #read first line and flush it
            self.serial_port.flushInput()
            self.serial_port.readline().decode('utf-8').strip()

            # Read incoming lines
            i = 0
            while i < 2:
                self.serial_port.timeout = 1
                line = self.serial_port.readline().decode('utf-8').strip()
                i += 1

                # Check if the line contains 's1'
                if required_str in line:
                    if i < 2:
                        log.debug(f"Activity detected on: {self.port_name} and found required str: {required_str}  #:{i}  {line}")

                    return True, line

        except (OSError, serial.SerialException):
            # Error occurred while reading from the port
            log.error(f"Failed to validate data from port: {self.port_name}")

        return False, line

    #### Getting data ###########################################################
    #### start_reading
    def start_reading(self):

        if self.serial_port == None:
            self.error_str = f"Start_reading - Serial port not configured: {self.port_name}"
            log.debug(self.error_str)
            return False

        # start timer, this sets a flag that it is in "threading mode"
        self.start_time = time.time()
        self._stop_flag = threading.Event()
        threading.Thread(target=self.record_data).start()

    # Function that will be its own thread pulling in data when collection is started
    def record_data(self):

        self.recorded_data = []
        self.lines_recorded = 0
        self.num_line_errors = 0
        self.running = True

        self.clear_buffer_hack()
#        self.serial_port.flushInput()
#        time.sleep(0.1)  # Add a small delay
#        self.serial_port.read_all()
#       self.serial_port.readline().decode('utf-8').strip()

        # read first line and flush it
        try:
            line = self.serial_port.readline().decode('utf-8').strip()
        except:
            print(f"ERROR reading from Serial port ---   Discard ROW")

        while not self._stop_flag.is_set() and self.running == True:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    #log.debug(f"start reading line: {line}")
                    self._process_line(line)
                    self.lines_recorded += 1

            except serial.SerialException:
                self.error_str = f"Error reading from serial port: {self.port_name}, lines_recorded: {self.lines_recorded} "
                log.debug(self.error_str)
                return False

        log.debug(f"record_data, lines_recorded: {self.lines_recorded}")


    #### stop_reading, returns the number of rows read in
    def stop_reading(self):

        if self.serial_port == None:
            self.error_str = f"Stop_reading - Serial port not configured: {self.port_name}"
            log.debug(self.error_str)
            return 0

        end_time = time.time()
        self.elapsed_time = end_time - self.start_time
        formatted_duration = "{:.3f}".format(self.elapsed_time)
        lps = "{:.2f}".format( len(self.recorded_data)/self.elapsed_time )

        if (self.debug_mode == True):
            log.f(f"lines/sec: {lps}, Elapsed time: {formatted_duration} secs, #lines: {len(self.recorded_data)},  errors: {self.num_line_errors}")

        # this turns the flag off for the thread which ends the data_record
        self._stop_flag.set()
        self.running = False

        return len( self.recorded_data)

    #### read_lines
    def read_lines(self, num_lines):

        try:
            self.recorded_data = []
            self.lines_recorded = 0
            self.num_line_errors = 0
            if self.serial_port == None:
                self.error_str = f"read_lines - Serial port not configured: {self.port_name}"
                log.debug(self.error_str)
                return False

            self.clear_buffer_hack()

            self.serial_port.readline().decode('utf-8').strip()

            # get time of start of reading
            self.start_time = time.time()

            for _ in range(num_lines):
                print_head_tail = False   # for debugging and printing out
                try:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    if print_head_tail and (self.lines_recorded < 2 or self.lines_recorded > num_lines - 3):
                        print(f"       {self.lines_recorded}:, {line}")
                    if line:
                        self._process_line(line)
                        self.lines_recorded += 1

                except serial.SerialException:
                    log.debug("Error reading from serial port.")
                    return False

            end_time = time.time()
            self.elapsed_time = end_time - self.start_time
            formatted_duration = "{:.3f}".format(self.elapsed_time)
            j = len(self.recorded_data)
            lps = "{:.2f}".format( j/self.elapsed_time )
            avg = "{:.3f}".format( self.elapsed_time/j )
            if self.debug_mode == True:
                log.f(f"lines/sec: {lps},  avgtime: {avg}, num_lines: {j}, Elapsed time: {formatted_duration} secs, #lines: {j}, errors: {self.num_line_errors}")
        except:
            return False

        return True

    # hack to clear the buffer because self.serial_port.flushInput(), read_all(), and time.sleep(0.1) DO NOT work
    def clear_buffer_hack(self):

        #I a not sure the next two lines help at all as I question flushInput() and whether or not it works but what the hell.
        self.serial_port.flushInput()
#        self.serial_port.reset_input_buffer()
        time.sleep(0.1)  # Add a small delay

        max_reads = 1000

        i = 0
        elapsed = 0
        #Comments.   should not have data a more than 100hz which means .001 is way under how often we should see data
        # so assume those points are all buffered up and therefore can be thrown away.   hence this is called a hack!
        very_start = time.time()
        while elapsed < .003 and i < max_reads:
            start = time.time()
            self.serial_port.readline().decode('utf-8').strip()
            i += 1
            end = time.time()
            elapsed = end - start

        elapsed_str = "{:.6f}".format(elapsed)
        very_elapsed = end - very_start
        very_elapsed_str = "{:.6f}".format(very_elapsed)

        if self.debug_mode == True:
            if i == max_reads:
                log.debug(f"MAX READS in clear_buffer_hack. count: {i} complete time: {very_elapsed_str}, last elapsed: {elapsed_str} ")
            else:
                log.debug(f"CLEARED clear_buffer_hack. count: {i} complete time: {very_elapsed_str}, last elapsed: {elapsed_str}")


    # returns a completed dataframe, cleaned up, with KG, and with athlete/protocol added if provided
    def get_data_df(self, l_zero=0, l_mult=1, r_zero=0, r_mult=1, athlete='na', protocol_name='na', protocol_type='double', leg='both'):

        df = pd.DataFrame()
        #make sure there is some recorded data
        if self.recorded_data == None or len(self.recorded_data) < 1:
            log.f("No Recorded Data")
            return(df)

        my_data = self._process_and_smooth_data(l_zero, l_mult, r_zero, r_mult, athlete, protocol_name, protocol_type, leg)
        #log.debug(my_data[0])

        if protocol_type == 'single':
            my_columns = ["Timestamp", "s1", "s2", "s1_clean", "s2_clean", "force_lbs", "force_N", "athletes_name", "protocol_name", "protocol_type", "leg", "elapsed_time_sec"]
        else:
            my_columns = ["Timestamp", "s1", "s2", "s1_clean", "s2_clean", "l_force_lbs", "l_force_N", "r_force_lbs", "r_force_N", "athletes_name", "protocol_name", "protocol_type", "leg", "elapsed_time_sec"]
        my_df = pd.DataFrame(my_data, columns=my_columns)
        #log.debug(df)

        return (my_df)

    def set_test_data_list(self, list):
        self.recorded_data = list

    #### Internal only #####################################################
    #utilized to process a given line utilizing expected s1 and s2 style format
    def _process_line(self, line):
        try:
            #log.f(f"line: {line}")
            data = json.loads(line)
            s1 = data['s1']
            s2 = data['s2']
            timestamp = time.time()
            row = [timestamp, s1, s2]
 #           log.debug(f"_process_line row: {row}")
            self.recorded_data.append(row)

        except json.JSONDecodeError:
            self.num_line_errors +=1
            log.error(f"Invalid JSON data, error# {self.num_line_errors} line: {line}")


    def _process_and_smooth_data(self, l_zero, l_mult, r_zero, r_mult, athlete, protocol_name, protocol_type, leg):
        # this function filters down values based upon the following rules
        #       replaces -4000000's with with prior good values or if necessary the next good value
        #       replaces -101 values with prior good values or if necessary the next good value

        # Column definitions
        # 0 - timestamp
        # 1 - s1
        # 2 - s2
        # 3 - s1_cleaned
        # 4 - s1_cleaned
        # 5 - l_force_kg
        # 6 - r_force_kg
        # 7 - athlete
        # 8 - protocol

        #log.f()
        #make sure there is some recorded data
        if len( self.recorded_data ) < 1:
            log.debug("No Recorded Data Rows")
            return([])

        #get column from within a list. creates a new list with just values in the columnn
        def get_column(data, column_index):
            return [ row[column_index] for row in data ]

        my_list = list( self.recorded_data )

        ###  S1 ###
        # get column s1 and clean it
        col = get_column(my_list, 1)
        clean_col = _clean_column_values(col)
#        log.debug(f"s1: {col}")
#        log.debug(f"s1 clean: {clean_col}")

        #add clean column to existing list (column 3)
        for i in range( len(my_list) ):
            my_list[i].append( clean_col[i] )

        ###  S2 ###
        # get column s2 and clean it
        col = get_column(my_list, 2)
        clean_col = _clean_column_values(col)

        #add clean column to existing list (column 4)
        for i in range( len(my_list) ):
            my_list[i].append( clean_col[i] )

        start_time = my_list[0][0]
        # add kg and lbs columns
        for row in my_list:

            s1_cleaned = row[3]
            s2_cleaned = row[4]

            # left hand side forces
            l_force_lbs = self.get_force_lbs(s1_cleaned, l_zero, l_mult)
            l_force_N = self.get_force_N(s1_cleaned, l_zero, l_mult)

            # right hand side forces
            r_force_lbs = self.get_force_lbs(s2_cleaned, r_zero, r_mult)
            r_force_N = self.get_force_N(s2_cleaned, r_zero, r_mult)
            elapsed = row[0] - start_time

            row.append(l_force_lbs)
            row.append(l_force_N)

            # if double protocol append the s2 forces (or right)
            if protocol_type == "double":
                row.append(r_force_lbs)
                row.append(r_force_N)

            row.append(athlete)
            row.append(protocol_name)
            row.append(protocol_type)
            row.append(leg)
            row.append(elapsed)

        #log.debug(f"fixed up list: {my_list[0]}")

        return my_list


    # get weight in lbs (multiplier was calibrated in lbs
    def get_force_lbs(self, reading, zero, multiplier):

        if multiplier != 0:
            force = (reading - zero) / multiplier

        return force

    # get weight in N (multiplier was calibrated in lbs so must go to kg and then to N)
    def get_force_N(self, reading, zero, multiplier):

        lbs_to_N = 1 / 2.0462 * 9.81 # converstion factor from lbs to kg (multiply lbs by this to get kg)
        force = -101 # default value if for some reason multiplier is equal to zero (divide by zero)
        if multiplier != 0:
            force = (reading - zero) / multiplier * lbs_to_N

        return force

# this function receives in a column full of readings and cleans them up based upon the rules specified
def _clean_column_values2(column):
    ugly_value = -4000000
    ugly2_value = 4000000

    for i in range(len(column)):
        if column[i] == -101  or column[i] == -1 or column[i] < ugly_value or column[i]> ugly2_value:
            if i > 0:
                column[i] = column[i - 1]
            else:   # handle the case at the beginning of a string  - ie find the first non error value but don't try
                    # more than 10 spots out
                k_max= 10
                if len(column) < 10:
                    k_max = len(column)
                for j in range(i, k_max):
                    if column[j] != -101 and column[j] > ugly_value and column[j] < ugly2_value:
                        column[i] = column[j]
                        break
    return column

def _clean_column_values(column):
    ugly_value = -4000000
    ugly2_value = 4000000

    for i in range(len(column)):
        if column[i] == -101  or column[i] == -1 or column[i] < ugly_value or column[i]> ugly2_value:

            # normal case for values in the middle we do linear interpolation starting 2 back from error and looking 2 forward from error
            if i > 1 and i < len(column) - 3:
                start = column[i - 2]
                end = column[i + 2]
                column[i-1] = linear_interpolation(start, end, .25)
                column[i] = linear_interpolation(start, end, .5)
                column[i+1] = linear_interpolation(start, end, .75)

            # handle the case at the beginning (first 2 value) - ie find the first non error value but don't try beyond that
            elif i < 2:
                k_max= 10
                if len(column) < 10:
                    k_max = len(column)
                for j in range(i, k_max):
                    if column[j] != -101 and column[j] > ugly_value and column[j] < ugly2_value:
                        column[i] = column[j]
                        break
            # handle end of string case.  if in the last 3 spots just fill it in with the prior values.
            elif i >= len(column) - 3:
                for j in range(i, len(column)):
                    column[j] = column[i-1]

    return column
def linear_interpolation(start_value, end_value, fraction):
    # Perform linear interpolation between start_value and end_value.
    # The fraction indicates the position between the two values (0.0 to 1.0).
    # Returns the interpolated value as an integer.

    interpolated_value = int(start_value + fraction * (end_value - start_value))
    return interpolated_value


#### Main ##########################################################

if __name__ == "__main__":
    reader = SerialDataReader()

    #puts out more data
    reader.debug_mode = True

    #test the smoothing algorithms
    test_data = [-101, -101, -101, -4444444, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, -101, 4444444]
    new_data = _clean_column_values(test_data)
    print(f"{test_data}\n{new_data}\n")

    test_data = [1, -101, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, -101]
    new_data = _clean_column_values(test_data)
    print(f"{test_data}\n{new_data}\n")

    test_data = [1, 2, 3, 1, -101, 5, 7, 8, 9, 10, 11, 2, -101, 14, 15, 16, -101, -101, -101, 19, 20, 21, 22, 23]
    new_data = _clean_column_values(test_data)
    print(f"{test_data}\n{new_data}\n")

    # Configure and test the serial port
    port = '/dev/cu.usbserial-02897983'
    port = 'COM4'

    baud = 115200

    # if only one port available then attempt to connect to it
    ports = reader.get_available_ports()
    if len(ports) == 1:
        port = ports[0]
        log.debug(f"Only one port available, setting port to: {port}, baud {baud}")

        #attempt to connect to port
        reader.configure_serial_port( port, baud )

    def main():
        app.title('Dialog')

        string_button = tk.Button(app, text='Show ports', width=25, command=show_ports)
        string_button.pack()

        string_button = tk.Button(app, text='Configure port', width=25, command=configure_port)
        string_button.pack()

        string_button = tk.Button(app, text='Test port', width=25, command=test_port)
        string_button.pack()

        string_button = tk.Button(app, text='Validate data', width=25, command=test_validate_data)
        string_button.pack()

        string_button = tk.Button(app, text='test read_lines', width=25, command=read_lines)
        string_button.pack()

        string_button = tk.Button(app, text='test read/stop', width=25, command=test_read_stop)
        string_button.pack()

        string_button = tk.Button(app, text='Start Reading', width=25, command=start_reading)
        string_button.pack()

        string_button = tk.Button(app, text='Stop Reading', width=25, command=stop_reading)
        string_button.pack()

        string_button = tk.Button(app, text='Test Combo Read', width=25, command=test_combo_read)
        string_button.pack()

        string_button = tk.Button(app, text='Print dataframe', width=25, command=print_df)
        string_button.pack()

        exit_button = tk.Button(app, text='App Close', width=25, command=app.destroy)
        exit_button.pack()

        app.mainloop()

    def show_ports():
        available_ports = reader.get_available_ports()
        log.f(f"Available serial ports:")
        if len(available_ports) < 1 :
            log.info(f"\nNo Ports available")
        else:
            i=1
            for string in available_ports:
                print(f"    port{i}: {string}")
                i += 1
            print("\n")

    def configure_port():
        log.f(f"Configure Port: {port}")
        result = reader.configure_serial_port(port, baud)
        log.f(f"Result: {result}\n")

    def test_port():
        log.f(f"Test Serial Port: {port}")
        result = reader.test_serial_port()
        log.f(f"Result: {result}\n")

    def test_validate_data():
        log.f(f"Serial_port_validate_data: {port}")
        result, line = reader.serial_port_validate_data('s2')
        log.f(f"Result: {result}, line: {line}\n")

    def read_lines():
        # Read a specific number of lines
        sleep = 1
        for i in range(5):
            num_lines = 100
            print(" ")
            log.f(f"Read lines: {num_lines}, sleep: {sleep}")
            result = reader.read_lines(num_lines)
            print_df()
            time.sleep(sleep)
            sleep += 1

    def test_read_stop():

        # Read for a specific number of seconds
        secs = 3
        for i in range(5):
            log.f(f"Test Read/Stop: {secs}  secs")
            reader.start_reading()

            time.sleep(secs)
            result = reader.stop_reading()

            log.f(f"Read_lines Result: {result}\n")
            time.sleep(1)


    def start_reading():
        #Start reading continuously
        log.f("Start Reading")
        reader.start_reading()

    def stop_reading():
        # Stop reading
        num_rows = reader.stop_reading()
        log.f(f"Stopped Reading, number of rows read in is: {num_rows}")
        print_df()
        print("\n")

    def test_combo_read():

        print("---------------------------------------------------------------")
        #empty queue hopefully with readlines
        result = reader.read_lines(200)
        log.f(f"Read_lines Result: {result}\n")

        # Read for a specific number of seconds
        secs = 4
        for i in range(10):
            log.f(f"Test Read/Stop: {secs}  secs")
            reader.start_reading()

            time.sleep(secs)
            result = reader.stop_reading()

            log.f(f"Read_lines Result: {result}\n")
            time.sleep(1)

    def print_df():

        #HACK - passes in l_zero, l_mult, r_zero, r_mult, athlete, protocol
        data_frame = reader.get_data_df(10, 1, 100, -1, "joe", "my_prot")
        log.f(f"df[0] - s1: {data_frame.iloc[0]['s1']} s2: {data_frame.iloc[0]['s2']}")

    app = tk.Tk()

    main()


