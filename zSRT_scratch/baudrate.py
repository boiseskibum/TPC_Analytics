#!/usr/bin/env python
# encode = utf-8

import sys
import time
import serial
import serial.tools.list_ports

from threading import Thread

class RawInput:

    """Gets a single character from standard input.  Does not echo to the screen."""

    def __init__(self):
        try:
            self.impl = RawInputWindows()
        except ImportError:
            self.impl = RawInputUnix()

    def __call__(self):
        return self.impl()


class RawInputUnix:

    def __init__(self):
        import tty
        import sys

    def __call__(self):
        import sys
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class RawInputWindows:

    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


class Baudrate:

    VERSION = '1.0'
    READ_TIMEOUT = 5
    BAUDRATES = [
        #			"1200",
        #			"1800",
        #			"2400",
        #			"4800",
        "9600",
        "38400",
        "19200",
        "57600",
        "74880",        #srt added in additional baud rate
        "115200",
    ]

    UPKEYS = ['u', 'U', 'A']
    DOWNKEYS = ['d', 'D', 'B']

    MIN_CHAR_COUNT = 25
    WHITESPACE = [' ', '\t', '\r', '\n']
    PUNCTUATION = ['.', ',', ':', ';', '?', '!']
    VOWELS = ['a', 'A', 'e', 'E', 'i', 'I', 'o', 'O', 'u', 'U']

    def __init__(self, port=None, threshold=MIN_CHAR_COUNT, timeout=READ_TIMEOUT, name=None, auto=True, verbose=False):
        self.port = port
        self.threshold = threshold
        self.timeout = timeout
        self.name = name
        self.auto_detect = auto
        self.verbose = verbose
        self.index = len(self.BAUDRATES) - 1
        self.valid_characters = []
        self.ctlc = False
        self.thread = None
        self.max_char_to_print = 20    # srt - maximum characters to print before bailing

        self._gen_char_list()
        print(f"vowels: {self.VOWELS}")
        print(f"punctuation: {self.PUNCTUATION}")
        print(f"VALID characters: {self.valid_characters}  END OF VALID CHARACTERS")

    def _gen_char_list(self):
        c = ' '

        while c <= '~':
            self.valid_characters.append(c)
            c = chr(ord(c) + 1)

        for c in self.WHITESPACE:
            if c not in self.valid_characters:
                self.valid_characters.append(c)

    def _print(self, data, current_count=0):
        if current_count < self.max_char_to_print:      # srt - added into to prevent writing to much junk to screen
            if self.verbose:
                sys.stderr.write(data)

    def Open(self):
        self.serial = serial.Serial(self.port, timeout=self.timeout)
        self.NextBaudrate(0)
        self.current_baudrate = self.BAUDRATES[self.index]

    def NextBaudrate(self, updn):

        self.index += updn

        if self.index >= len(self.BAUDRATES):
            self.index = 0
        elif self.index < 0:
            self.index = len(self.BAUDRATES) - 1

        sys.stderr.write(
            '\n\n@@@@@@@@@@@@@@@@@@@@@ Baudrate: %s @@@@@@@@@@@@@@@@@@@@@\n\n' % self.BAUDRATES[self.index])

        self.serial.flush()
        self.serial.baudrate = self.BAUDRATES[self.index]
        self.current_baudrate = self.BAUDRATES[self.index]
        #self.serial.flush()        # clear buffer hack below replaces this line
        self.clear_buffer_hack()

    def Detect(self):
        count = 0
        whitespace = 0
        punctuation = 0
        vowels = 0
        start_time = 0
        timed_out = False
        clear_counters = False
        all_bytes_count = 0
        bad_bytes = 0
        failed_bytes = 0

        print(f"Auto Detect: {self.auto_detect}")

        if not self.auto_detect:
            self.thread = Thread(None, self.HandleKeypress, None, (self, 1))
            self.thread.start()

        while True:
            if start_time == 0:
                start_time = time.time()

            byte = self.serial.read(1)

            if byte:
                try:
                    all_bytes_count += 1        #srt added in overall bytes count
                    character = byte.decode()

                    if (self.current_baudrate == "74880"):
                        # print(f"    character: {byte}, count: {count}" )
                        if character in self.valid_characters:
                            #print(f"               byte: {byte}, count: {count}")
                            pass
                        pass

                    if self.auto_detect and character in self.valid_characters:
                        if character in self.WHITESPACE:
                            whitespace += 1
                        elif character in self.PUNCTUATION:
                            punctuation += 1
                        elif character in self.VOWELS:
                            vowels += 1

                        count += 1
                        #  print(f"byte: {byte}, count: {count}" )
                    else:
                        bad_bytes += 1
                        clear_counters = True
                except:

                    failed_bytes += 1
                    clear_counters = True

                # srt - added in byte to string capability as well as only print so many of characters
                if (self.current_baudrate == "74880"):

