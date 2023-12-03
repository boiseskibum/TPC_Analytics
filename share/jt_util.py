# -*- coding: utf-8 -*-
"""jt_util.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11FFJ6P5Dj1NEe_jds0E6vbS_8PX1I9P7
"""

####  jt_util provides general utilities and logging capability for a program
#
# jt_logging:       class to enable logging/debugging capability
# jt_path_base():   get the base path for code for Google Collab, MacOS, Windows
# jt_whoami():      returns the function name that the code is in

import inspect
import datetime
import platform
import os, sys, subprocess

# This is a class to be utilized locally to hold a string buffer.  This is utilized to temporarily hold
# strings before the path is known to store information to log files
class StringBuffer:
    def __init__(self, max_size=1000):
        self.buffer = []
        self.max_size = max_size

    def add(self, string):
        if len(self.buffer) >= self.max_size:
            self.buffer.pop(0)  # Remove the oldest entry
        self.buffer.append(string)

    def get_all(self):
        return self.buffer

#############################################
# jt_logging class
#
# this class is a Singleton.  IE, it will only be created once for a given Notebook/program
#############################################

logging_levels = { 
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
    }

class jt_logging(object):
    __instance = None
    log_path = None
    log_prefix = None
    start_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_handle = None
    prefix = ''
    temp_buffer = None
    level_str = "INFO"
    level = logging_levels[level_str]

    def __new__(cls, *args, **kwargs):
        if not jt_logging.__instance:
            jt_logging.__instance = object.__new__(cls)
 
        return jt_logging.__instance

    def __init__(self):
        pass

    #### PUBLIC Functions  ####

    #return logging level
    def get_level(self):
        return(self.level_str)

    #return if in debug mode
    def if_debug(self):
        if self.level_str == "DEBUG":
            return True
        else:
            return False

      #prints out the stack if logging_levels is less than or equal to INFO
    def f(self, msg = "", log_regardless = "FALSE"):
        whoiam = jt_whoami(1)
        if self.level <= logging_levels["INFO"] or log_regardless != "FALSE":
            self.print(msg, 1, True)
        return(whoiam)

    def set_logging_level(self, new_level): 
        if logging_levels.get(new_level):
            self.level_str = new_level
            self.level = logging_levels[new_level]  
        else:
            error_str = f"LOGGING LEVEL INVALID: {new_level}  Valid levels: {list(logging_levels.keys())}"
            print(error_str)  
            self.print_to_file(error_str)
        return(self.level_str)

      # set up logging to the file system, if not called it doesn't run
    def set_log_file(self, path, prefix): 
        self.log_path = path
        self.log_prefix = prefix

        # if using buffer, iterate through strings in buffer sending them to the log file.  After doing so
        # then eliminate the buffer and in the future srings will go directly there
        if self.temp_buffer is not None:
            buff = self.temp_buffer.get_all()
            print(f'***** len buff: {len(buff)}')
            for str in buff:
                self.print_to_file(str)
            self.temp_buffer = None

    # this function is utilized to turn buffering on until at which point the set_log_file function can
    # be called with the path information which is unknown on application startup.
    def set_temp_startup_buffering(self):
        self.temp_buffer = StringBuffer()

    #outputs message regardless
    def msg(self, msg = ""):
        self.print(": " + msg, 1)

    def debug(self, msg = ""):
        if self.level <= logging_levels["DEBUG"]:
            output_str = "DEBUG: " + msg
            self.print(output_str, 1)

    def info(self, msg= ""):
        if self.level <= logging_levels["INFO"]:
            output_str = "INFO: " + msg
            self.print(output_str, 1)

    def warning(self, msg = ""):
        if self.level <= logging_levels["WARNING"]:
            output_str = "WARNING: " + msg
            self.print(output_str, 1)

    def error(self, msg = ""):
        if self.level <= logging_levels["ERROR"]:
            output_str = "ERROR: " + msg
            self.print(output_str, 1)

    def critical(self, msg = ""):
        if self.level <= logging_levels["CRITICAL"]:
            output_str = "CRITICAL: " + msg
            self.print(output_str, 1)

    ## The PRIVATE functions below are for internal use only
    def print(self, output_str = "", indentation_subtraction = 0, include_stack = False):
        #output_str is any string to print out.  For the user of this
        #indentation_subtraction is for internal use only. speficially the f function
        indentation_block = ".  "
        indentation_str = ""

        wholeStack = inspect.stack()
        stack_str = jt_stack_str(wholeStack)
        num_functions_deep = jt_num_functions_deep(wholeStack)

        #create spacing (tabs going over)
        x = 1 + indentation_subtraction
        while x < num_functions_deep:
          indentation_str = indentation_str + indentation_block
          x += 1

        # if including stack prefix it to output String
        if( include_stack == True ):
          output_str = stack_str + "  " + output_str

        output_str = indentation_str + output_str

        if self.temp_buffer is not None:
            self.temp_buffer.add(output_str)

        #write to log file if set up
        self.print_to_file(output_str)

        #write to screen
        print(f"{self.prefix}{output_str}")

        return output_str

    def print_to_file(self, output_str):
       if(self.log_path):
            file_name = self.log_path + self.log_prefix + "{}.txt".format(self.start_timestamp)

            # apppend to file if it exists, otherwise create it
            try:
                with open(file_name, "a") as f:
                    f.write(output_str + "\n")
            except FileNotFoundError:
                with open(file_name, "w") as f:
                    f.write(output_str + "\n")
                    print('OUTPUT LOG: ', file_name)

