
import os, platform, glob, sys, time, json

# this appends to the path so that files can be found in the different sub directories
sys.path.append('./share')

# retrieve username and platform information
import getpass as gt

my_username = gt.getuser()
my_platform = platform.system()

# appends the path to look for files to the existing path

# mount drive if in google collab()
if my_platform == "Linux":

    from google.colab import drive

    try:
        drive.mount('/gdrive')
    except:
        print("INFO: Drive already mounted")

    # required to import jt_util
    sys.path.append('/gdrive/MyDrive/Colab Notebooks')

import jt_util as util

# set base and application path
path_base = util.jt_path_base()  # this figures out right base path for Colab, MacOS, and Windows

print(f"path_base: {path_base}")

# setup path variables for base and misc
path_app = path_base + 'Force Plate Testing/'
path_data = path_app + 'data/'
path_results = path_app + 'results/'
path_log = path_app + 'log/'
#path_graphs = path_app + 'graphs/'
path_config = path_app + 'config/'
path_db = path_app + 'db/'