#                    self._print( self.byte_to_string(byte), 0 )
#                    self._print( self.byte_to_string(byte), all_bytes_count )
                    pass

                if count >= self.threshold:
                    #print(f"  > threshold: {self.threshold}, cnt: {count}, ws: {whitespace}, p: {punctuation}, v: {vowels}" )
                    pass

                if count >= self.threshold and whitespace > 0 and punctuation > 0 and vowels > 0:
                    break
                elif (time.time() - start_time) >= self.timeout:
                    timed_out = True
            else:
                timed_out = True

            if timed_out and self.auto_detect:
                print(f" TIMED_OUT ")
                start_time = 0
                self.NextBaudrate(-1)
                clear_counters = True
                timed_out = False
                print(f" timed out - all_bytes: {all_bytes_count}, bad_bytes {bad_bytes}, %{ int(bad_bytes/all_bytes_count * 100) }, fb: {failed_bytes}")
                all_bytes_count = 0
                bad_bytes = 0

            if clear_counters:
                if (self.current_baudrate == "74880"):
                    #print(f" clear counters -cnt: {count}, bb: {bad_bytes}, ws: {whitespace}, p: {punctuation}, v: {vowels}")
                    pass
                whitespace = 0
                punctuation = 0
                vowels = 0
                count = 0
                clear_counters = False

            if self.ctlc:
                break

        self._print("\n")
        return self.BAUDRATES[self.index]

    def HandleKeypress(self, *args):
        userinput = RawInput()

        while not self.ctlc:
            c = userinput()
            if c in self.UPKEYS:
                self.NextBaudrate(1)
            elif c in self.DOWNKEYS:
                self.NextBaudrate(-1)
            elif c == '\x03':
                self.ctlc = True

    def MinicomConfig(self, name=None):
        success = True

        if name is None:
            name = self.name

        config = "########################################################################\n"
        config += "# Minicom configuration file - use \"minicom -s\" to change parameters.\n"
        config += "pu port             %s\n" % self.port
        config += "pu baudrate         %s\n" % self.BAUDRATES[self.index]
        config += "pu bits             8\n"
        config += "pu parity           N\n"
        config += "pu stopbits         1\n"
        config += "pu rtscts           No\n"
        config += "########################################################################\n"
        print(f'{config}')
        

        return (success, config)

    def Close(self):
        self.ctlc = True
        self.serial.close()


    # srt - fixes byte code that is bad and returns as a string
    def byte_to_string(self, byte):
        try:
            # Try to decode the byte as a string
            string = byte.decode()
        except UnicodeDecodeError:
            # If decoding fails, convert the numeric value to a string
            string = str(byte) + " "

        return string

    def clear_buffer_hack(self):

        #I a not sure the next two lines help at all as I question flushInput() and whether or not it works but what the hell.
        self.serial.flushInput()