##### END OF CLASS #####################################################################

##### jt_stack_str() #######
def jt_stack_str(wholeStack):
    #determin number of levels deep in the stack

    num_functions_deep=0
    stack_str = ">>> "
    stack = []

    #find the top level function in the stack
    for frame in wholeStack:
        func_name = frame.function

        # skip the first function because it is this one
        if num_functions_deep >0 :
            if func_name[0] == "<":
                stack.append("top")
                break;
            else:
                stack.append(func_name)

        num_functions_deep += 1

    # reverse these so the top level function comes out first, followed by 2nd, ...
    stack.reverse()
  #  for item in stack[:-1]:   #iterate through the list but skipping last element (typically log.f() )
    for item in stack[:-1]:   #iterate through the list but skipping last element (typically log.f() )
        stack_str = stack_str + item + "|"

    #print(f"jt debug         num_functions_deep:{num_functions_deep}  stack = {stack_str}")
    return(stack_str)

##### Number of levels deep in the stack () #####
def jt_num_functions_deep(wholeStack):
  
    num_functions_deep=0
    for frame in wholeStack:
        func_name = frame.function

        # skip the first function because it is this one
        if num_functions_deep >0 :
            if func_name[0] == "<":
                break
        num_functions_deep += 1

    return(num_functions_deep)

##### jt_whoami() ######
def jt_whoami(level = 0):

      whole_stack = inspect.stack()

      # the level argument allows this function to ignore a level by setting to 1
      func_name = whole_stack[1 + level].function
      if func_name[0] == "<":
         func_name = "top"
      return(func_name)

##### jt_path_base() function to return base path independent of operating system (Colab, MacOS, Windows)
#   if platform is Google Colab mount google drive

def jt_path_base():

    my_platform = platform.system()
    #print(f"system: {my_platform}")

    #get user
    import getpass as gt
    my_username = gt.getuser()
    #print(f"my_username: {my_username}")

    #Google Colab, technically not correct because python runs on plain Linux also...
    if my_platform == "Linux": 

      from google.colab import drive
      try:
        drive.mount('/gdrive')
      except:
        print("INFO: Drive already mounted")

      my_path = '/gdrive/MyDrive/'

    #MacOS 
    elif my_platform == "Darwin":

        #show files in cloud storage
        path = '/Users/' + my_username + '/Library/CloudStorage'
        files = os.listdir(path)
        print('cloud storage files: ', files)

        # mac_gdrive_path = '/Users/stephentaylor/Library/CloudStorage/GoogleDrive-boiseskibum@gmail.com/'
        # MacOS - retrieve google Drive name portion fo the string
        google_drive = [match for match in files if "GoogleDrive" in match]
        print(f"google drive name: {google_drive}")

        # MacOS google drive directory
        my_path = '/Users/' + my_username + '/My Drive/'    # changed on 7/16/2023   Seems as though google changed?
        if not os.path.isdir(my_path):
            print(f"MacOS path didn't work:  {my_path}")
            my_path = '/Users/' + my_username + '/Library/CloudStorage/' + google_drive[0] + '/My Drive/'
            if not os.path.isdir(my_path):
                print(f"MacOS old style path didn't work either:  {my_path}")
            else:
                print(f"MacOS path:  {my_path}")
        else:
            print(f"MacOS path:  {my_path}")

    #Windows
    elif my_platform == "Windows":

        win_gdrive_path = 'C:/Users/' + my_username + '/My Drive/'
        win_onedrive_path = 'C:/Users/' + my_username + '/OneDrive/'

        my_path = win_gdrive_path 

    return my_path

def jt_path_config():

    my_platform = platform.system()
    #print(f"system: {my_platform}")

    #get user
    import getpass as gt
    my_username = gt.getuser()
    #print(f"my_username: {my_username}")


    if my_platform == "Darwin":

        #show files in cloud storage
        path = '/Users/' + my_username + '/Library/CloudStorage'
        files = os.listdir(path)
        print('cloud storage files: ', files)

        # mac_gdrive_path = '/Users/stephentaylor/Library/CloudStorage/GoogleDrive-boiseskibum@gmail.com/'
        # MacOS - retrieve google Drive name portion fo the string
        google_drive = [match for match in files if "GoogleDrive" in match]
        print(f"google drive name: {google_drive}")

        # MacOS google drive directory
        my_path = '/Users/' + my_username + '/My Drive/'    # changed on 7/16/2023   Seems as though google changed?
        if not os.path.isdir(my_path):
            print(f"MacOS path didn't work:  {my_path}")
            my_path = '/Users/' + my_username + '/Library/CloudStorage/' + google_drive[0] + '/My Drive/'
            if not os.path.isdir(my_path):
                print(f"MacOS old style path didn't work either:  {my_path}")
            else:
                print(f"MacOS path:  {my_path}")
        else:
            print(f"MacOS path:  {my_path}")

    #Windows
    elif my_platform == "Windows":

        win_gdrive_path = 'C:/Users/' + my_username + '/My Drive/'
        win_onedrive_path = 'C:/Users/' + my_username + '/OneDrive/'

        my_path = win_gdrive_path

    return my_path


##### Open any file with a native viewer for the OS
def open_file_in_native_viewer(filepath):

    if os.path.exists(filepath):
        # Make sure the file path is absolute
        absolute_filepath = os.path.abspath(filepath)
        print(f'OS opening file: {absolute_filepath}')
        # Check the operating system
        if sys.platform.startswith("darwin"):
            # macOS
            subprocess.run(["open", absolute_filepath])
        elif sys.platform.startswith("win32"):
            # Windows
            subprocess.run(["start", absolute_filepath], shell=True)
        else:
            print("ERROR Unsupported OS")
    else:
        print(f'open_file_explorer ERROR:   filepath: {filepath} does not exist ')

# opens the finder (macOS) or explorer (windows) to the path input.  Accepts either a filepath or just the path to
# a directory
def open_file_explorer(file_path):

    # Extract the directory part from the file path
    directory = os.path.dirname(file_path)

    # Check if the directory exists
    if os.path.isdir(directory):

        # Make sure the path is absolute
        absolute_path = os.path.abspath(directory)

        if sys.platform.startswith('darwin'):
            # For macOS
            subprocess.run(['open', absolute_path])
        elif sys.platform.startswith('win32'):
            # For Windows
            subprocess.run(['explorer', absolute_path])
    else:
        print(f'open_file_explorer ERROR:   directory: {directory} does not exist ')