#        self.serial_port.reset_input_buffer()
        time.sleep(0.1)  # Add a small delay

        max_reads = 10000

        i = 0
        elapsed = 0
        #Comments.   should not have data a more than 100hz which means .001 is way under how often we should see data
        # so assume those points are all buffered up and therefore can be thrown away.   hence this is called a hack!
        very_start = time.time()
        while elapsed < .01 and i < max_reads:
            start = time.time()
            self.serial.read()
            i += 1
            end = time.time()
            elapsed = end - start

        elapsed_str = "{:.6f}".format(elapsed)
        very_elapsed = end - very_start
        very_elapsed_str = "{:.6f}".format(very_elapsed)


        if i == max_reads:
            print(f"MAX READS in clear_buffer_hack. count: {i} complete time: {very_elapsed_str}, last elapsed: {elapsed_str} ")
        else:
            print(f"CLEARED clear_buffer_hack. count: {i} complete time: {very_elapsed_str}, last elapsed: {elapsed_str}")


if __name__ == '__main__':

    import subprocess
    from getopt import getopt as GetOpt, GetoptError

    def usage():
        baud = Baudrate()

        print ("")
        print ("Baudrate v%s" % baud.VERSION)
        print ("Craig Heffner, http://www.devttys0.com")
        print ("")
        print ("Usage: %s [OPTIONS]" % sys.argv[0])
        print ("")
        print ("\t-p <serial port>       Specify the serial port to use [/dev/ttyUSB0]")
        print ("\t-t <seconds>           Set the timeout period used when switching baudrates in auto detect mode [%d]" % baud.READ_TIMEOUT)
        print ("\t-c <num>               Set the minimum ASCII character threshold used during auto detect mode [%d]" % baud.MIN_CHAR_COUNT)
        print ("\t-n <name>              Save the resulting serial configuration as <name> and automatically invoke minicom (implies -a)")
        print ("\t-a                     Enable auto detect mode")
        print ("\t-b                     Display supported baud rates and exit")
        print ("\t-q                     Do not display data read from the serial port")
        print ("\t-h                     Display help")
        print ("")
        sys.exit(1)

def check_port(port):
    display = False      #changed from False to True
    verbose = True      # made false
    auto = True         # srt made true
    run = True          # srt made true
    threshold = 25
    timeout = 5         #srt - changed timeout to 2 seconds from 5
    name = None


    try:
        (opts, args) = GetOpt(sys.argv[1:], 'p:t:c:n:abqh')
    except (GetoptError, e):
        print (e)
        usage()

    for opt, arg in opts:
        if opt == '-t':
            timeout = int(arg)
        elif opt == '-c':
            threshold = int(arg)
        elif opt == '-p':
            port = arg
        elif opt == '-n':
            name = arg
            auto = True
            run = True
        elif opt == '-a':
            auto = True
        elif opt == '-b':
            display = True
        elif opt == '-q':
            verbose = False
        else:
            usage()

    baud = Baudrate(port, threshold=threshold,
                    timeout=timeout, name=name, verbose=verbose, auto=auto)

    if display:
        print ("")
        for rate in baud.BAUDRATES:
            print ("\t%s" % rate)
        print ("")
    else:
        print ("")
        print ("Starting baudrate detection on %s, turn on your serial device now." % port)
        print ("Press Ctl+C to quit.")
        print ("")

        baud.Open()

        try:
            rate = baud.Detect()
            print ("\nDetected baudrate: %s" % rate)

            if name is None:
                print ("\nSave minicom configuration as: ",
                name = sys.stdin.readline().strip())
                print ("")

            (ok, config) = baud.MinicomConfig(name)
            if name and name is not None:
                if ok:
                    if not run:
                        print ("Configuration saved. Run minicom now [n/Y]? ",
                        yn = sys.stdin.readline().strip())
                        print ("")
                        if yn == "" or yn.lower().startswith('y'):
                            run = True

                    if run:
                        subprocess.call(["minicom", name])
                else:
                    print (config)
            else:
                print (config)
        except KeyboardInterrupt:
            pass

        baud.Close()

def main():

    available_ports = list(serial.tools.list_ports.comports())

    if not available_ports:
        print("No serial ports found!")
    else:
        # Print the list of available serial ports
        for port in available_ports:
            print(port.device)
            check_port(port.device)

main()