#######################################################################################################################
###  Examples
#######################################################################################################################
# function nesting example
def foo1(my_string):
    log = jt_logging()
    log.f("srt foo1()")
    log.print(f'whoami {jt_whoami()}')
    jt_whoami()
    log.print(f"jt in foo1: {my_string}")
    log.debug("debug log entry")
    log.info("info log entry")
    log.warning("warning log entry")

    log.set_logging_level("INFO")
    foo2("abc foo2 testing")

def foo2(my_string):
    log = jt_logging()
    log.f("srt foo2()")
    log.print(f"jt in foo2: {my_string}")
    log.debug("debug log entry")
    log.info("info log entry")
    log.warning("warning log entry")

    log.set_logging_level("WARNING")
    log.warning("warning log entry try 2")
    log.f()

    log.error("error log entry")

    log.set_logging_level("SCREW UP)")

    foo3("def")

def foo3(my_string):
    log = jt_logging()
    log.f("srt foo3()")
    log.print(f"jt in foo3: {my_string}")
    log.print(jt_whoami())

    foo4("xyz")


def foo4(my_string):
    log = jt_logging()
    log.f("srt foo4()")
    my_int = 39
    log.print(f"jt in foo4: {my_string}")
    log.print(f"Here: {jt_whoami()}, {my_int}")

#######################
def example1():
  log = jt_logging()
  log.f("srt example1()")
  log.print("abc")
  log.print("def")

  log.debug("debug log entry")
  log.info("info log entry")
  log.warning("warning log entry")

  foo1("ohmy")


######################
def example2():

  log = jt_logging("srt example2()")

  log.print("my test str")
  print(log.set_logging_level("INFO"))

  # should not print anything
  log.debug("abc def")

  #should print
  log.info("xyz")

  log.set_logging_level("DEBUG")

  #should print
  log.debug("abc def")

###########################
def example_with_logging():
  log = jt_logging()
  log.set_log_file('/gdrive/MyDrive/', 'example_')
  log.f()
  log.print("abc")
  log.print("")

  log.debug("debug log entry")
  log.info("info log entry")
  log.warning("warning log entry")

  foo1("ohmy")

def example_a():
   log.f("srt example_a()")
   log.print("abc")
   foo1("ohmy")


def example_b():
   log.f("srt example_b()")  
   example1()

def example_c(): 
    #example writing to log file
    log.f("srt example_c()")

    from google.colab import drive
    drive.mount('/gdrive')

    example_with_logging()

#debug stack size

def funct_debug():
  print(f'funct_debug - who am I: {jt_whoami()}')
  wholeStack = inspect.stack()

  stack_str = jt_stack_str(wholeStack)
  depth = jt_num_functions_deep(wholeStack)

  print( f'  depth {depth}, stack: {stack_str}')

def jt_funct1():
  print(f'\nfunct1 - who am I: {jt_whoami()}')
  funct_debug()

def jt_funct2():
  print(f'\nfunct2 - who am I: {jt_whoami()}')
  funct_debug()
  jt_funct1()

# essentially the main starts here
#print(f'\ntop - who am I: {jt_whoami()}')

#funct_debug()

#jt_funct1()

#jt_funct2()

import inspect

def func1():
    func2()

def func2():
    func3()

def func3():
    stack = inspect.stack()
    print(f'stack type {type(stack)}')
    funct_name = stack[0].function
    print(f'func {funct_name}')
    for frame in stack:
        if(frame.function[0] == '<'):
            break
        print(frame.function)


#func1()

#Print out whole stack

def more_debug():
    wholeStack = inspect.stack()

    stack = []
    num_functions_deep = 0

    for frame in wholeStack:

        if(frame.function[0] == '<'):
            break
        stack.append(frame.function)
        num_functions_deep += 1

    print (f'\nstack {stack}, {num_functions_deep}')

### Main routines
if __name__ == '__main__':

    log = jt_logging()
    log.msg("srt message")
    log.f("SRT top")
    more_debug()

#example1()

#example_a()